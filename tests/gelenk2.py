
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
        pg = await b.new_page(viewport={'width':1280,'height':1000})
        await pg.goto('file://' + HIER + '/page.html')
        await pg.wait_for_timeout(1500)
        await pg.evaluate("() => { const s=document.querySelector('.tour button:last-of-type, .tour'); if(s) s.remove(); }")
        # FAAH-Hemmer waehlen
        ok = await pg.evaluate("""() => {
          const b=[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='FAAH-Hemmer');
          if(b){b.click();return true;} return false; }""")
        await pg.wait_for_timeout(700)
        # Reiter Koerper
        await pg.evaluate("""() => {
          const b=[...document.querySelectorAll('button')].find(e=>e.textContent.trim()==='Körper');
          if(b)b.click(); }""")
        await pg.wait_for_timeout(1200)
        el = await pg.query_selector('#koerper')
        print('Stoff gewaehlt:', ok)
        if el: await el.screenshot(path=HIER + '/koerper.png')
        info = await pg.evaluate("""() => {
          const out=[];
          document.querySelectorAll('#koerper circle').forEach(c=>{
            const cx=+c.getAttribute('cx'), cy=+c.getAttribute('cy');
            if(cy>430) out.push({cx,cy,r:c.getAttribute('r'),fill:(c.getAttribute('fill')||'').slice(0,18),
                                 st:(c.getAttribute('stroke')||'').slice(0,18)});
          });
          return out; }""")
        print('Kreise unterhalb y=430:', info)
        await b.close()
asyncio.run(main())
