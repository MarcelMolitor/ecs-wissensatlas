
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    pg=await b.new_page(viewport={'width':1280,'height':900})
    errs=[]; pg.on('pageerror',lambda e:errs.append('ERR:'+str(e)))
    pg.on('console',lambda m:errs.append('C:'+m.text) if m.type=='error' else None)
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(900)
    # 1. Alle Substanzen durchklicken
    n=await pg.evaluate("document.querySelectorAll('#picker .chip').length")
    print('Substanzen:', n)
    bad=[]
    for i in range(n):
      c=pg.locator('#picker .chip').nth(i); lbl=(await c.inner_text()).strip()
      await c.click(); await pg.wait_for_timeout(260)
      st=await pg.evaluate("""() => ({name:document.getElementById('subName').textContent.trim(),
        what:document.getElementById('subWhat').textContent.length,
        steps:document.querySelectorAll('#steps li').length,
        meters:document.querySelectorAll('#meters .meter').length,
        canvas:(()=>{const c=document.getElementById('cv');return c?c.width*c.height:0})()})""")
      if not st['name'] or st['what']<20 or st['steps']==0 or st['canvas']==0: bad.append((lbl,st))
    print('Substanzen mit Problemen:', bad or 'keine')
    # 2. Organe und Hirnregionen
    await pg.evaluate("document.querySelector('#picker .chip').click()"); await pg.wait_for_timeout(250)
    org=await pg.evaluate("""() => { const o=[...document.querySelectorAll('#bodySvg .organ')]; const bad=[];
      for (const e of o){ e.dispatchEvent(new MouseEvent('click',{bubbles:true}));
        const t=document.getElementById('organInfo').textContent.trim(); if (t.length<20) bad.push(e.id||'?'); }
      return {anzahl:o.length, leer:bad}; }""")
    print('Organe:', org)
    await pg.click('#viewSeg button[data-v="brain"]'); await pg.wait_for_timeout(350)
    br=await pg.evaluate("""() => { const o=[...document.querySelectorAll('#brainSvg .region')]; const bad=[];
      for (const e of o){ e.dispatchEvent(new MouseEvent('click',{bubbles:true}));
        const t=document.getElementById('organInfo').textContent.trim(); if (t.length<20) bad.push(e.id||'?'); }
      return {anzahl:o.length, leer:bad}; }""")
    print('Hirnregionen:', br)
    await pg.click('#viewSeg button[data-v="body"]'); await pg.wait_for_timeout(250)
    # 3. Genotyp, Dosis, Schritt-Modus, Pause
    await pg.click('#genSeg button[data-g="AA"]'); await pg.wait_for_timeout(250)
    print('Genotyp AA Text:', (await pg.inner_text('#genText'))[:48])
    vis=await pg.evaluate("!document.getElementById('doseBox').hidden")
    if vis:
      await pg.evaluate("const d=document.getElementById('dose'); d.value=2; d.dispatchEvent(new Event('input',{bubbles:true}))")
      await pg.wait_for_timeout(250); print('Dosis-Text:', (await pg.inner_text('#doseTxt'))[:48])
    await pg.click('#stepBtn'); await pg.wait_for_timeout(300)
    print('Schritt-Modus:', (await pg.inner_text('#stepTxt'))[:46])
    await pg.click('#stepNext'); await pg.wait_for_timeout(250)
    print('nach Weiter:', (await pg.inner_text('#stepTxt'))[:46])
    await pg.click('#stepEnd'); await pg.wait_for_timeout(200)
    await pg.click('#playBtn'); await pg.wait_for_timeout(200)
    await pg.click('#resetBtn'); await pg.wait_for_timeout(300)
    # 4. Wirkstoff-Labor
    await pg.evaluate("location.hash='#labor'"); await pg.wait_for_timeout(900)
    lab=await pg.evaluate("""() => ({canvas:(()=>{const c=document.getElementById('labCv');return c?c.width*c.height:0})(),
      regler:document.querySelectorAll('#tabpanel .lab-ctl').length,
      urteil:(document.querySelector('#tabpanel .lab-note')||{}).textContent?.length||0})""")
    print('Labor:', lab)
    sel=await pg.evaluate("[...document.querySelectorAll('#tabpanel select')].length")
    if sel: 
      await pg.evaluate("const s=document.querySelector('#tabpanel select'); s.selectedIndex=(s.selectedIndex+1)%s.options.length; s.dispatchEvent(new Event('change',{bubbles:true}))")
      await pg.wait_for_timeout(500)
    print('Labor nach Umstellen ok:', await pg.evaluate("document.querySelectorAll('#tabpanel .lab-ctl').length>0"))
    # 5. Suche
    await pg.fill('#findQ','MAGL'); await pg.wait_for_timeout(450)
    print('Suchtreffer MAGL:', await pg.evaluate("document.querySelectorAll('#findRes button').length"))
    await pg.click('#findRes button'); await pg.wait_for_timeout(700)
    print('Suche springt nach:', await pg.evaluate("document.querySelector('#tabs [aria-selected=true]')?.textContent"))
    print('Fehler:', [e for e in errs if 'ERR_' not in e and 'Failed to fetch' not in e][:6] or 'keine')
    await b.close()
asyncio.run(main())
