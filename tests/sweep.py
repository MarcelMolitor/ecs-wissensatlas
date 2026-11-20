
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    for name,vp,theme in [('desk',{'width':1280,'height':900},'light'),('phone',{'width':390,'height':844},'dark')]:
      errs=[]
      pg=await b.new_page(viewport=vp,color_scheme=theme)
      pg.on('pageerror',lambda e:errs.append('ERR:'+str(e)))
      pg.on('console',lambda m:errs.append('C:'+m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text else None)
      await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(700)
      ng=await pg.evaluate('document.querySelectorAll("#groups button").length')
      bad=[]; seen=[]
      for g in range(ng):
        await pg.click(f'#groups button[data-g="{g}"]'); await pg.wait_for_timeout(300)
        for i in range(await pg.evaluate('document.querySelectorAll("#tabs button").length')):
          t=pg.locator('#tabs button').nth(i)
          lbl=await t.inner_text(); await t.click(); await pg.wait_for_timeout(350)
          h=await pg.inner_html('#tabpanel'); seen.append(lbl)
          if '[[' in h: bad.append(lbl+':marker')
          if len(await pg.inner_text('#tabpanel'))<80: bad.append(lbl+':empty')
      ov=await pg.evaluate('document.documentElement.scrollWidth-document.documentElement.clientWidth')
      print(f'[{name}/{theme}] tabs={len(seen)} overflow={ov} problems={bad} errors={errs}')
      print('   ',seen)
      await pg.close()
    await b.close()
asyncio.run(main())
