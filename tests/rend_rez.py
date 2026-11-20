
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
        pg = await b.new_page(viewport={'width':1280,'height':900})
        errs=[]; pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.on('pageerror', lambda e: errs.append('PAGEERROR '+str(e)))
        await pg.goto('file://' + HIER + '/page.html#rezeptoren/r-weitere')
        await pg.wait_for_timeout(2500)
        t = await pg.inner_text('#r-weitere')
        print(t)
        print('\n=== rohe Marker:', re.findall(r'\[\[\d+\]\]', t))
        print('=== gerade Zeichen:', [c for c in '"\'' if c in t])
        print('=== Bindestrich-Arten:', {d: t.count(d) for d in ['-', '–', '—']})
        print('=== Konsolenfehler:', errs)
        # Querverweise klickbar?
        n = await pg.eval_on_selector_all('#r-weitere .xlink', 'els => els.map(e => e.textContent)')
        print('=== Querverweise:', n)
        await b.close()
asyncio.run(main())
