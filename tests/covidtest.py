
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re
from playwright.async_api import async_playwright
exec(open(HIER + '/run.py').read().split("async def main")[0])  # regenerates page.html
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    for name,vp,theme in [('desk',{'width':1280,'height':900},'light'),('phone',{'width':390,'height':844},'dark')]:
      errs=[]
      pg=await b.new_page(viewport=vp, color_scheme=theme)
      pg.on('pageerror',lambda e:errs.append('ERR:'+str(e)))
      pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)
      await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(600)
      # open Praxis group, then covid tab
      await pg.click('#groups button[data-g="1"]'); await pg.wait_for_timeout(300)
      tabs=await pg.eval_on_selector_all('#tabs button','e=>e.map(x=>x.textContent)')
      await pg.click('#tabs button:has-text("COVID-19")'); await pg.wait_for_timeout(500)
      panel=await pg.inner_html('#tabpanel')
      txt=await pg.inner_text('#tabpanel')
      ov=await pg.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
      cites=len(re.findall(r'class="cite"',panel))
      print(f'[{name}/{theme}] tabs={tabs} overflow={ov} len={len(txt)} cites={cites} leftover={"[[" in panel} rows={panel.count("<tr>")} factors={panel.count("class=\"factor\"")}')
      # citation jump
      await pg.click('#tabpanel .cite a[data-pm="37713293"]'); await pg.wait_for_timeout(700)
      tgt=await pg.evaluate("(()=>{const e=document.getElementById(String.raw`key-37713293`);return e?e.querySelector(`.knum`).textContent:null})()")
      n=await pg.evaluate('document.querySelectorAll("#keyList li").length')
      inf=await pg.evaluate('[...document.querySelectorAll("#keyTopics button")].map(b=>b.textContent).includes("Infektion")')
      print(f'   jump->{tgt} studies={n} infektion-chip={inf} errors={errs}')
      await pg.close()
    await b.close()
asyncio.run(main())
