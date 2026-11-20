
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page(viewport={'width':1280,'height':900})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + HIER + '/page.html#stoff/nbx'); await pg.wait_for_timeout(1400)
        print('Name:', await pg.inner_text('#subName'))
        print('Tags:', (await pg.inner_text('#subTags')).replace('\n',' | '))
        print('Schritte:', await pg.locator('#steps li').count())
        print('Status-Laenge:', len(await pg.inner_text('#status')))
        print('rohe Marker im Status:', '[[' in await pg.inner_text('#status'))
        # Organ Blase anklicken
        await pg.locator('#koerper g.organ[data-k="blase"]').evaluate(
            "e => e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")  # Klick wird sonst abgefangen
        await pg.wait_for_timeout(500)
        t = await pg.inner_text('#organInfo')
        print('Blase-Karte:', t.replace('\n',' | ')[:300])
        print('rohe Marker in Organkarte:', '[[' in t)
        # Ueberblickstabelle
        await pg.click('button[data-go="uebersicht"]'); await pg.wait_for_timeout(400)
        rows = await pg.locator('#ovBody tr').count()
        print('Uebersicht-Zeilen:', rows)
        # Zeitleiste
        await pg.evaluate("location.hash='#geschichte'"); await pg.wait_for_timeout(800)
        tl = await pg.locator('#tabpanel .timeline li').all_inner_texts()
        print('Zeitleiste:', len(tl), 'Eintraege, sortiert:', [x.split('\n')[0] for x in tl] == sorted(x.split('\n')[0] for x in tl))
        print('Fehler:', errs)
        await b.close()
asyncio.run(main())
