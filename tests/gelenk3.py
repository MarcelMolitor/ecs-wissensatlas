
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re
from playwright.async_api import async_playwright
EXE = _CHROME
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width':1280,'height':1000})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + HIER + '/page.html#organ/gelenk')
        await pg.wait_for_timeout(2800)
        t = await pg.inner_text('#koerper')
        i = t.find('Gelenke')
        print(t[i:i+1800] if i>=0 else t[-1800:])
        print('\n=== rohe Marker:', re.findall(r'\[\[\d+\]\]', t))
        print('=== Fehler:', errs)
        await b.close()
asyncio.run(main())
