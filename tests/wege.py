# -*- coding: utf-8 -*-
"""Einstiegswege, Einleitungssatz je Breite, Umschalter auf Tippgeraeten."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright
EXE = _CHROME
SEITE=sys.argv[1] if len(sys.argv)>1 else 'file://' + HIER + '/page.html'
ZIEL={'botenstoffe':'Botenstoffe','anwendung':'Medizin','mythen':'Mythen-Check','bilanz':'Was man daraus lernen kann'}
async def lauf(p,w,pr):
    b=await p.chromium.launch(executable_path=EXE,args=['--no-sandbox'])
    ctx=await b.new_context(viewport={'width':w,'height':850},has_touch=w<700,is_mobile=w<700)
    pg=await ctx.new_page(); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
    await pg.goto(SEITE); await pg.wait_for_timeout(1800)
    lead=await pg.inner_text('header .lead')
    if w<=880 and ('Links siehst du' in lead or 'darunter' not in lead): pr.append('%d: Einleitung spricht von links/rechts: %s'%(w,lead[:80]))
    if w>880 and ('Links siehst du' not in lead or 'darunter' in lead): pr.append('%d: Einleitung falsch: %s'%(w,lead[:80]))
    if await pg.locator('.wege .xlink').count()!=4: pr.append('%d: nicht vier Wege'%w)
    m=await pg.evaluate("()=>{const vw=document.documentElement.clientWidth;return [...document.querySelectorAll('.wege .xlink')].map(e=>{const r=e.getBoundingClientRect();return [Math.round(r.height),r.right<=vw+1&&r.left>=-1]})}")
    for h,drin in m:
        if h<44: pr.append('%d: Weg nur %d px hoch'%(w,h))
        if not drin: pr.append('%d: Weg ragt aus dem Bild'%w)
    if await pg.evaluate("()=>document.documentElement.scrollWidth-document.documentElement.clientWidth")>1: pr.append('%d: seitlicher Ueberlauf'%w)
    for tab,name in ZIEL.items():
        await pg.evaluate("()=>window.scrollTo(0,0)"); await pg.locator('.wege .xlink[data-tab="%s"]'%tab).click(); await pg.wait_for_timeout(900)
        akt=await pg.evaluate("()=>{const b=document.querySelector('#tabs button[aria-selected=\"true\"],#tabs button.on,#tabs button[aria-pressed=\"true\"]');return b?b.textContent.trim():''}")
        if name not in akt: pr.append('%d: Weg %s oeffnet Reiter %r'%(w,tab,akt))
        y=await pg.evaluate("()=>document.getElementById('tabs').getBoundingClientRect().top")
        if not (-200<y<850): pr.append('%d: nach Weg %s ist der Reiter nicht im Bild (y=%d)'%(w,tab,y))
    if w<700:
        h=await pg.evaluate("()=>Math.min(...[...document.querySelectorAll('.seg button')].filter(b=>b.getBoundingClientRect().height>0).map(b=>b.getBoundingClientRect().height))")
        if h<33: pr.append('Umschalter nur %.0f px hoch'%h)
        await pg.evaluate("()=>window.scrollTo(0,0)"); await pg.wait_for_timeout(200); await pg.screenshot(path=HIER + '/wege_%d.png'%w)
    pr.extend('%d: %s'%(w,e) for e in err); await b.close()
async def main():
    pr=[]
    async with async_playwright() as p:
        for w in (1280,390): await lauf(p,w,pr)
    print('Probleme:',pr or 'keine'); print('Fehler: keine')
    if pr: sys.exit(1)
asyncio.run(main())
