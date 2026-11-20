
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page(viewport={'width':1280,'height':1600})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + HIER + '/page.html#stoff/nbx'); await pg.wait_for_timeout(1200)
        for k in ['blase','spinal','brain']:
            await pg.eval_on_selector('#or-'+k, "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(350)
            t = await pg.inner_text('#organInfo')
            print('==', k, '| roh:', '[[' in t); print('   ', t.replace('\n',' | ')[:260])
        await pg.click('button[data-go="uebersicht"]'); await pg.wait_for_timeout(400)
        print('Uebersicht-Zeilen:', await pg.locator('#ovBody tr').count())
        print('Nabiximols in Tabelle:', await pg.locator('#ovBody tr', has_text='Nabiximols').count())
        await pg.evaluate("location.hash='#geschichte'"); await pg.wait_for_timeout(900)
        tl = await pg.locator('#tabpanel .timeline li').all_inner_texts()
        yrs=[x.split('\n')[0] for x in tl]
        print('Zeitleiste:', len(tl), 'sortiert:', yrs==sorted(yrs))
        await pg.evaluate("location.hash='#anwendung'"); await pg.wait_for_timeout(700)
        print('Dexanabinol in Medizin:', await pg.locator('#tabpanel tr', has_text='Dexanabinol').count())
        print('Taranabant in Medizin:', await pg.locator('#tabpanel tr', has_text='Taranabant').count())
        print('Fehler:', errs)
        await b.close()
asyncio.run(main())
