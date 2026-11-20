
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
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for tab, ziel in [('rezeptoren','r-weitere'), ('botenstoffe','bo-noladin')]:
            await pg.goto('file://' + HIER + '/page.html#'+tab); await pg.wait_for_timeout(1800)
            chips = await pg.evaluate("() => [...document.querySelectorAll('#tabpanel .jumps .qchip')].map(e=>e.textContent)")
            print(tab, 'Chips:', chips)
            if chips:
                await pg.click('#tabpanel .jumps .qchip[data-jump="%s"]' % ziel)
                await pg.wait_for_timeout(700)
                # Auf Stillstand warten statt auf eine feste Dauer (20.11.2026,
                # Chromium 1194 -> 1243: weiches Scrollen braucht dort rund 1,2 s).
                _v = None
                for _ in range(40):
                    await pg.wait_for_timeout(150)
                    _j = await pg.evaluate('Math.round(window.scrollY)')
                    if _j == _v:
                        break
                    _v = _j
                y = await pg.evaluate("(id) => { const e=document.getElementById(id); return e ? Math.round(e.getBoundingClientRect().top) : null; }", ziel)
                print('   Sprung zu', ziel, '-> top =', y)
        print('Fehler:', errs)
        await b.close()
asyncio.run(main())
