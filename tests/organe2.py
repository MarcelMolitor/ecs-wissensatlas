# -*- coding: utf-8 -*-
"""Mund & Speichel, Gehoer (13.11.2026). Prueft Tafeltext, die drei Fallen
(Chancenverhaeltnis statt Haeufigkeit; Hoerkern statt Innenohr; Dichte ohne
Messwert am Menschen) und dass die Beschriftungen im Bild bleiben."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright
EXE = _CHROME
SEITE=sys.argv[1] if len(sys.argv)>1 else 'file://' + HIER + '/page.html'
SOLL={'mund':(['an Mäusen gezeigt','nicht auf den Drüsenzellen','Chancenverhältnis 2,1','einen Zusammenhang, keine Ursache','nicht nachgewiesen','Deutliche Wirkung'],['doppelt so oft','doppelt so häufig']),
      'ohr':(['Hörkern','weder im Tierversuch noch am Menschen überzeugende Daten','nach fünf und zehn Jahren zeigte sich kein Unterschied','nicht trennen','nicht nachgewiesen','Keine belegte Wirkung gegen Tinnitus'],['hilft gegen Tinnitus','lindert Tinnitus','im Innenohr sitzt'])}
async def main():
    pr=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=EXE,args=['--no-sandbox'])
        for w in (1280,390):
            pg=await b.new_page(viewport={'width':w,'height':1000}); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
            await pg.goto(SEITE); await pg.wait_for_timeout(1800)
            n=await pg.locator('#bodySvg .organ').count()
            # 14.11.2026: 21 mit den peripheren Nerven (t/nerven.py).
            if n!=23: pr.append('%d Organe statt 23'%n)
            raus=await pg.evaluate("""()=>{const sv=document.getElementById('bodySvg').getBoundingClientRect();return [...document.querySelectorAll('#bodySvg .olabel')].filter(t=>{const r=t.getBoundingClientRect();return r.left<sv.left-1||r.right>sv.right+1}).map(t=>t.textContent)}""")
            if raus: pr.append('%d: Beschriftung laeuft aus dem Bild: %s'%(w,raus))
            await pg.locator('button.chip[data-id="thc"]').first.evaluate("e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(400)
            for k,(muss,verboten) in SOLL.items():
                if not await pg.locator('#or-'+k).count(): pr.append('Organ fehlt: '+k); continue
                await pg.locator('#or-'+k).evaluate("e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(300)
                t=await pg.inner_text('#organInfo')
                if '${' in t or '[[' in t: pr.append(k+': Vorlagenrest')
                for m in muss:
                    if m not in t: pr.append('%s fehlt: %s'%(k,m))
                for v in verboten+[' mg','Joint']:
                    if v in t: pr.append('%s: unerwuenscht: %s'%(k,v))
            pr.extend(err); await pg.close()
        print('Probleme:',pr or 'keine'); print('Fehler: keine')
        await b.close()
        if pr: sys.exit(1)
asyncio.run(main())
