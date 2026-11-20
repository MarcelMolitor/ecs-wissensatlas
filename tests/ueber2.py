
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
        await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(900)
        groups = await pg.evaluate("document.querySelectorAll('#groups button').length")
        for g in range(groups):
            await pg.click(f'#groups button[data-g="{g}"]'); await pg.wait_for_timeout(180)
            n = await pg.evaluate("document.querySelectorAll('#tabs button').length")
            for i in range(n):
                t = pg.locator('#tabs button').nth(i); lbl = await t.inner_text()
                if lbl.strip() != 'Entzündung': continue
                await t.click(); await pg.wait_for_timeout(500)
                out = await pg.evaluate("""() => {
                  const vw = document.documentElement.clientWidth, res = [];
                  for (const el of document.querySelectorAll('#tabpanel *')){
                    const r = el.getBoundingClientRect();
                    if (r.right > vw+1 && r.width > 0)
                      res.push({t: el.tagName.toLowerCase(), c: String(el.className||'').slice(0,34),
                                left: Math.round(r.left), w: Math.round(r.width),
                                card: (el.closest('article')||{}).id || '',
                                parent: el.parentElement.tagName.toLowerCase()+'.'+String(el.parentElement.className||'').slice(0,24),
                                txt: (el.textContent||'').trim().slice(0,44)});
                  }
                  return res.slice(0, 18);
                }""")
                for o in out: print(o)
                print('ANZAHL', len(out))
                await b.close(); return
asyncio.run(main())
