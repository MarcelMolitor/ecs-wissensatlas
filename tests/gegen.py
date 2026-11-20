# -*- coding: utf-8 -*-
"""Prueft die Gegenmittel-Karte, indem sie bedient wird.

Wie t/tabak.py: ueber die Sprungleiste hingehen, den GERENDERTEN Text lesen,
jeden Querverweis einzeln anklicken und nachsehen, wo man landet. Zwei
Verweise fuehren diesmal aus dem Reiter heraus (Lebensphasen l-kind und der
Stoff Rimonabant), das ist der Grund fuer die drei Faelle unten.

Drei harte Zusicherungen am Ende sind Inhaltsregeln dieser Karte:
 - keine Milligramm-Angabe. Selonabant ist nicht erhaeltlich, die Mengen
   duerften stehen - sie tragen aber nichts bei und die Karte handelt von
   einem Notfall.
 - der Satz ueber die fehlenden Stimmungsveraenderungen muss drinstehen, denn
   er ist der eigentliche Inhalt der Karte.
 - die Grenze muss drinstehen: niemand hat den Stoff je einem vergifteten
   Menschen gegeben.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['Selonabant', '154', '82,8', '30,6', 'NCT07211607', 'Mai 2026',
        '40 gesunden Menschen', 'keine klinisch bedeutsamen Stimmungsveränderungen',
        'Niemand hat Selonabant je einem vergifteten Menschen gegeben',
        'drei Jahre', 'genau zwei eingetragene Studien']


async def zum_reiter(pg):
    await pg.click('#groups button[data-g="1"]')
    await pg.wait_for_timeout(260)
    await pg.click('#tabs button:has-text("Medizin")')
    await pg.wait_for_timeout(420)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1600)
        probleme = []

        # --- Ueber die Sprungleiste hingelangen
        await zum_reiter(pg)
        chip = pg.locator('.qchip[data-jump="m-gegen"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt (%d)' % await chip.count())
        else:
            if (await chip.inner_text()).strip() != 'Gegenmittel':
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
                const c = document.getElementById('m-gegen');
                const r = c.getBoundingClientRect();
                return {top: Math.round(r.top), hoch: Math.round(r.height)};
            }""")
            print('  Karte nach Sprung:', lage)
            if abs(lage['top']) > 400 or lage['hoch'] < 300:
                probleme.append('Sprung landet falsch oder Karte zu klein: %s' % lage)

        txt = await pg.inner_text('#m-gegen')
        print('  Kartentext:', len(txt), 'Zeichen')

        # --- Inhaltsregeln
        mg = re.findall(r'(\d+)\s*mg', txt)
        if mg:
            probleme.append('Mengenangabe im Text: %s mg' % mg)
        for muss in MUSS:
            if muss not in txt:
                probleme.append('fehlt im Kartentext: %s' % muss)

        # --- Jeden Querverweis einzeln anklicken
        n = await pg.locator('#m-gegen button.xlink').count()
        print('  Querverweise in der Karte:', n)
        if n != 5:
            probleme.append('%d Querverweise, erwartet 5' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#m-gegen button.xlink').nth(i)
            beschr = (await kn.inner_text()).strip()
            karte = await kn.get_attribute('data-card')
            stoff = await kn.get_attribute('data-sub')
            await kn.click()
            await pg.wait_for_timeout(850)
            if karte:
                da = await pg.evaluate("""(id) => {
                    const c = document.getElementById(id);
                    if (!c) return 'FEHLT';
                    const r = c.getBoundingClientRect();
                    return {sichtbar: r.height > 0, top: Math.round(r.top)};
                }""", karte)
                if da == 'FEHLT' or not da['sichtbar']:
                    probleme.append('Verweis "%s" -> %s nicht erreichbar (%s)' % (beschr, karte, da))
                else:
                    print('   ok  "%s" -> Karte %s, top=%s' % (beschr[:34], karte, da['top']))
            elif stoff:
                name = (await pg.inner_text('#subName')).replace('#', '').strip()
                print('   ok  "%s" -> Stoff %s' % (beschr[:34], name))
                if not name:
                    probleme.append('Stoffverwies "%s" waehlt nichts aus' % beschr)
            else:
                reiter = await pg.evaluate(
                    '() => document.querySelector("#tabs button[aria-selected=true]")?.textContent')
                print('   ok  "%s" -> Reiter %s' % (beschr[:34], reiter))
                if not reiter:
                    probleme.append('Reiterverweis "%s" wechselt nicht' % beschr)

        # --- Findet die Suche die Karte und den Stoffnamen?
        for q in ['gegenmittel', 'selonabant']:
            await pg.fill('#findQ', q)
            await pg.wait_for_timeout(520)
            tref = await pg.eval_on_selector_all('#findRes [role=option]', 'e => e.map(x => x.textContent)')
            print('  Suche "%s": %d Treffer' % (q, len(tref)))
            if not tref:
                probleme.append('Suche findet "%s" nicht' % q)

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
