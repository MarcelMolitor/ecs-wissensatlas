
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re
from playwright.async_api import async_playwright
exec(open(HIER + '/run.py').read().split("async def main")[0])
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    for name,vp,th in [('desk',{'width':1280,'height':900},'light'),('phone',{'width':390,'height':844},'dark')]:
      errs=[]
      pg=await b.new_page(viewport=vp,color_scheme=th)
      pg.on('pageerror',lambda e:errs.append('ERR:'+str(e)))
      pg.on('console',lambda m:errs.append('C:'+m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text else None)
      await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(700)
      print(f'--- {name}/{th} ---')
      # index size
      await pg.fill('#findQ','MAGL'); await pg.wait_for_timeout(400)
      n=await pg.evaluate('document.querySelectorAll("#findRes button[data-i]").length'); hits=await pg.eval_on_selector_all('#findRes button[data-i] .ft','e=>e.map(x=>x.textContent.slice(0,46))')
      print(' MAGL results=',n); [print('   ',h) for h in hits[:4]]
      # click first result
      await pg.click('#findRes button[data-i="0"]'); await pg.wait_for_timeout(900)
      print(' after click: hash=',await pg.evaluate('location.hash'),'flash=',await pg.evaluate('document.querySelectorAll(".flash").length'))
      for q,exp in [('Dravet','tab/study'),('Lunge','organ'),('Hippocampus','region'),('Anandamid','sub'),('Zytokinsturm','tab')]:
        await pg.fill('#findQ',q); await pg.wait_for_timeout(350)
        hs=await pg.eval_on_selector_all('#findRes button[data-i]','e=>e.map(x=>x.querySelector(".fk").textContent.split(" ")[0])')
        print(f'  "{q}": {len(hs)} -> {hs[:3]}')
      # keyboard
      await pg.fill('#findQ','CB2'); await pg.wait_for_timeout(350)
      await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('ArrowDown'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(800)
      print(' kbd ok, hash=',await pg.evaluate('location.hash'),'open=',await pg.evaluate('!document.getElementById("findRes").hidden'))
      # hash sync + back
      await pg.click('#findX')
      await pg.click('#groups button[data-g="1"]'); await pg.wait_for_timeout(250)
      await pg.click('#tabs button:has-text("COVID-19")'); await pg.wait_for_timeout(350)
      h1=await pg.evaluate('location.hash')
      await pg.go_back(); await pg.wait_for_timeout(600)
      h2=await pg.evaluate('location.hash'); t2=await pg.eval_on_selector('#tabs button[aria-selected="true"]','e=>e.textContent')
      print(f' hash after covid={h1}  back->{h2} curTab={t2}')
      # xlink from covid tab
      await pg.click('#groups button[data-g="1"]'); await pg.wait_for_timeout(200); await pg.click('#tabs button:has-text("COVID-19")'); await pg.wait_for_timeout(300)
      xl=await pg.evaluate('document.querySelectorAll("#tabpanel .xlink").length')
      await pg.click('#tabpanel .xlink[data-tab="rezeptoren"]'); await pg.wait_for_timeout(500)
      print(' xlinks in covid=',xl,'-> curTab=',await pg.eval_on_selector('#tabs button[aria-selected="true"]','e=>e.textContent'))
      # organ xlink
      await pg.click('#viewSeg button[data-v="body"]'); await pg.wait_for_timeout(200); await pg.locator('.organ[data-k="lung"]').evaluate(
          "e => e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")  # Klick wird sonst abgefangen
      await pg.wait_for_timeout(300)
      await pg.click('#organInfo .xlink[data-tab="covid"]'); await pg.wait_for_timeout(500)
      print(' lung->covid curTab=',await pg.eval_on_selector('#tabs button[aria-selected="true"]','e=>e.textContent'))
      ov=await pg.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
      print(' overflow=',ov,'errors=',errs)
      await pg.close()
    await b.close()
asyncio.run(main())

