# -*- coding: utf-8 -*-
"""Amygdala-Tafel: Tierbefund als Tierbefund, Genvariante, und der misslungene
Schritt zur Krankheit (PET bei PTBS, negativer FAAH-Hemmer). Vorher trug die
Tafel nur die Genvariante, obwohl die anderen Belege auf der Seite standen."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright
EXE = _CHROME
SEITE=sys.argv[1] if len(sys.argv)>1 else 'file://' + HIER + '/page.html'
MUSS=['Mäuse ohne CB1','verlernten Angst leichter','rund 10 Prozent niedriger','ohne Zusammenhang mit den Beschwerden','nicht stärker als die Vergleichsbehandlung','an Mäusen gezeigt']
async def main():
    pr=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=EXE,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1280,'height':1100})
        err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1800)
        await pg.locator('#viewSeg button[data-v="brain"]').click(); await pg.wait_for_timeout(500)
        await pg.locator('#rg-amygdala').evaluate("e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(500)
        t=await pg.evaluate("()=>{const r=document.querySelector('#rg-amygdala');let n=document.querySelector('#organInfo');return n?n.innerText:''}")
        if len(sys.argv)>2: print(t)
        if '${' in t or '[[' in t: pr.append('Vorlagenrest')
        for m in MUSS:
            if m not in t: pr.append('fehlt: '+m)
        kn=pg.locator('#organInfo .xlink[data-card="g-ptbs"]')
        if await kn.count()!=1: pr.append('Verweis auf g-ptbs fehlt')
        else:
            await kn.click(); await pg.wait_for_timeout(900)
            if not await pg.evaluate("()=>{const c=document.getElementById('g-ptbs');return c?c.getBoundingClientRect().height>0:false}"): pr.append('Verweis fuehrt ins Leere')
        print('Probleme:',pr or 'keine'); print('Fehler:',err or 'keine')
        await b.close()
        if pr or err: sys.exit(1)
asyncio.run(main())
