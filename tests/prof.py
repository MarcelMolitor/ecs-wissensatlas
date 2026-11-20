
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
    ctx=await b.new_context(viewport={'width':1280,'height':900})
    pg=await ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.route('http://atlas.test/', lambda r: r.fulfill(body=open(HIER + '/page.html').read(), content_type='text/html'))
    await pg.goto('http://atlas.test/'); await pg.wait_for_timeout(600)
    print('foryou hidden before:', await pg.is_hidden('#forYou'))
    await pg.click('#mySeg button[data-g="CA"]'); await pg.wait_for_timeout(300)
    print('foryou aea:', (await pg.inner_text('#forYou'))[:90])
    print('genText:', await pg.inner_text('#genText'))
    await pg.click('.chip[data-id="cbd"]'); print('cbd:', (await pg.inner_text('#forYou'))[:120])
    await pg.reload(); await pg.wait_for_timeout(600)
    print('after reload pressed:', await pg.get_attribute('#mySeg button[data-g="CA"]','aria-pressed'), '| sim gen:', await pg.get_attribute('#genSeg button[data-g="CA"]','aria-pressed'))
    await pg.click('#tab-gene'); print('gene badge:', await pg.locator('.badge.me').count())
    await pg.click('#mySeg button[data-g=""]'); await pg.wait_for_timeout(200); print('cleared hidden:', await pg.is_hidden('#forYou'), '| badge:', await pg.locator('.badge.me').count())
    await pg.locator('.topbar').screenshot(path='top.png')
    await pg.click('#mySeg button[data-g="AA"]'); await pg.locator('.panel').nth(1).screenshot(path='fy.png')
    print('ERR',errs); await b.close()
asyncio.run(main())
