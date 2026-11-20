# -*- coding: utf-8 -*-
"""Prueft die Karte bo-blutwert und die beiden belegten obasis-Felder.

Der Zweck: Die beiden Kernbotenstoffe behaupteten im Feld "Woher man das
weiss" eine Messung am Menschen OHNE Beleg. t/evtyp.py prueft dieses Feld nur
bei Belegstufe g - aea und 2ag stehen auf m und fielen durch das Raster.
Diese Pruefung verlangt den Beleg direkt.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
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

        # --- 1. obasis von aea und 2ag muss Belege tragen
        for sid in ('aea', '2ag'):
            await pg.click('.chip[data-id="%s"]' % sid)
            await pg.wait_for_timeout(450)
            n = await pg.evaluate("""() => {
                const dts = [...document.querySelectorAll('#organInfo dt, dl.kv dt')];
                return document.body.innerHTML.length;
            }""")
            # Das Feld steht im Stoffpanel unter "Woher man das weiss"
            ob = await pg.evaluate("""() => {
                const el = [...document.querySelectorAll('dt')].find(d => /Woher/.test(d.textContent));
                return el ? {text: el.nextElementSibling.textContent,
                             zitate: el.nextElementSibling.querySelectorAll('sup.cite').length} : null;
            }""")
            if not ob:
                probleme.append('%s: Feld "Woher man das weiss" nicht gefunden' % sid)
            else:
                print('  %-4s obasis: %d Belege' % (sid, ob['zitate']))
                if ob['zitate'] < 1:
                    probleme.append('%s: obasis behauptet eine Messung ohne Beleg' % sid)

        # --- 2. Karte bo-blutwert
        await pg.click('#groups button[data-g="0"]')
        await pg.wait_for_timeout(260)
        await pg.click('#tabs button:has-text("Botenstoffe")')
        await pg.wait_for_timeout(460)
        chip = pg.locator('.qchip[data-jump="bo-blutwert"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf bo-blutwert fehlt')
        else:
            await chip.click()
            await pg.wait_for_timeout(650)
        t = await pg.inner_text('#bo-blutwert')
        print('  bo-blutwert:', len(t), 'Zeichen')
        for muss in ['1,35 Nanomol pro Liter', '16 gesunden Menschen', 'Zwei Wege, dasselbe Ergebnis',
                     'höher als Anandamid selbst', 'Zeit bis zum Zentrifugieren', 'in sein Isomer umlagert',
                     'dieselben krankheitsabhängigen Profile', 'Vergleiche sind und keine Werte',
                     'nie ein Zielwert']:
            if muss not in t:
                probleme.append('bo-blutwert, fehlt: %s' % muss)
        # Keine erfundene Mengenangabe ueber die eigene Seite.
        if 'genauso vielen Stellen' in t:
            probleme.append('zurueckgezogene Mengenangabe wieder da')
        # Die Karte darf keinen Normalwert oder Zielwert anbieten.
        for weg in ['Normalbereich', 'Referenzbereich', 'sollte bei', 'Zielwert von']:
            if weg in t:
                probleme.append('bietet doch einen Normalwert an: %s' % weg)

        # --- 3. Querverweise
        n = await pg.locator('#bo-blutwert button.xlink').count()
        print('  Querverweise:', n)
        for i in range(n):
            await pg.click('#groups button[data-g="0"]')
            await pg.wait_for_timeout(240)
            await pg.click('#tabs button:has-text("Botenstoffe")')
            await pg.wait_for_timeout(400)
            kn = pg.locator('#bo-blutwert button.xlink').nth(i)
            beschr = (await kn.inner_text()).strip()
            ziel = await kn.get_attribute('data-card')
            stoff = await kn.get_attribute('data-sub')
            await kn.click()
            await pg.wait_for_timeout(800)
            if ziel:
                da = await pg.evaluate("""(id) => {
                    const c = document.getElementById(id);
                    return c ? c.getBoundingClientRect().height > 0 : 'FEHLT';
                }""", ziel)
                if da != True:
                    probleme.append('Verweis "%s" -> %s tot (%s)' % (beschr, ziel, da))
                else:
                    print('   ok  "%s" -> %s' % (beschr[:30], ziel))
            elif stoff:
                name = (await pg.inner_text('#subName')).replace('#', '').strip()
                print('   ok  "%s" -> Stoff %s' % (beschr[:30], name))
                if not name:
                    probleme.append('Stoffverweis "%s" waehlt nichts aus' % beschr)
            else:
                print('   ok  "%s" -> Reiter' % beschr[:30])

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
