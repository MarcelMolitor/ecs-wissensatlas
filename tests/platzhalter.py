# -*- coding: utf-8 -*-
"""Kein unersetzter Platzhalter darf dem Leser angezeigt werden.

WARUM ES DIESEN TEST GIBT: Am 27.11.2026 stand in einer neuen Karte mitten im
Fliesstext "[[28861483]]" - die rohe Quellennummer statt eines Verweises. Die
Seite wandelt [[pmid]] nur dort um, wo es durch cite() laeuft; in statischem
Karten-HTML bleibt es stehen, wie es ist.

Mein eigener Patch hatte das NICHT gefunden, weil er im QUELLTEXT geprueft
hatte, ob "[[28861483]]" vorkommt - und das tat es ja, genau darin bestand der
Fehler. Die Pruefung bestaetigte den Fehler, statt ihn zu finden.

Das ist an diesem Tag der vierte Fall derselben Sorte: im Quelltext gemessen,
was man in der Darstellung haette messen muessen. Darum dieser Test, und zwar
ausdruecklich ueber den GERENDERTEN Text aller Reiter.

Geprueft wird auf:
  [[...]]   nicht umgewandelte Quellennummer
  ${...}    nicht ausgewertete Vorlage
  undefined / NaN   ein ausgewerteter Ausdruck, der ins Leere lief
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None
import asyncio
import re
import sys
from playwright.async_api import async_playwright

SEITE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'
# Ein nackter Pfad ist fuer den Browser keine Adresse - die Suite reicht aber
# genau das herein.
if not re.match(r'^[a-z]+://', SEITE):
    SEITE = 'file://' + _os.path.abspath(SEITE)

MUSTER = [
    (re.compile(r'\[\[[^\]\n]{1,40}\]\]'), 'rohe Quellennummer'),
    (re.compile(r'\$\{[^}\n]{0,60}\}'), 'nicht ausgewertete Vorlage'),
    (re.compile(r'\bundefined\b'), 'undefined'),
    (re.compile(r'\bNaN\b'), 'NaN'),
]


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1000})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1500)
        probleme = []
        reiter = 0
        gruppen = await pg.eval_on_selector_all('#groups button[data-g]', 'e => e.length')
        for g in range(gruppen):
            await pg.click('#groups button[data-g="%d"]' % g)
            await pg.wait_for_timeout(250)
            n = await pg.eval_on_selector_all('#tabs button.tab', 'e => e.length')
            for k in range(n):
                await pg.click('#tabs button.tab >> nth=%d' % k)
                await pg.wait_for_timeout(260)
                reiter += 1
                name = await pg.eval_on_selector(
                    '#tabs button.tab >> nth=%d' % k, 'e => e.textContent.trim()')
                txt = await pg.inner_text('#tabpanel')
                for mus, was in MUSTER:
                    for t in mus.findall(txt)[:3]:
                        probleme.append('[%s] %s: %s' % (name, was, t))
        # Auch der Statustext der Stoffe laeuft durch dieselbe Umwandlung.
        chips = await pg.eval_on_selector_all('.chip[data-id]', 'e => e.map(x => x.dataset.id)')
        for cid in chips:
            await pg.click('.chip[data-id="%s"]' % cid)
            await pg.wait_for_timeout(160)
            txt = await pg.inner_text('#status')
            for mus, was in MUSTER:
                for t in mus.findall(txt)[:2]:
                    probleme.append('[Stoff %s] %s: %s' % (cid, was, t))
        print('Reiter geprüft: %d | Stoffe geprüft: %d' % (reiter, len(chips)))
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)

asyncio.run(main())
