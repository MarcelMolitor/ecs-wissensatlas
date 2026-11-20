
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
        pg = await b.new_page(viewport={'width':320,'height':800})
        await pg.goto('file://' + HIER + '/page.html#entzuendung')
        await pg.wait_for_timeout(2500)
        out = await pg.evaluate("""() => {
          const res = [];
          document.querySelectorAll('#panel-entzuendung *, [id="entzuendung"] *').forEach(e => {
            if (e.scrollWidth > 340 || e.getBoundingClientRect().width > 340) {
              const r = e.getBoundingClientRect();
              res.push({tag:e.tagName, cls:e.className && String(e.className).slice(0,40),
                        id:e.id, sw:e.scrollWidth, w:Math.round(r.width),
                        card:(e.closest('article')||{}).id, txt:(e.textContent||'').slice(0,60)});
            }
          });
          return res.slice(0, 25);
        }""")
        for o in out: print(o)
        if not out:
            # welcher Reiter ist aktiv / wie heisst der Container
            print(await pg.evaluate("() => [...document.querySelectorAll('[role=tabpanel],section,main>div')].map(e=>e.id).slice(0,20)"))
        await b.close()
asyncio.run(main())
