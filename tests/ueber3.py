
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
        pg = await b.new_page(viewport={'width':320,'height':860})
        await pg.goto('file://' + HIER + '/page.html#entzuendung/e-zellen'); await pg.wait_for_timeout(2200)
        out = await pg.evaluate("""() => {
          const a = document.getElementById('e-zellen'), res = [];
          if (!a) return 'keine Karte';
          for (const el of a.querySelectorAll('*')){
            const r = el.getBoundingClientRect();
            if (r.width > 330) res.push({t: el.tagName.toLowerCase(),
              c: (el.getAttribute('class')||''), w: Math.round(r.width), sw: el.scrollWidth,
              style: el.getAttribute('style')||'', txt:(el.textContent||'').trim().slice(0,38)});
          }
          const svg = document.querySelector('#e-ablauf svg');
          return {karte: Math.round(a.getBoundingClientRect().width), breit: res.slice(0,14),
                  svgAttr: svg ? {w: svg.getAttribute('width'), vb: svg.getAttribute('viewBox'), st: svg.getAttribute('style')||'', cls: svg.getAttribute('class')||''} : null};
        }""")
        print(out)
        await b.close()
asyncio.run(main())
