#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Jede Laboreinstellung muss entweder auf ein existierendes Stoffprofil
verlinken oder ausdruecklich sagen, dass es keinen solchen Stoff gibt."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re
from playwright.async_api import async_playwright

async def zeile(pg):
    return await pg.evaluate("""() => {
      const box = document.getElementById('labVerdict');
      const z = [...box.querySelectorAll('p')].find(p => p.textContent.includes('nächster echter Verwandter'));
      if (!z) return null;
      return {txt: z.textContent.trim(),
              subs: [...z.querySelectorAll('button.xlink[data-sub]')].map(b => b.dataset.sub),
              tabs: [...z.querySelectorAll('button.xlink[data-tab]')].map(b => b.dataset.tab)};
    }""")

async def seg(pg, lab, i):
    await pg.locator('.seg[data-lab="%s"] button' % lab).nth(i).click()
    await pg.wait_for_timeout(280)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page(viewport={'width': 1280, 'height': 1200})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + HIER + '/page.html#labor'); await pg.wait_for_timeout(1200)
        # Die Stoff-ids stehen als data-id an den Knoepfen der Stoffauswahl,
        # NICHT als data-pick - das war am 30.10. ein Fehlalarm dieses Tests.
        ids = set(await pg.evaluate("() => [...document.querySelectorAll('#picker [data-id]')].map(e => e.dataset.id)"))
        assert len(ids) > 20, 'Stoff-ids nicht gefunden: %d' % len(ids)
        faelle, fehlt = [], []

        # Abbau bremsen: sel x ziel
        for si, sn in enumerate(['nur FAAH', 'auch andere Enzyme']):
            for zi, zn in enumerate(['nur FAAH', 'FAAH + MAGL']):
                await seg(pg, 'mode', 0); await seg(pg, 'sel', si); await seg(pg, 'ziel', zi)
                faelle.append(('FAAH sel=%s ziel=%s' % (sn, zn), await zeile(pg)))
        # CB2: cb2sel x zns
        for ci, cn in enumerate(['nur CB2', 'auch CB1']):
            for zi, zn in enumerate(['zentral', 'peripher']):
                await seg(pg, 'mode', 1); await seg(pg, 'cb2sel', ci); await seg(pg, 'zns', zi)
                faelle.append(('CB2 %s / %s' % (cn, zn), await zeile(pg)))
        # CB1: vier Wege
        for hi, hn in enumerate(['blockieren', 'peripher', 'Signalbahn', 'daempfen']):
            await seg(pg, 'mode', 2); await seg(pg, 'cb1how', hi)
            faelle.append(('CB1 %s' % hn, await zeile(pg)))

        for name, z in faelle:
            if z is None:
                fehlt.append(name + ': ZEILE FEHLT'); print(name.ljust(28), 'ZEILE FEHLT'); continue
            tote = [s for s in z['subs'] if s not in ids]
            if tote: fehlt.append('%s: tote Stoff-ids %s' % (name, tote))
            # 21.11.2026: Die Pruefung verlangte woertlich "kein eigenes Profil".
            # Die Seite schreibt beim Doppelhemmer "deshalb hat er hier auch kein
            # Profil" - dieselbe Aussage, ein Wort kuerzer. Der Test meldete das
            # seit dem Umschreiben zweimal, gab aber 0 zurueck, und run-all.sh sah
            # es nicht. Beides ist jetzt behoben: hier der Wortlaut, dort der Laeufer.
            if not z['subs'] and 'Keinen' not in z['txt'] \
                    and not re.search(r'kein (eigenes )?Profil', z['txt']):
                fehlt.append('%s: kein Link und keine ausdrueckliche Absage' % name)
            print(name.ljust(28), (z['subs'] or z['tabs'] or ['-']), '|', z['txt'][:78])
        print('\nFaelle:', len(faelle), '| Probleme:', fehlt or 'keine', '| Konsole:', errs or 'keine')
        await b.close()
asyncio.run(main())
