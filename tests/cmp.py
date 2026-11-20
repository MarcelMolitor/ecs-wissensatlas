
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
exec(open(HIER + '/run.py').read().split('async def main')[0])
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    for scheme,name,vp in [('light','desk',{'width':1280,'height':900}),('dark','phone',{'width':390,'height':844})]:
      ctx=await b.new_context(viewport=vp,color_scheme=scheme); pg=await ctx.new_page(); errs=[]
      pg.on('pageerror',lambda e:errs.append(str(e)))
      await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(600)
      await pg.click('.chip[data-id="thc"]')
      terms=await pg.locator('#synapse .term').count()
      await pg.click('#subStudies button[data-k="cmp"]'); await pg.wait_for_timeout(2500)
      vals=await pg.evaluate("[...document.querySelectorAll('#vergleich .val')].map(v=>v.textContent).join(' | ')")
      sels=await pg.evaluate("[...document.querySelectorAll('.cmp-sel')].map(s=>s.value)")
      await pg.locator('#vergleich').screenshot(path=f'{name}-cmp.png')
      await pg.select_option('.cmp-col[data-side="1"] select','cbd'); await pg.wait_for_timeout(1200)
      vals2=await pg.evaluate("[...document.querySelectorAll('.cmp-col[data-side=\"1\"] .val')].map(v=>v.textContent).join(' | ')")
      # tooltip
      await pg.click('#cmpClose'); await pg.wait_for_timeout(300)
      t=pg.locator('#synapse .term').first; label=await t.inner_text(); await t.click(); await pg.wait_for_timeout(200)
      tipv=await pg.is_visible('#tip'); tipt=await pg.inner_text('#tipT')
      box=await pg.locator('#tip').bounding_box()
      await pg.screenshot(path=f'{name}-tip.png')
      await pg.keyboard.press('Escape'); tiph=await pg.is_hidden('#tip')
      await pg.click('#groups button[data-g="1"]'); await pg.click('#tab-wechsel'); tt=await pg.locator('#tabpanel .term').count()
      ov=await pg.evaluate('document.documentElement.scrollWidth - window.innerWidth')
      print(name,scheme,'terms',terms,'| sel',sels,'| vals',vals,'| cbd side',vals2,'| tip',label,'->',tipt,tipv,'esc-hidden',tiph,'box',box and (round(box['x']),round(box['width'])),'| wechsel terms',tt,'| overflow',ov,'| errs',errs)
    await b.close()
asyncio.run(main())
