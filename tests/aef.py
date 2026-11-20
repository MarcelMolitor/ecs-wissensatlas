
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page(viewport={'width':1400,'height':1300})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + HIER + '/page.html#stoff/aef'); await pg.wait_for_timeout(2200)
        print('Name:', (await pg.inner_text('#subName')).strip())
        print('Chips gesamt:', await pg.locator('#picker .chip').count())
        for sel,lab in [('#subStatus','Status'),('#subWhat','Was'),('#subBasis','Basis')]:
            if await pg.locator(sel).count():
                t=await pg.inner_text(sel); print(lab+':', len(t), 'Zeichen | Rohmarker:', '[[' in t)
        print('Belegnummern auf Stoffseite:', await pg.locator('sup.cite a').count())
        print('Schritte:', await pg.locator('#subSteps li').count())
        print('Externer Link im Status:', await pg.locator('#subStatus a[href*="businesswire"]').count())
        # Schritte durchklicken (FOCI)
        for k in range(await pg.locator('#subSteps li').count()):
            await pg.locator('#subSteps li').nth(k).click(); await pg.wait_for_timeout(180)
        print('nach Schrittklicks Fehler:', errs)
        # Organ
        await pg.eval_on_selector('#or-brain', "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(300)
        print('Organtext-Belege:', await pg.locator('#organBox sup.cite a').count() if await pg.locator('#organBox').count() else 'n/a')
        # Überblickszeile
        await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(1500)
        row = pg.locator('#ovBody tr[data-id="aef"]')
        print('OV-Zeile:', await row.count(), '|', (await row.inner_text()).replace('\n',' / ') if await row.count() else '')
        print('OV-Zeilen gesamt:', await pg.locator('#ovBody tr').count())
        print('Fehler:', errs)
        await b.close()
asyncio.run(main())
