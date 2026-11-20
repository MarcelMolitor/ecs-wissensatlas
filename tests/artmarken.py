# -*- coding: utf-8 -*-
"""Art-Marken (Mensch/Tier/Zelle) hinter den Quellen der Kartentafeln.
Prueft: jede Quelle mit eindeutigem Typ traegt die richtige Marke (gegen das
Verzeichnis gerechnet, nicht gegen eine Liste), ausserhalb der Tafeln erscheint
keine, die Legende ist sichtbar."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, io, re, sys
from playwright.async_api import async_playwright
EXE = _CHROME
SEITE=sys.argv[1] if len(sys.argv)>1 else 'file://' + HIER + '/page.html'
QUELLE=SEITE.replace('file://','') if len(sys.argv)>1 else HIER + '/page.html'
SOLL={'Tierstudie':'Tier','Zellversuch':'Zelle','Mensch + Tier':'Mensch+Tier','RCT':'Mensch','Mensch':'Mensch','Meta-Analyse':'Mensch','Beobachtung':'Mensch','Fallserie':'Mensch','Studie ohne Kontrolle':'Mensch','Umfrage':'Mensch','Fallbericht':'Mensch','Genetik-Studie':'Mensch'}
async def main():
    pr=[]
    S=io.open(QUELLE,encoding='utf-8').read()
    typ={m.group(1):m.group(2) for m in re.finditer(r"\['(\d+)',\d{4},'[^']*','[^']*','(?:[^'\\]|\\.)*','[^']*','([^']*)'",S)}
    if len(typ)<500: pr.append('nur %d Quellen erkannt'%len(typ))
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path=EXE,args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1280,'height':1100}); err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1800)
        JS="""()=>[...document.querySelectorAll('#organInfo sup.cite a[data-pm]')].map(a=>{const c=getComputedStyle(a.parentElement,'::after').content;return [a.dataset.pm,c]})"""
        gesehen=0; arten=set()
        await pg.locator('#viewSeg button[data-v="brain"]').click(); await pg.wait_for_timeout(500)
        for k in await pg.evaluate("()=>[...document.querySelectorAll('#brainSvg .region')].map(g=>g.dataset.k)"):
            await pg.locator('#rg-'+k).evaluate("e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(120)
            for pm,c in await pg.evaluate(JS):
                gesehen+=1; soll=SOLL.get(typ.get(pm,''))
                ist=None if c in ('none','normal','""') else c.strip('"')
                if ist: arten.add(ist)
                if ist!=soll: pr.append('%s/%s: Marke %r, erwartet %r (Typ %s)'%(k,pm,ist,soll,typ.get(pm)))
        if gesehen<60: pr.append('nur %d Quellen in den Hirntafeln gesehen'%gesehen)
        if not {'Mensch','Tier'}<=arten: pr.append('Marken-Arten in den Hirntafeln: %s'%arten)
        print('  %d Quellen in 19 Hirntafeln geprueft, Arten: %s'%(gesehen,sorted(arten)))
        if not await pg.locator('#artLeg').is_visible(): pr.append('Legende nicht sichtbar')
        # Ausserhalb der Tafeln keine Marke
        aus=await pg.evaluate("""()=>[...document.querySelectorAll('sup.cite[data-art]')].filter(s=>!s.closest('#organInfo')).filter(s=>{const c=getComputedStyle(s,'::after').content;return c!=='none'&&c!=='normal'}).length""")
        if aus: pr.append('%d Marken ausserhalb der Kartentafeln'%aus)
        await pg.locator('#rg-olf').evaluate("e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))"); await pg.wait_for_timeout(300)
        await pg.locator('#organInfo').screenshot(path=HIER + '/marken.png')
        print('Probleme:',pr[:12] or 'keine'); print('Fehler:',err or 'keine')
        await b.close()
        if pr or err: sys.exit(1)
asyncio.run(main())
