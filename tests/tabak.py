# -*- coding: utf-8 -*-
"""Prueft die Rauchstopp-Karte, indem sie wirklich bedient wird.

Der Sprungknopf wird geklickt, der gerenderte Text gelesen (nicht der
Quelltext), jeder Querverweis der Karte angeklickt und nachgesehen, wo man
landet. Dazu die neue Zeile und der neue Absatz in b-muster.

Die beiden harten Zusicherungen am Ende sind Inhaltsregeln dieser Seite:
 - keine Milligramm-Angabe zu CBD (frei kaeufliche Stoffe ohne Mengen)
 - kein unmoegliches Vertrauensintervall aus der Rigotti-Zusammenfassung
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1600)
        probleme = []

        # --- Ueber die Sprungleiste hingelangen, wie ein Mensch es tut
        await pg.click('#groups button[data-g="1"]')
        await pg.wait_for_timeout(300)
        await pg.click('#tabs button:has-text("Medizin")')
        await pg.wait_for_timeout(500)
        chip = pg.locator('.qchip[data-jump="m-tabak"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt (%d)' % await chip.count())
        else:
            if (await chip.inner_text()).strip() != 'Rauchstopp':
                probleme.append('Sprungknopf heisst "%s"' % await chip.inner_text())
            await chip.click()
            await pg.wait_for_timeout(700)
            # Auf Stillstand warten statt auf eine feste Dauer. Am 20.11.2026
            # wurde der Container ersetzt und Chromium sprang von 1194 auf 1243;
            # derselbe Sprung braucht dort mehr als doppelt so lang. Gemessener
            # Verlauf der Kartenoberkante: 9522 -> 2333 -> 661 -> 164 -> 137.
            # Eine feste Wartezeit von 680 ms misst mitten in der Bewegung und
            # meldet einen Seitenfehler, den es nicht gibt. Sechs Tests hingen
            # daran. Dieselbe Lehre wie beim fest eingetragenen Chromium-Pfad:
            # kein Wert, der an eine Umgebung gebunden ist.
            _vorher = None
            for _ in range(40):                      # hoechstens 6 Sekunden
                await pg.wait_for_timeout(150)
                _jetzt = await pg.evaluate('Math.round(window.scrollY)')
                if _jetzt == _vorher:
                    break
                _vorher = _jetzt
            lage = await pg.evaluate("""() => {
                const c = document.getElementById('m-tabak');
                const r = c.getBoundingClientRect();
                return {top: Math.round(r.top), hoch: Math.round(r.height)};
            }""")
            print('  Karte nach Sprung:', lage)
            if abs(lage['top']) > 400 or lage['hoch'] < 300:
                probleme.append('Sprung landet falsch oder Karte zu klein: %s' % lage)

        txt = await pg.inner_text('#m-tabak')
        print('  Kartentext:', len(txt), 'Zeichen')

        # --- Inhaltsregeln
        import re
        mg = re.findall(r'(\d+)\s*mg', txt)
        if mg:
            probleme.append('Mengenangabe im Text: %s mg' % mg)
        if '1,71' in txt or '2,36' in txt:
            probleme.append('fehlerhaftes Vertrauensintervall aus Rigotti uebernommen')
        # Die Surinabant-Zeilen sind nachtraeglich dazugekommen und sie sind eine
        # EINSCHRAENKUNG der eigenen Aussage: Placebo war dort numerisch besser.
        # Faellt der Abschnitt je weg, steht der Nutzennachweis zu gut da.
        for muss in ['1,50', '1567', '39,0', '24 Rauchende', 'NCT06218056', 'Taranabant', '2008', '2011',
                     'drei Jahre nach dem Marktende', 'Surinabant', '810 Rauchende', '25,2',
                     'Januar 2012', 'einen von drei', 'bei einem der drei geprüften Blocker']:
            if muss not in txt:
                probleme.append('fehlt im Kartentext: %s' % muss)

        # --- Jeden Querverweis der Karte anklicken
        n = await pg.locator('#m-tabak button.xlink').count()
        print('  Querverweise in der Karte:', n)
        for i in range(n):
            await pg.click('#groups button[data-g="1"]')
            await pg.wait_for_timeout(240)
            await pg.click('#tabs button:has-text("Medizin")')
            await pg.wait_for_timeout(360)
            kn = pg.locator('#m-tabak button.xlink').nth(i)
            beschr = (await kn.inner_text()).strip()
            ziel = await kn.get_attribute('data-card')
            await kn.click()
            await pg.wait_for_timeout(800)
            if ziel:
                da = await pg.evaluate("""(id) => {
                    const c = document.getElementById(id);
                    if (!c) return 'FEHLT';
                    const r = c.getBoundingClientRect();
                    return {sichtbar: r.height > 0, top: Math.round(r.top)};
                }""", ziel)
                if da == 'FEHLT' or not da['sichtbar']:
                    probleme.append('Verweis "%s" -> %s nicht erreichbar (%s)' % (beschr, ziel, da))
                else:
                    print('   ok  "%s" -> %s, top=%s' % (beschr[:38], ziel, da['top']))
            else:
                reiter = await pg.evaluate(
                    '() => document.querySelector("#tabs button[aria-selected=true]")?.textContent')
                print('   ok  "%s" -> Reiter %s' % (beschr[:38], reiter))
                if not reiter:
                    probleme.append('Reiterverweis "%s" wechselt nicht' % beschr)

        # --- b-muster: neue Zeile und neuer Absatz
        await pg.click('#groups button[data-g="2"]')
        await pg.wait_for_timeout(260)
        await pg.click('#tabs button:has-text("Was man daraus lernen")')
        await pg.wait_for_timeout(500)
        mt = await pg.inner_text('#b-muster')
        if 'Rauchstopp' not in mt:
            probleme.append('b-muster: Zeile Rauchstopp fehlt')
        if 'keine Garantie' not in mt:
            probleme.append('b-muster: neuer Absatz fehlt')
        zeilen = await pg.locator('#b-muster tbody tr').count()
        print('  b-muster Tabellenzeilen:', zeilen)
        if zeilen != 11:
            probleme.append('b-muster hat %d Zeilen, erwartet 11' % zeilen)

        # --- Findet die Suche die Karte?
        await pg.fill('#findQ', 'rauchstopp')
        await pg.wait_for_timeout(500)
        tref = await pg.eval_on_selector_all('#findRes [role=option]', 'e => e.map(x => x.textContent)')
        print('  Suche "rauchstopp":', len(tref), 'Treffer')
        if not tref:
            probleme.append('Suche findet "rauchstopp" nicht')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
