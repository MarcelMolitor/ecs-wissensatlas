
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, json
from playwright.async_api import async_playwright
html=open(HIER + '/page.html').read()
import sys
mock="""<script>
window.claude={use:async(n)=>{
 if(n==='mcp') return {callTool:async(srv,tool,input)=>{
   await new Promise(r=>setTimeout(r,50));
   if(tool==='search_articles') return {payload:{pmids:['1','2'],total_count:25598}};
   if(tool==='get_article_metadata') return {payload:{articles:[{identifiers:{pmid:'1',doi:'10.1/x'},title:'Test <b>title</b> one',abstract:'Abstract text.',journal:{iso_abbreviation:'J Test'},authors:[{last_name:'A',initials:'B'},{last_name:'C'},{last_name:'D'},{last_name:'E'}],publication_date:{year:'2026'},article_types:['Randomized Controlled Trial']},{identifiers:{pmid:'2'},title:'Two',abstract:'[Abstract not available]',journal:{title:'X'},authors:[],publication_date:{year:'2025'},article_types:['Review']}]}};
   if(tool==='search_trials') return {payload:{count:1,total:308,next_page_token:'tok',items:[{nct_id:'NCT01035281',title:'Trial title',status:'RECRUITING',phase:['PHASE2'],conditions:['Pain'],interventions:['Nabilone'],sponsor:'Uni',enrollment:60,start_date:'2008-01',primary_completion_date:'2011-01',locations_count:1,study_type:'INTERVENTIONAL'}]}};
 }};
 if(n==='sample') return async(p,o)=>{o.onText&&o.onText({text:'Deutsch Satz eins.',delta:''});return {text:'Deutsch Satz eins. Zwei. Drei.',truncated:false}};
 return null;}};
</script>"""
doc='<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"></head><body>'+mock+html+'</body></html>'
# 21.11.2026: Dieser Test schrieb seine praeparierte Fassung frueher ZURUECK
# nach page.html - die gemeinsame Pruefkopie aller Tests - und stellte sie nie
# wieder her. Die 20 Tests, die alphabetisch nach run.py laufen, prueften damit
# eine Seite in einer zweiten HTML-Huelle und mit einer Attrappe fuer
# window.claude. Dieselbe Fehlerart wie im November, als 22 Tests die
# Arbeitsdatei statt der geprueften Fassung lasen. Eigene Datei, und danach weg.
EIGEN = HIER + '/page-run.html'
open(EIGEN,'w').write(doc)
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    errs=[]
    for name,vp in [('desk',{'width':1280,'height':900}),('phone',{'width':390,'height':844})]:
      pg=await b.new_page(viewport=vp)
      pg.on('pageerror',lambda e:errs.append(str(e)))
      pg.on('console',lambda m:errs.append('console:'+m.text) if m.type=='error' else None)
      await pg.goto('file://' + EIGEN); await pg.wait_for_timeout(800)
      # click every substance
      chips=await pg.query_selector_all('.chip')
      for c in chips:
        await c.click(); await pg.wait_for_timeout(250)
      # organs
      for o in await pg.query_selector_all('.organ .ring-base'): await o.click(timeout=3000)
      # tabs
      for t in await pg.query_selector_all('#tabs .tab'):
        await t.click(); await pg.wait_for_timeout(300)
      # studies jump from substance
      await pg.click('.chip[data-id="cbd"]'); await pg.wait_for_timeout(200)
      await pg.click('#subStudies button[data-k="pm"]'); await pg.wait_for_timeout(600)
      st=await pg.inner_text('#stList'); meta=await pg.inner_text('#stMeta')
      await pg.click('.js-sum'); await pg.wait_for_timeout(300)
      sm=await pg.inner_text('#stList')
      await pg.click('#stMore'); await pg.wait_for_timeout(400)
      await pg.click('#subStudies button[data-k="ct"]'); await pg.wait_for_timeout(600)
      ct=await pg.inner_text('#ctMeta')+' | '+await pg.inner_text('#ctList')
      await pg.click('#ctMore'); await pg.wait_for_timeout(300)
      ov=await pg.evaluate('document.documentElement.scrollWidth - window.innerWidth')
      print(name,'overflow',ov)
      print(' studien:',st[:120].replace('\n',' / '),'| meta:',meta)
      print(' summary has german:', 'Deutsch Satz' in sm)
      print(' ct:',ct[:200].replace('\n',' / '))
      await pg.evaluate('window.scrollTo(0,0)')
      await pg.screenshot(path=f'{name}.png',full_page=False)
      await pg.click('.chip[data-id="thc"]'); await pg.wait_for_timeout(1500)
      await pg.locator('#synapse .lab').screenshot(path=f'{name}-lab.png')
      res={}
      for sid in ['thc','syn','thcv','rim']:
        await pg.click(f'.chip[data-id="{sid}"]')
        for d in ['0','2']:
          await pg.evaluate(f"(()=>{{const r=document.getElementById('dose');r.value='{d}';r.dispatchEvent(new Event('input'))}})()")
          await pg.wait_for_timeout(2500)
          res[sid+d]=await pg.inner_text('#mv0')
      print(' dose CB1-activation low/high:',res)
      await pg.click('.chip[data-id="cbd"]')
      n=await pg.locator('#status sup.cite').count(); print(' cbd citations in status:',n)
      await pg.locator('#status sup.cite a').first.click(); await pg.wait_for_timeout(800)
      print(' flashed:', await pg.evaluate("document.querySelector('.st-item.flash')?.id"))
      await pg.locator('#synapse .lab').screenshot(path=f'{name}-lab2.png')
      await pg.locator('#doseBox').screenshot(path=f'{name}-dose.png')
      await pg.click('#groups button[data-g="0"]'); await pg.click('#tab-gene'); await pg.wait_for_timeout(300)
      print(' gene cites:', await pg.locator('#tabpanel sup.cite').count())
    print('ERRORS',errs)
    await b.close()
    _os.path.exists(EIGEN) and _os.remove(EIGEN)
asyncio.run(main())
