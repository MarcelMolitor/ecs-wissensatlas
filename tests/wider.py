# -*- coding: utf-8 -*-
"""Der Reiter "Widersprueche" ist eine Zusammenfassung - seine Gefahr ist,
dass er etwas behauptet, was die Tafeln nicht tragen, oder dass er beim
naechsten Umbau still ins Leere zeigt.

Geprueft:
1. Der Reiter ist ueber eine GRUPPE erreichbar, nicht nur per Direktlink.
   (renderTabs() zeichnet NUR die ids der aktuellen Gruppe - ein Reiter, der
   in keiner Gruppe steht, existiert fuer den Mausbenutzer nicht. Genau das
   waere hier beinahe passiert.)
2. Alle fuenf Arten sind da, jede mit Sprungziel.
3. Jeder zitierte Beleg steht im Verzeichnis.
4. KEIN Beleg wird hier erstmals eingefuehrt - der Reiter fasst nur zusammen,
   was an den Tafeln steht. Jede PMID des Reiters muss auch ausserhalb davon
   vorkommen.
5. Die Querverweise zeigen auf vorhandene Organe und Reiter."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
m=re.search(r"\{id:'wider', t:'Widersprüche', html:\(\) => `(.*?)`\},\n",T,re.S)
if not m:
    print('FEHLER: Reiter wider nicht gefunden'); sys.exit(1)
W=m.group(1)
# 1 erreichbar
g=re.search(r'const GROUPS = \[(.*?)\n\];',T,re.S)
if not g or "'wider'" not in g.group(1):
    F.append('Der Reiter steht in keiner Gruppe - per Maus nicht erreichbar')
# 2 fuenf Arten
for sid in ['w-zwei','w-genauer','w-rezeptor','w-richtung','w-gemeint']:
    if 'id="%s"'%sid not in W: F.append('Abschnitt %s fehlt'%sid)
    if 'data-jump="${id}"' not in W and 'data-jump="%s"'%sid not in W and sid not in W:
        F.append('Sprungmarke %s fehlt'%sid)
spr=re.search(r"\[\['w-zwei'.*?\]\]",W,re.S)
if spr and len(re.findall(r"\['w-",spr.group(0)))!=5:
    F.append('Es sind nicht genau fuenf Sprungmarken')
# 3+4 Belege
pms=set(re.findall(r'\[\[(\d+)\]\]',W))
if len(pms)<18: F.append('Nur %d verschiedene Belege im Reiter - zu duenn'%len(pms))
aussen=T[:m.start()]+T[m.end():]
for pm in sorted(pms):
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    elif '[[%s]]'%pm not in aussen:
        F.append('Beleg %s kommt NUR im Widerspruchsreiter vor - er fuehrt eine Quelle ein, statt zusammenzufassen'%pm)
# 5 Querverweise
organe=set(re.findall(r'data-organ="(\w+)"',W))
vorhanden=set(re.findall(r"(\w+):\{name:'[^']+',(?:sl:'[^']*',)?rec:",T))
for o in sorted(organe):
    if "%s:{name:'"%o not in T: F.append('Organverweis %s zeigt ins Leere'%o)
reiter=set(re.findall(r'data-tab="(\w+)"',W))
for r in sorted(reiter):
    if "{id:'%s',"%r not in T: F.append('Reiterverweis %s zeigt ins Leere'%r)
# Der Reiter darf nicht behaupten, Widersprueche aufzuloesen
for b in ['löst das auf','ist damit geklärt','die richtige Studie ist']:
    if b in W: F.append('Anmassung: "%s"'%b)
print('FEHLER' if F else 'OK','Widerspruchsreiter: %d Belege, %d Organverweise, %d Reiterverweise, %d Zeichen'%(len(pms),len(organe),len(reiter),len(W)))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
