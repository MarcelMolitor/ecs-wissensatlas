
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
WIDTHS=[320,360,390,768,1024,1280]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    for w in WIDTHS:
      pg=await b.new_page(viewport={'width':w,'height':860})
      await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(700)
      groups=await pg.evaluate("document.querySelectorAll('#groups button').length")
      worst=[]
      for g in range(groups):
        await pg.click(f'#groups button[data-g="{g}"]'); await pg.wait_for_timeout(180)
        n=await pg.evaluate("document.querySelectorAll('#tabs button').length")
        for i in range(n):
          t=pg.locator('#tabs button').nth(i); lbl=await t.inner_text(); await t.click(); await pg.wait_for_timeout(230)
          ov=await pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
          if ov>0:
            culprit=await pg.evaluate("""() => {
              const vw=document.documentElement.clientWidth, out=[];
              for (const el of document.querySelectorAll('#tabpanel *')){
                const r=el.getBoundingClientRect();
                if (r.right > vw+1 && r.width>0) out.push([el.tagName.toLowerCase()+'.'+(el.className||'').toString().split(' ').filter(Boolean).slice(0,2).join('.'), Math.round(r.right-vw)]);
              }
              return out.sort((a,b)=>b[1]-a[1]).slice(0,3);
            }""")
            worst.append((lbl,ov,culprit))
      print(f'[{w}px] Überlauf:', worst if worst else 'keiner')
      await pg.close()
    # Überschriftenhierarchie
    pg=await b.new_page(viewport={'width':1280,'height':900})
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(700)
    hh=await pg.evaluate("""() => {
      const groups=[...document.querySelectorAll('#groups button')], bad=[];
      for (let g=0; g<groups.length; g++){ groups[g].click();
        for (const t of [...document.querySelectorAll('#tabs button')]){ t.click();
          const hs=[...document.getElementById('tabpanel').querySelectorAll('h1,h2,h3,h4,h5')].map(h=>+h.tagName[1]);
          let prev=2, jumps=[];
          for (const lv of hs){ if (lv-prev>1) jumps.push(prev+'->'+lv); prev=lv; }
          if (jumps.length) bad.push([t.textContent.trim(), jumps.slice(0,3)]);
        } }
      return bad;
    }""")
    print('\nÜberschriftensprünge:', hh if hh else 'keine')
    # Druckansicht
    await pg.emulate_media(media='print')
    await pg.evaluate("location.hash='#fatigue'"); await pg.wait_for_timeout(600)
    pr=await pg.evaluate("""() => ({
      jumpsHidden: [...document.querySelectorAll('#tabpanel .jumps')].every(e=>getComputedStyle(e).display==='none'),
      anchorsHidden: [...document.querySelectorAll('#tabpanel .anchor')].every(e=>getComputedStyle(e).display==='none'),
      tabsHidden: getComputedStyle(document.getElementById('tabs')).display==='none',
      citeSrc: (document.querySelector('#tabpanel sup.cite a')||{}).dataset?.src || null,
      tableVisible: !!document.querySelector('#tabpanel table')
    })""")
    print('Druckansicht:', pr)
    await b.close()
asyncio.run(main())
