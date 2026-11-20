# -*- coding: utf-8 -*-
"""Bedienung der Hirnkarte (Design-Runde 13.11.2026).
Schmal: 19 Regionen-Knoepfe sichtbar und gross genug, Beschriftungen im Bild
aus, Bildausschnitt aufs Gehirn, Antippen eines Knopfs waehlt die Region.
Breit: Knoepfe aus, Beschriftungen an. Beide: die fuenf kleinsten Regionen sind
an ihrer Mitte UND 4 Einheiten daneben treffbar, ohne dass ein Nachbar gewinnt."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright
EXE = _CHROME
SEITE=sys.argv[1] if len(sys.argv)>1 else 'file://' + HIER + '/page.html'
KLEIN={'pallidum':(164,130),'nigra':(211,203),'vta':(224,207),'pag':(217,222),'brech':(224,256)}
async def lauf(p, breite, pr):
    b=await p.chromium.launch(executable_path=EXE,args=['--no-sandbox'])
    ctx=await b.new_context(viewport={'width':breite,'height':900},has_touch=breite<700)
    pg=await ctx.new_page(); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
    await pg.goto(SEITE); await pg.wait_for_timeout(1800)
    if await pg.locator('#regionChips').is_visible(): pr.append('%d: Knoepfe schon in der Koerperansicht sichtbar'%breite)
    await pg.locator('#viewSeg button[data-v="brain"]').click(); await pg.wait_for_timeout(600)
    await pg.locator('#brainSvg').scroll_into_view_if_needed()
    schmal=breite<=640
    sicht=await pg.locator('#regionChips').is_visible()
    lab=await pg.evaluate("()=>getComputedStyle(document.querySelector('#brainSvg .rlabel')).display")
    vb=await pg.get_attribute('#brainSvg','viewBox')
    if schmal:
        if not sicht: pr.append('%d: Regionen-Knoepfe nicht sichtbar'%breite)
        if lab!='none': pr.append('%d: Beschriftungen im Bild noch sichtbar'%breite)
        if vb=='0 0 460 366': pr.append('%d: Bildausschnitt nicht verengt'%breite)
        n=await pg.locator('#regionChips .rchip').count()
        nreg=await pg.locator('#brainSvg .region').count()
        if n!=nreg: pr.append('%d Knoepfe, aber %d Regionen'%(n,nreg))
        h=await pg.evaluate("()=>Math.min(...[...document.querySelectorAll('#regionChips .rchip')].map(e=>e.getBoundingClientRect().height))")
        if h<36: pr.append('Knopf nur %.0f px hoch'%h)
        ueber=await pg.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")
        if ueber>1: pr.append('%d: Seite laeuft %d px seitlich ueber'%(breite,ueber))
        for k,name in (('vta','Tegmentum'),('olf','Riechkolben'),('cortex','Großhirnrinde')):
            await pg.locator('#regionChips .rchip[data-k="%s"]'%k).click(); await pg.wait_for_timeout(350)
            t=await pg.inner_text('#organInfo h3')
            if name not in t: pr.append('Knopf %s oeffnet %s'%(k,t))
            if await pg.get_attribute('#regionChips .rchip[data-k="%s"]'%k,'aria-pressed')!='true': pr.append('Knopf %s nicht als gewaehlt markiert'%k)
            if await pg.locator('#regionChips .rchip[aria-pressed="true"]').count()!=1: pr.append('mehr als ein Knopf gewaehlt')
        # Eine Reihe: Tafel muss ohne weites Scrollen unter dem Bild folgen, und der
        # gewaehlte Knopf muss in der Reihe sichtbar sein.
        lage=await pg.evaluate("""()=>{const c=document.getElementById('regionChips').getBoundingClientRect();const o=document.getElementById('organInfo').getBoundingClientRect();
          const s=document.querySelector('#regionChips .rchip[aria-pressed="true"]').getBoundingClientRect();return {h:c.height,ab:o.top-c.bottom,l:s.left-c.left,r:c.right-s.right}}""")
        if lage['h']>70: pr.append('%d: Knopfreihe ist %d px hoch - umbrochen?'%(breite,lage['h']))
        if lage['l']<-2 or lage['r']<-2: pr.append('%d: gewaehlter Knopf liegt ausserhalb der Reihe'%breite)
        farbe=await pg.evaluate("()=>[...document.querySelectorAll('#regionChips .rchip i')].filter(i=>!i.style.background).length")
        if farbe: pr.append('%d Knoepfe ohne Dichte-Farbfeld'%farbe)
    else:
        if sicht: pr.append('%d: Regionen-Knoepfe sichtbar, obwohl die Beschriftungen da sind'%breite)
        if lab=='none': pr.append('%d: Beschriftungen fehlen'%breite)
        if vb!='0 0 460 366': pr.append('%d: Bildausschnitt verengt: %s'%(breite,vb))
    await pg.evaluate("()=>document.getElementById('brainSvg').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(250)
    for k,(x,y) in KLEIN.items():
        for dx,dy in ((0,0),(4,0),(-4,0),(0,4),(0,-4)):
            wer=await pg.evaluate("""([x,y])=>{const sv=document.getElementById('brainSvg');const p=sv.createSVGPoint();p.x=x;p.y=y;const q=p.matrixTransform(sv.getScreenCTM());
              const e=document.elementFromPoint(q.x,q.y);return e&&e.closest('.region')?e.closest('.region').dataset.k:null}""",[x+dx,y+dy])
            if wer!=k: pr.append('%d: Punkt (%d|%d) bei %s trifft %s'%(breite,x+dx,y+dy,k,wer))
    if not schmal:
        await pg.locator('#rg-insula .rshape').hover(); await pg.wait_for_timeout(150)
        if not await pg.evaluate("()=>document.getElementById('rg-insula').classList.contains('hov')"): pr.append('Ueberfahren hebt nicht hervor')
    await pg.locator('#brainSvg').screenshot(path=HIER + '/hirn_%d.png'%breite)
    if schmal: await pg.screenshot(path=HIER + '/hirn_%d_seite.png'%breite)
    pr.extend('%d: %s'%(breite,e) for e in err)
    await b.close()
async def main():
    pr=[]
    async with async_playwright() as p:
        for w in (1280,390,360): await lauf(p,w,pr)
    print('Probleme:',pr or 'keine'); print('Fehler: keine')
    if pr: sys.exit(1)
asyncio.run(main())
