
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
TOURVIS = '!document.getElementById("tour").hidden'
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    for nm,vp in [('desk',{'width':1280,'height':900}),('phone',{'width':390,'height':844})]:
      errs=[]; pg=await b.new_page(viewport=vp)
      pg.on('pageerror',lambda e:errs.append(str(e)))
      for h,card in [('#nachbarn/n-tnf','n-tnf'),
                     ('#entzuendung/c-was-die-kette-zusammengenommen-tragt','c-was-die-kette-zusammengenommen-tragt'),
                     ('#covid/c-unterm-strich','c-unterm-strich')]:
        await pg.goto('file://' + HIER + '/page.html'+h); await pg.wait_for_timeout(1300)
        ok=await pg.evaluate('(()=>{const e=document.getElementById("%s");if(!e)return "KARTE FEHLT";const r=e.getBoundingClientRect();return r.top>-100&&r.top<innerHeight})()'%card)
        tab=await pg.eval_on_selector('#tabs button[aria-selected="true"]','e=>e.textContent')
        print(f'[{nm}] {h:55s} Reiter={tab:16s} sichtbar={ok} Tour={await pg.evaluate(TOURVIS)}')
      await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(1300)
      print(f'[{nm}] ohne Direktlink: Tour={await pg.evaluate(TOURVIS)} Fehler={errs}')
      await pg.close()
    await b.close()
asyncio.run(main())
