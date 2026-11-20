# -*- coding: utf-8 -*-
"""Prueft die Karte r-natrium im Reiter Rezeptoren.

Der Kern dieser Pruefung ist, dass die Karte ihre eigene Geschichte NICHT
schliesst: Sie nennt zwei Mechanismuskandidaten fuer denselben zugelassenen
Nutzen und sagt, dass keiner am Menschen gezeigt ist. Die Verbotsliste unten
sind Formulierungen, die daraus eine fertige Erklaerung machen wuerden.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['Ein Natriumkanal ist kein Rezeptor', 'bakteriellen Kanal', 'fehlerhaften Ströme',
        'Lamotrigin und Lacosamid', 'Zwei Mechanismen, ein zugelassenes Medikament',
        'GPR55', 'Tierversuch mit Gegenprobe', 'Drei verschiedene Kanäle in drei Arbeiten',
        '182 Menschen', 'Alter beim ersten Anfall', 'Gemessen hat sie niemand', 'nicht untersucht']
VERBOTEN = ['CBD wirkt über den Natriumkanal', 'damit ist geklärt', 'erklärt die Wirkung',
            'der Mechanismus ist', 'weil es Natriumkanäle blockiert, hilft']


async def zum_reiter(pg):
    await pg.click('#groups button[data-g="0"]')
    await pg.wait_for_timeout(240)
    await pg.click('#tabs button:has-text("Rezeptoren")')
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
        chip = pg.locator('.qchip[data-jump="r-natrium"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt')
        else:
            if (await chip.inner_text()).strip() != 'Der Natriumkanal':
                probleme.append('Sprungknopf heisst "%s"' % await chip.inner_text())
            await chip.click()
            await pg.wait_for_timeout(680)
            lage = await pg.evaluate("""() => {
                const r = document.getElementById('r-natrium').getBoundingClientRect();
                return {top: Math.round(r.top), hoch: Math.round(r.height)};
            }""")
            print('  Karte nach Sprung:', lage)
            if abs(lage['top']) > 400 or lage['hoch'] < 300:
                probleme.append('Sprung landet falsch: %s' % lage)

        t = await pg.inner_text('#r-natrium')
        print('  Kartentext:', len(t), 'Zeichen')
        for muss in MUSS:
            if muss not in t:
                probleme.append('fehlt: %s' % muss)
        for weg in VERBOTEN:
            if weg in t:
                probleme.append('schliesst die Geschichte: %s' % weg)
        # Die drei Belegstufen der Karte muessen alle da sein.
        for stufe in ['gut belegt', 'teils belegt', 'nicht untersucht']:
            if stufe not in t:
                probleme.append('Belegstufe fehlt: %s' % stufe)

        n = await pg.locator('#r-natrium button.xlink').count()
        print('  Querverweise:', n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#r-natrium button.xlink').nth(i)
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
                if da is not True:
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

        for q in ['natriumkanal', 'lamotrigin', 'nav1']:
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
