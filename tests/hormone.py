# -*- coding: utf-8 -*-
"""Prueft die Sexualhormon-Karte im Reiter Nachbarsysteme.

Wie t/tabak.py und t/gegen.py: ueber die Sprungleiste hingehen, den
GERENDERTEN Text lesen, jeden Querverweis einzeln anklicken.

Die harten Zusicherungen sind die Stellen, an denen die Karte sich selbst
einschraenkt - fallen sie weg, behauptet sie mehr, als die Arbeiten tragen:
 - die Progesteron-Angabe darf NICHT uebernommen werden (p=0,022 wird dort
   als "nicht korreliert" bezeichnet, das passt nicht zusammen)
 - der Gleichlauf darf nicht als Steuerung dargestellt werden
 - der Wechseljahres-Befund muss als Nebenbefund einer Tierstudie kenntlich
   bleiben
 - TNF darf hier nicht stehen: der Satz "bei beiden Geschlechtern erhoeht"
   stammt aus dem Vorabdruck, nicht aus der veroeffentlichten Fassung
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['Eisprung', 'Lutealphase', 'Estradiol', 'LH', 'FSH',
        'Was daraus nicht folgt', 'kein Eingriff', 'Progesteron', '0,022',
        'Nebenbefund in einer Tierstudie', '56 und 65', '46 und 55',
        '88 Menschen', '85 nach Geschlecht und Alter', 'Interleukin 6 und 8',
        'nur noch eine Tendenz', 'ohne Zyklustag nicht lesbar',
        'Hypothese']
# Genau der Satz, der aus dem Vorabdruck stammt und hier nicht stehen darf.
VERBOTEN = ['TNF war bei beiden', 'das Gegenteil anzeigen',
            'einzige Nachbar, der sich innerhalb']


async def zum_reiter(pg):
    await pg.click('#groups button[data-g="0"]')
    await pg.wait_for_timeout(260)
    await pg.click('#tabs button:has-text("Nachbarsysteme")')
    await pg.wait_for_timeout(460)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1600)
        probleme = []

        await zum_reiter(pg)
        chip = pg.locator('.qchip[data-jump="n-hormone"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt (%d)' % await chip.count())
        else:
            if (await chip.inner_text()).strip() != 'Sexualhormone':
                probleme.append('Sprungknopf heisst "%s"' % await chip.inner_text())
            await chip.click()
            await pg.wait_for_timeout(700)
            lage = await pg.evaluate("""() => {
                const c = document.getElementById('n-hormone');
                const r = c.getBoundingClientRect();
                return {top: Math.round(r.top), hoch: Math.round(r.height)};
            }""")
            print('  Karte nach Sprung:', lage)
            if abs(lage['top']) > 400 or lage['hoch'] < 300:
                probleme.append('Sprung landet falsch oder Karte zu klein: %s' % lage)

        txt = await pg.inner_text('#n-hormone')
        print('  Kartentext:', len(txt), 'Zeichen')
        for muss in MUSS:
            if muss not in txt:
                probleme.append('fehlt im Kartentext: %s' % muss)
        for weg in VERBOTEN:
            if weg in txt:
                probleme.append('zurueckgezogene Formulierung wieder da: %s' % weg)
        # Die Karte nennt keine Blutwerte mit Einheit, weil die Arbeit keine nennt.
        if re.search(r'\d+[,.]\d+\s*(nmol|pmol|ng|µg)', txt):
            probleme.append('Blutwert mit erfundener Einheit im Text')

        n = await pg.locator('#n-hormone button.xlink').count()
        print('  Querverweise in der Karte:', n)
        if n != 7:
            probleme.append('%d Querverweise, erwartet 7' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#n-hormone button.xlink').nth(i)
            beschr = (await kn.inner_text()).strip()
            karte = await kn.get_attribute('data-card')
            await kn.click()
            await pg.wait_for_timeout(820)
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
                    print('   ok  "%s" -> %s, top=%s' % (beschr[:32], karte, da['top']))
            else:
                reiter = await pg.evaluate(
                    '() => document.querySelector("#tabs button[aria-selected=true]")?.textContent')
                print('   ok  "%s" -> Reiter %s' % (beschr[:32], reiter))
                if not reiter:
                    probleme.append('Reiterverweis "%s" wechselt nicht' % beschr)

        # --- Der Rueckverweis aus ef-geschlecht muss existieren
        await pg.click('#groups button[data-g="1"]')
        await pg.wait_for_timeout(260)
        await pg.click('#tabs button:has-text("Einflussfaktoren")')
        await pg.wait_for_timeout(460)
        g = await pg.inner_text('#ef-geschlecht')
        if 'Sexualhormone' not in g:
            probleme.append('ef-geschlecht verweist nicht zurueck')
        zurueck = pg.locator('#ef-geschlecht button.xlink[data-card="n-hormone"]')
        if await zurueck.count() != 1:
            probleme.append('Rueckverweis-Knopf fehlt (%d)' % await zurueck.count())

        for q in ['sexualhormone', 'eisprung', 'estradiol']:
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
