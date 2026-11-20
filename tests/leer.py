
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
EXE = _CHROME
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width':1280,'height':900})
        await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(1800)
        for w in ['adhs','krankenkasse','multiple sklerose']:
            await pg.fill('#findQ',''); await pg.wait_for_timeout(150)
            await pg.fill('#findQ', w); await pg.wait_for_timeout(450)
            html = await pg.evaluate("() => { const r=document.getElementById('findRes'); return r ? r.innerText.slice(0,260) : 'kein findRes'; }")
            n = await pg.evaluate("() => document.querySelectorAll('#findRes [role=option]').length")
            print('%-20s role=option: %d | Text: %s' % (w, n, html.replace('\n',' | ')[:200]))
        await b.close()
asyncio.run(main())
