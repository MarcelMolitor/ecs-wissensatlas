
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page(viewport={'width':1400,'height':1200})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(1500)
        await pg.click("#tabs .tab >> text=Nachbarsysteme"); await pg.wait_for_timeout(500)
        print('Sprungleiste:', await pg.eval_on_selector_all('.jumps .qchip','e=>e.map(x=>x.textContent)'))
        c = pg.locator('#n-glp1')
        print('Karte vorhanden:', await c.count())
        t = await c.inner_text()
        print('Zeichen:', len(t))
        print('Belegnummern in Karte:', await c.locator('sup.cite a').count())
        print('Gegenproben:', await c.locator('ol.steps li').count())
        print('Rohmarker:', '[[' in t)
        print('xlinks:', await c.locator('.xlink').count())
        await c.locator('.xlink[data-sub]').click(); await pg.wait_for_timeout(600)
        print('Nach Klick ausgewaehlt:', (await pg.inner_text('#subName')).strip())
        await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(1200)
        await pg.click("#tabs .tab >> text=Nachbarsysteme"); await pg.wait_for_timeout(400)
        await pg.click('.jumps .qchip >> text=GLP-1'); await pg.wait_for_timeout(500)
        print('Sprung sichtbar:', await pg.locator('#n-glp1').is_visible())
        print('Fehler:', errs)
        await b.close()
asyncio.run(main())
