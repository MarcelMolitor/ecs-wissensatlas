
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
        for w in (320, 1280):
            pg = await b.new_page(viewport={'width':w,'height':900})
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + HIER + '/page.html#entzuendung/e-zellen')
            await pg.wait_for_timeout(2200)
            r = await pg.evaluate("""() => {
              const t = document.querySelector('.cmp-tab'), wrap = t && t.parentElement;
              const svg = document.querySelector('#e-ablauf svg'), sw = svg && svg.parentElement;
              const card = document.getElementById('e-zellen');
              return {
                karte: Math.round(card.getBoundingClientRect().width),
                hNorm: Math.round(card.querySelector('h3').getBoundingClientRect().width),
                tabWrap: wrap ? Math.round(wrap.getBoundingClientRect().width) : null,
                tabInner: t ? t.scrollWidth : null,
                tabScroll: wrap ? wrap.scrollWidth > wrap.clientWidth : null,
                svgWrap: sw ? Math.round(sw.getBoundingClientRect().width) : null,
                svgBreit: svg ? Math.round(svg.getBoundingClientRect().width) : null,
                svgScroll: sw ? sw.scrollWidth > sw.clientWidth : null,
                seitenUeberlauf: document.documentElement.scrollWidth - document.documentElement.clientWidth
              };
            }""")
            print(w, r, 'Fehler:', errs)
            await pg.close()
        await b.close()
asyncio.run(main())
