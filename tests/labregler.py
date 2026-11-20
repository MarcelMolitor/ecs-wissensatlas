#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prueft die Behauptung, die seit 30.10. im Wirkstoff-Labor steht:
Bindung und Wirkstaerke aendern Animation und Erklaerung, aber NICHT die
Einschaetzung und nicht die Huerden. Wenn das irgendwann nicht mehr stimmt,
muss entweder der Satz weg oder der Code zurueck."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright

URL = 'file://' + HIER + '/page.html'


async def zustand(pg):
    kopf = pg.locator('#labVerdict .fy-h')
    return {
        'stufe-text': ((await kopf.first.inner_text()).strip() if await kopf.count() else '(keine)'),
        'stufe-farbe': ((await kopf.first.get_attribute('style')) or '' if await kopf.count() else ''),
        'huerden': (await pg.inner_text('#labRun')).strip(),
    }


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page(viewport={'width': 1280, 'height': 1200})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append(str(e)))
        await pg.goto(URL + '#labor')
        await pg.wait_for_timeout(1200)

        moden = [b_.strip() for b_ in await pg.locator('.seg[data-lab="mode"] button').all_inner_texts()]
        abw, geprueft = [], 0
        for mi, mname in enumerate(moden):
            await pg.locator('.seg[data-lab="mode"] button').nth(mi).click()
            await pg.wait_for_timeout(500)
            anwendungen = await pg.locator('#labUse option').all()
            werte = [await o.get_attribute('value') for o in anwendungen]
            for w in werte:
                await pg.select_option('#labUse', w)
                await pg.wait_for_timeout(350)
                basis = await zustand(pg)
                # Wirkstaerke durchfahren
                for s in ['0', '1', '2']:
                    await pg.eval_on_selector('#labStr', """(el, v) => {
                        el.value = v; el.dispatchEvent(new Event('input', {bubbles:true}));
                    }""", s)
                    await pg.wait_for_timeout(300)
                    z = await zustand(pg)
                    geprueft += 1
                    for k in z:
                        if z[k] != basis[k]:
                            abw.append('%s/%s Wirkstaerke=%s aendert %s' % (mname, w, s, k))
                # Bindung umschalten, falls in diesem Modus vorhanden
                knoepfe = pg.locator('.seg[data-lab="bind"] button')
                if await knoepfe.count():
                    for bi in range(await knoepfe.count()):
                        await knoepfe.nth(bi).click()
                        await pg.wait_for_timeout(300)
                        z = await zustand(pg)
                        geprueft += 1
                        for k in z:
                            if z[k] != basis[k]:
                                abw.append('%s/%s Bindung#%d aendert %s' % (mname, w, bi, k))
        print('Einstellungen geprueft:', geprueft)
        print('Abweichungen:', 'keine' if not abw else '')
        for a in sorted(set(abw)):
            print('   ', a)
        print('Fehler:', fehler)
        await b.close()
        sys.exit(1 if (abw or fehler) else 0)

asyncio.run(main())
