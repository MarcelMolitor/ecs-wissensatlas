
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
TERMS=['Golfkrieg','Oleoylethanolamid','PEA-LUT','Post-COVID','ME/CFS','Fatigue','Mangel-Hypothese','Versace']
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    pg=await b.new_page(viewport={'width':1280,'height':900})
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(800)
    for t in TERMS:
      await pg.fill('#findQ', t); await pg.wait_for_timeout(420)
      hits=await pg.evaluate("""() => {
        const r=document.getElementById('findRes');
        if (r.hidden) return null;
        return [...r.querySelectorAll('button')].slice(0,3).map(b=>({
          t:(b.querySelector('.ft')?.textContent||'').trim(),
          k:(b.querySelector('.fk')?.textContent||'').trim()}));
      }""")
      print(f'{t:20s} ->', hits if hits else 'KEIN TREFFER')
    await pg.fill('#findQ',''); await pg.wait_for_timeout(200)
    await b.close()
asyncio.run(main())
