
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page()
        await pg.goto('file://' + HIER + '/page.html#studien'); await pg.wait_for_timeout(2000)
        ids = await pg.evaluate("[...document.querySelectorAll('[id^=\"key-\"]')].map(e=>e.id.slice(4))")
        print('gerendert:', len(ids))
        S=open(HIER + '/page.html').read()
        mine = re.findall(r"^ \['?(\d+)'?,\d{4},", S, re.M)
        print('Regex:', len(mine), '| nur gerendert:', sorted(set(ids)-set(mine)), '| nur Regex:', sorted(set(mine)-set(ids)))
        await b.close()
asyncio.run(main())
