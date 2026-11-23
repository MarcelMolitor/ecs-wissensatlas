# -*- coding: utf-8 -*-
"""Prueft den neuen Querverweis im Tourette-Satz des MAGL-Hemmers.

Er steht im Statustext des Stoffes, also NICHT in #tabpanel - deshalb faengt
audit2.py ihn nicht. Hier wird er wirklich angeklickt.
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
        await pg.wait_for_timeout(1500)
        probleme = []
        # MAGL-Hemmer waehlen
        await pg.click('.chip[data-id="magl"]')
        await pg.wait_for_timeout(500)
        txt = await pg.inner_text('#status')
        # 23.11.2026 nachgezogen. Dieser Test hielt den alten Wortlaut fest:
        # 'Ergebnisbericht im Register' und den Stempel '31.10.2026'. Beides
        # stimmte nicht mehr - die Seite sagte damals, zu NCT03625453 gebe es
        # "weder eine Veroeffentlichung noch einen Ergebnisbericht". Die
        # Veroeffentlichung gibt es seit 2021 (Mueller-Vahl u. a., Mov Disord),
        # und ihr Ergebnis fiel zugunsten von Placebo aus. Der Test hielt also
        # eine falsche Aussage fest - wie schon fuenfmal zuvor an anderer Stelle.
        #
        # Darum jetzt zwei Sorten Pruefung:
        for muss in ['im Januar 2020',          # die Studie selbst
                     'kein Ergebnisbericht',    # was im Register fehlt
                     'zugunsten von Placebo',   # wie sie ausgegangen ist
                     'Pflichtmeldung']:         # warum beides zusammen zaehlt
            if muss not in txt:
                probleme.append('Satzteil fehlt: ' + muss)
        # ... und das Datum NICHT woertlich, sondern als Form. Ein Stempel muss
        # da sein; welcher, entscheidet der Tag, an dem jemand nachgesehen hat.
        import re as _re
        if not _re.search(r'abgefragt am \d{1,2}\.\d{1,2}\.20\d\d', txt):
            probleme.append('kein Datumsstempel am Registerbefund')
        # Die Seite darf die Studie nicht wieder als unveroeffentlicht fuehren.
        for schlecht in ['weder eine Veröffentlichung', 'nie veröffentlicht',
                         'keine Veröffentlichung']:
            if schlecht in txt:
                probleme.append('gilt wieder als unveröffentlicht: ' + schlecht)
        kn = pg.locator('#status button[data-card="b-quellen"]')
        if await kn.count() != 1:
            probleme.append('Knopf nicht gefunden: %d' % await kn.count())
        else:
            await kn.click()
            # Auf Stillstand warten statt auf eine feste Dauer (20.11.2026,
            # Chromium 1194 -> 1243: weiches Scrollen braucht rund 1,2 s).
            # Dieser Test fiel bei meiner ersten Suche durch, weil ich nach
            # dem Klickziel gesucht hatte (qchip, data-jump, xlink) statt
            # nach dem Pruefmuster. Er klickt einen Statusleisten-Knopf.
            # Richtig ist die Suche nach der Schwellenpruefung auf eine Lage.
            _v = None
            for _ in range(40):
                await pg.wait_for_timeout(150)
                _j = await pg.evaluate('Math.round(window.scrollY)')
                if _j == _v:
                    break
                _v = _j
            akt = await pg.evaluate("""() => {
                const c = document.getElementById('b-quellen');
                if (!c) return 'KARTE FEHLT';
                const r = c.getBoundingClientRect();
                return {sichtbar: r.height > 0, top: Math.round(r.top),
                        reiter: document.querySelector('.st-tab[aria-selected=true]')?.textContent || ''};
            }""")
            print('  nach Klick:', akt)
            if akt == 'KARTE FEHLT' or not akt['sichtbar']:
                probleme.append('Karte b-quellen nach Klick nicht sichtbar: %s' % akt)
            elif abs(akt['top']) > 400:
                probleme.append('Karte nicht im Blick, top=%s' % akt['top'])
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)

asyncio.run(main())
