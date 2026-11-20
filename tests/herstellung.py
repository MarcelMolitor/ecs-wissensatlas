# -*- coding: utf-8 -*-
"""Prueft die Herstellungsseite: die belegte Enzym-Tabelle und die zwei neuen
Karten e-herstellung (Reiter Enzyme) und bo-vesikel (Reiter Botenstoffe).

DER EIGENTLICHE ZWECK dieser Pruefung steht in der ersten Pruefschleife: JEDE
Zeile der Enzym-Tabelle muss einen Beleg tragen. Genau das fehlte vorher an
fuenf von acht Zeilen, und t/belege.py hat es nicht gemeldet, weil
Tabellenzeilen kein ev() tragen und damit durch dessen Raster fallen.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'


async def reiter(pg, name):
    await pg.click('#groups button[data-g="0"]')
    await pg.wait_for_timeout(240)
    await pg.click('#tabs button:has-text("%s")' % name)
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

        # --- 1. JEDE Zeile der Enzym-Tabelle braucht einen Beleg
        await reiter(pg, 'Enzyme')
        zeilen = await pg.eval_on_selector_all('#tabpanel table tbody tr', """e => e.map(tr => ({
            enzym: tr.children[0].textContent.trim(),
            zitate: tr.querySelectorAll('sup.cite').length}))""")
        print('  Enzym-Tabelle:', len(zeilen), 'Zeilen')
        if len(zeilen) != 8:
            probleme.append('%d Tabellenzeilen, erwartet 8' % len(zeilen))
        for z in zeilen:
            print('   %-18s %d Belege' % (z['enzym'], z['zitate']))
            if z['zitate'] < 1:
                probleme.append('Tabellenzeile ohne Beleg: %s' % z['enzym'])

        # --- 2. Karte e-herstellung
        t = await pg.inner_text('#e-herstellung')
        for muss in ['85 Prozent', '15 Prozent', 'ABHD6', 'bilden sie weiter Anandamid',
                     'Dieselbe Zielscheibe', 'beschrieben wurde er 2010']:
            if muss not in t:
                probleme.append('e-herstellung, fehlt: %s' % muss)
        if 'seit über fünfzehn Jahren offen' in t:
            probleme.append('zurueckgezogene Behauptung ueber die Literatur wieder da')

        # --- 3. Karte bo-vesikel
        await reiter(pg, 'Botenstoffe')
        chip = pg.locator('.qchip[data-jump="bo-vesikel"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf bo-vesikel fehlt')
        else:
            await chip.click()
            await pg.wait_for_timeout(650)
        v = await pg.inner_text('#bo-vesikel')
        print('  bo-vesikel:', len(v), 'Zeichen')
        for muss in ['2000 Moleküle', 'Anandamid nicht', 'in seine Hülle', 'Zellkultur und Mäusegewebe',
                     'Transportweg ist noch kein Vorrat', 'Hypothese', 'auf Abruf freigesetzt']:
            if muss not in v:
                probleme.append('bo-vesikel, fehlt: %s' % muss)
        # Diese Karte darf den Lehrsatz nicht fuer widerlegt erklaeren.
        for weg in ['widerlegt die', 'falsch war der Satz', 'in jedem Lehrbuch']:
            if weg in v:
                probleme.append('zu starke Formulierung: %s' % weg)
        if 'nicht widerlegt' not in v:
            probleme.append('bo-vesikel: die Einordnung "nicht widerlegt" fehlt')

        # --- 4. Der Verweis in b-chemie
        c = await pg.inner_text('#b-chemie')
        if 'Der Vorrat, den es vielleicht doch gibt' not in c:
            probleme.append('b-chemie verweist nicht auf bo-vesikel')
        # Die Belegstufe dort ist bewusst NICHT gesenkt worden.
        if 'gut belegt' not in c:
            probleme.append('b-chemie: Belegstufe gut belegt verschwunden')

        # --- 5. Alle Querverweise beider Karten anklicken
        for karte, rtr in (('e-herstellung', 'Enzyme'), ('bo-vesikel', 'Botenstoffe')):
            await reiter(pg, rtr)
            n = await pg.locator('#%s button.xlink' % karte).count()
            print('  %s: %d Querverweise' % (karte, n))
            for i in range(n):
                await reiter(pg, rtr)
                kn = pg.locator('#%s button.xlink' % karte).nth(i)
                beschr = (await kn.inner_text()).strip()
                ziel = await kn.get_attribute('data-card')
                await kn.click()
                await pg.wait_for_timeout(800)
                if ziel:
                    da = await pg.evaluate("""(id) => {
                        const c = document.getElementById(id);
                        if (!c) return 'FEHLT';
                        return {sichtbar: c.getBoundingClientRect().height > 0};
                    }""", ziel)
                    if da == 'FEHLT' or not da['sichtbar']:
                        probleme.append('%s: Verweis "%s" -> %s tot' % (karte, beschr, ziel))
                    else:
                        print('   ok  "%s" -> %s' % (beschr[:32], ziel))
                else:
                    print('   ok  "%s" -> Reiter' % beschr[:32])

        for q in ['vorrat', 'mikrovesikel' if False else 'bläschen', 'abhd6']:
            await pg.fill('#findQ', q)
            await pg.wait_for_timeout(520)
            tref = await pg.eval_on_selector_all('#findRes [role=option]', 'e => e.length')
            print('  Suche "%s": %s Treffer' % (q, tref))
            if not tref:
                probleme.append('Suche findet "%s" nicht' % q)

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
