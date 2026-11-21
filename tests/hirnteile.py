# -*- coding: utf-8 -*-
"""Die drei am 13.11.2026 ergaenzten Hirnregionen: Stirnhirn, Globus pallidus,
Brechzentrum. Prueft gerenderten Text, Belegmarken, Dichtestufe, dass die
Formen sichtbar und nicht verdeckt sind, und dass keine Dosis dasteht."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright
EXE = _CHROME
SEITE=sys.argv[1] if len(sys.argv)>1 else 'file://' + HIER + '/page.html'
SOLL={'prefrontal':('Stirnhirn','hoch',['Assoziationsrinde','am Befinden der Teilnehmenden änderte sich dabei nichts','keine spürbare Wirkung','Eine eigene Dichtezahl']),
      'pallidum':('Globus pallidus','sehr hoch',['höchsten Einzelwerte','Gehirnen Verstorbener','eine eigene Tafel']),
      'nigra':('Substantia nigra','sehr hoch',['dichtesten besetzten Stellen','Mittelhirn ist nach derselben Messung gering besetzt','ist offen']),
      'cingulate':('Gyrus cinguli','hoch',['nicht aber, wie stark','41 Prozent höher','kein gesicherter Wert','Eine eigene Dichtezahl']),
      'insula':('Inselrinde','hoch',['als Folge, nicht als Angriffsort','nichts Schmerzspezifisches','ohne dass die Leistung litt','nur ungefähr eingetragen']),
      'olf':('Riechkolben','hoch',['Bei hungrigen Mäusen','Am Menschen ist das Gegenteil gemessen','gemessen ist sie nicht','stammt hier nicht vom Menschen']),
      'hypothalamus':('Hypothalamus','mäßig',['fast alles aus dem Tierversuch','die sonst Sättigung melden','das Ergebnis gemessen, nicht der Ort','an welcher Stelle im Körper']),
      'thalamus':('Thalamus','mäßig',['Kopplung zwischen Thalamus und Tastrinde','nicht begutachteten Vorabveröffentlichung']),
      'vta':('Tegmentum (VTA)','sehr gering',['Eine eigene Dichtemessung','abgeflachten','heißen nicht wenig Wirkung','ist hier nicht belegt']),
      'brech':('Brechzentrum','hoch',['am Frettchen gezeigt','Area postrema','der Ort nicht','deutlich schlechter vertragen','keinen Messwert am Menschen'])}
async def main():
    pr=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=EXE,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1280,'height':1100})
        err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1800)
        await pg.locator('#viewSeg button[data-v="brain"]').click(); await pg.wait_for_timeout(600)
        n=await pg.locator('#brainSvg .region').count()
        if n!=19: pr.append('%d Regionen statt 19'%n)
        for k,(name,dichte,muss) in SOLL.items():
            if not await pg.locator('#rg-'+k).count(): pr.append('Region fehlt: '+k); continue
            # Die Form muss an ihrem Mittelpunkt das oberste Element sein.
            await pg.locator('#brainSvg').scroll_into_view_if_needed()
            # Der Gyrus cinguli ist ein Bogen: Die Mitte seines Rahmens liegt
            # UNTER dem Bogen, also gar nicht in der Form. Dort wird ein Punkt
            # im Band geprueft (194|76), sonst die Rahmenmitte.
            oben=await pg.evaluate("""k=>{const s=document.querySelector('#rg-'+k+' .rshape');const r=s.getBoundingClientRect();
              let x=r.x+r.width/2,y=r.y+r.height/2;
              if(k==='cingulate'){const sv=document.getElementById('brainSvg');const p=sv.createSVGPoint();p.x=194;p.y=76;const q=p.matrixTransform(sv.getScreenCTM());x=q.x;y=q.y;}
              const e=document.elementFromPoint(x,y);return e&&e.closest('.region')?e.closest('.region').dataset.k:null}""",k)
            if oben!=k: pr.append('%s wird in der Mitte von %s verdeckt'%(k,oben))
            await pg.locator('#rg-'+k).evaluate("e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(450)
            t=await pg.inner_text('#organInfo')
            if len(sys.argv)>2: print(t,'\n')
            if name not in t.split('\n')[0]: pr.append('%s: Tafel zeigt %s'%(k,t[:30]))
            if '${' in t or '[[' in t: pr.append(k+': Vorlagenrest')
            if ('\n'+dichte) not in t.replace('\n\n','\n'): pr.append('%s: Dichte "%s" nicht gezeigt'%(k,dichte))
            for m in muss:
                if m not in t: pr.append('%s fehlt: %s'%(k,m))
            for v in ('Über diese Region laufen auch die Effekte','Eine eigene Funktionszuschreibung für diese Region gibt es nicht'):
                if v in t: pr.append(k+': zurueckgebauter Satz ist wieder da: '+v)
            for d in (' mg','Milligramm'):
                if d in t: pr.append(k+': Dosisangabe')
            if await pg.locator('#organInfo sup, #organInfo .ref').count()<(2 if k=='vta' else 3): pr.append(k+': weniger als 3 Belegmarken')
        drin=await pg.evaluate("""()=>{const sv=document.getElementById('brainSvg');const st=document.querySelector('#rg-brainstem .rshape');
          const pt=sv.createSVGPoint();let aus=0;for(const k of ['brech','nigra','vta','pag']){const bb=document.querySelector('#rg-'+k+' .rshape').getBBox();
          for(let a=0;a<360;a+=30){pt.x=bb.x+bb.width/2+bb.width/2*Math.cos(a*Math.PI/180)*.98;pt.y=bb.y+bb.height/2+bb.height/2*Math.sin(a*Math.PI/180)*.98;if(!st.isPointInFill(pt))aus++}}return aus}""")
        if drin: pr.append('Brechzentrum/Nigra/Tegmentum/Hoehlengrau: %d Punkte liegen ausserhalb des Hirnstamms'%drin)
        print('Probleme:',pr or 'keine'); print('Fehler:',err or 'keine')
        await pg.locator('#brainSvg').screenshot(path=HIER + '/hirn.png')
        await b.close()
        if pr or err: sys.exit(1)
asyncio.run(main())
