# -*- coding: utf-8 -*-
"""Die freie Studiensuche darf nicht wieder auf advanced_query zurückfallen.

ANLASS (14.11.): Die Seite schickte die freie Eingabe als advanced_query. Echte
Aufrufe zeigten, dass das dort die falsche Tuer ist:
  "cannabidiol anxiety"                        -> 206 Treffer, die ersten drei
                                                  ohne jeden Angst-Bezug
  "cannabidiol AND anxiety"                    -> IDENTISCH 206, das UND wird
                                                  ignoriert
  condition=anxiety + intervention=cannabidiol -> 39, alle passend
Der Platzhalter schlug ausgerechnet das Beispiel vor, das nicht funktioniert.

Dieser Test haelt die Reparatur fest."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys,asyncio
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
# 1. advanced_query darf aus der Nutzereingabe nicht mehr entstehen
ci=re.search(r"function ctInput\(\)\{.*?\n\}",T,re.S)
if not ci: F.append('ctInput nicht gefunden')
else:
    b=ci.group(0)
    # Kommentare entfernen - sonst trifft die Pruefung den Erklaertext statt des Codes.
    # (Genau dieser Fehlalarm ist beim Schreiben dieses Tests passiert.)
    code=re.sub(r'/\*.*?\*/','',b,flags=re.S)
    code=re.sub(r'//[^\n]*','',code)
    if 'advanced_query:' in code or 'advanced_query ' in code:
        F.append('ctInput schickt wieder advanced_query')
    if 'condition:' not in b or 'intervention:' not in b:
        F.append('ctInput baut nicht condition/intervention aus der Eingabe')
# 2. beide Felder im Markup, altes Feld weg
for fid in ['ctQCond','ctQIntr']:
    if 'id="%s"'%fid not in T: F.append('Feld %s fehlt'%fid)
if 'id="ctQ"' in T: F.append('Das alte Einzelfeld ctQ ist noch da')
if 'CT.custom' in T: F.append('CT.custom wird noch verwendet')
# 3. der irrefuehrende Platzhalter darf nicht zurueck
if 'z. B. cannabidiol anxiety' in T:
    F.append('Der Platzhalter schlaegt wieder die kombinierte Eingabe vor, die nicht funktioniert')
# 4. der Aussenlink baut Felder, nicht term=
cs=re.search(r"function ctSearchUrl\(\)\{.*?\n\}",T,re.S)
if cs:
    b=cs.group(0)
    if "'cond='" not in b or "'intr='" not in b: F.append('ctSearchUrl baut keine Feldparameter')
# 5. Darstellung: beide Felder da, kein Fehler, kein Ueberlauf am Handy
async def sicht():
    from playwright.async_api import async_playwright
    out=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--no-sandbox'],executable_path=_CHROME)
        for w in (1180,390):
            pg=await b.new_page(viewport={'width':w,'height':900})
            err=[]; pg.on('pageerror',lambda e:err.append(str(e)))
            await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(1300)
            await pg.evaluate("location.hash='#klinisch'"); await pg.wait_for_timeout(1000)
            r=await pg.evaluate("""(()=>({c:!!document.getElementById('ctQCond'),i:!!document.getElementById('ctQIntr'),
               alt:!!document.getElementById('ctQ'),ue:document.documentElement.scrollWidth>window.innerWidth+1}))()""")
            if not r['c'] or not r['i']: out.append('%dpx: ein Feld fehlt'%w)
            if r['alt']: out.append('%dpx: altes Feld noch da'%w)
            if r['ue']: out.append('%dpx: seitlicher Ueberlauf'%w)
            if err: out.append('%dpx: Seitenfehler %s'%(w,err[0][:80]))
            await pg.close()
        await b.close()
    return out
F += asyncio.run(sicht())
print('FEHLER' if F else 'OK','Studiensuche nutzt condition/intervention statt advanced_query')
for f in F: print(' -',f)
sys.exit(1 if F else 0)
