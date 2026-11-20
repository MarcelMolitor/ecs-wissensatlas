# -*- coding: utf-8 -*-
"""Prueft die Karte m-falcarinol im Reiter Medizin.

Die VERBOTSLISTE ist der Kern: Diese Karte handelt von einem Stoff in
Alltagsgemuese, und genau daraus laesst sich leicht eine Gesundheitsaussage
machen, die die Arbeit nicht traegt - in beide Richtungen. Weder "Moehren
wirken auf das Endocannabinoid-System" noch "Moehren sind gefaehrlich".
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['Falcarinol', 'Möhren, Petersilie, Sellerie und Ginseng', 'verklebt es dauerhaft',
        'binden umkehrbar', 'Gegenprobe – und die ist hier gelungen', 'IL-8 und CCL2',
        'abhängig von CB1', 'Dasselbe tat Rimonabant', 'sagt nicht, an wem der Hauttest',
        'Mensch und Tier', 'macht aus Gemüse kein Medikament und keine Gefahr',
        'Falcarinol-Dermatitis', 'Die Autoren schließen daraus']
VERBOTEN = ['Möhrenerntenden', 'Möhren wirken auf', 'Möhren sind gefährlich',
            'Anandamid wirkt dort also eher allergiehemmend', 'sollte man meiden',
            'Möhrenessen ändert']


async def zum_reiter(pg):
    await pg.click('#groups button[data-g="1"]')
    await pg.wait_for_timeout(250)
    await pg.click('#tabs button:has-text("Medizin")')
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
        chip = pg.locator('.qchip[data-jump="m-falcarinol"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt')
        else:
            await chip.click()
            await pg.wait_for_timeout(680)
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
                const r = document.getElementById('m-falcarinol').getBoundingClientRect();
                return {top: Math.round(r.top), hoch: Math.round(r.height)};
            }""")
            print('  Karte nach Sprung:', lage)
            if abs(lage['top']) > 400 or lage['hoch'] < 280:
                probleme.append('Sprung landet falsch: %s' % lage)

        t = await pg.inner_text('#m-falcarinol')
        print('  Kartentext:', len(t), 'Zeichen')
        for muss in MUSS:
            if muss not in t:
                probleme.append('fehlt: %s' % muss)
        for weg in VERBOTEN:
            if weg in t:
                probleme.append('Formulierung, die die Arbeit nicht traegt: %s' % weg)
        # Drei verschiedene Belegstufen, die dritte bewusst niedriger.
        for stufe in ['teils belegt', 'schwach belegt']:
            if stufe not in t:
                probleme.append('Belegstufe fehlt: %s' % stufe)
        # Keine Mengenangabe zu einem Lebensmittel.
        import re
        if re.search(r'\d+\s*(mg|g|Gramm|Möhren am Tag)', t):
            probleme.append('Mengenangabe zu einem Lebensmittel im Text')

        n = await pg.locator('#m-falcarinol button.xlink').count()
        print('  Querverweise:', n)
        if n != 6:
            probleme.append('%d Querverweise, erwartet 6' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#m-falcarinol button.xlink').nth(i)
            beschr = (await kn.inner_text()).strip()
            ziel = await kn.get_attribute('data-card')
            stoff = await kn.get_attribute('data-sub')
            await kn.click()
            await pg.wait_for_timeout(820)
            if ziel:
                da = await pg.evaluate("""(id) => {
                    const c = document.getElementById(id);
                    return c ? c.getBoundingClientRect().height > 0 : 'FEHLT';
                }""", ziel)
                if da is not True:
                    probleme.append('Verweis "%s" -> %s tot (%s)' % (beschr, ziel, da))
                else:
                    print('   ok  "%s" -> %s' % (beschr[:32], ziel))
            elif stoff:
                name = (await pg.inner_text('#subName')).replace('#', '').strip()
                print('   ok  "%s" -> Stoff %s' % (beschr[:32], name))
                if not name:
                    probleme.append('Stoffverweis "%s" waehlt nichts aus' % beschr)

        # Der Rueckverweis aus m-pflanzen muss da sein: dort scheiterte die
        # Gegenprobe, hier gelang sie - die beiden Karten gehoeren zusammen.
        await zum_reiter(pg)
        pf = await pg.inner_text('#m-pflanzen')
        if 'Stoff aus der Möhre' not in pf:
            probleme.append('m-pflanzen verweist nicht auf m-falcarinol')

        for q in ['falcarinol', 'möhre', 'sellerie']:
            await pg.fill('#findQ', q)
            await pg.wait_for_timeout(520)
            n2 = await pg.eval_on_selector_all('#findRes [role=option]', 'e => e.length')
            print('  Suche "%s": %s Treffer' % (q, n2))
            if not n2:
                probleme.append('Suche findet "%s" nicht' % q)

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
