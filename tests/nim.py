# -*- coding: utf-8 -*-
"""Die Nimacimab-Karte muss VOLLSTAENDIG bleiben - das war die Bedingung, unter
der sie ueberhaupt gebaut wurde ("halb gebaut waere schlechter als gar nicht").

Ein neuer Stoff haengt auf dieser Seite an SECHS Stellen. Fehlt eine, sieht die
Karte fertig aus und ist es nicht:
  1. Stoff-Eintrag mit organs, obasisEv, obasis, sim
  2. COL   - Farbtoken des Molekuels
  3. PERM  - damit es den Rezeptor dauerhaft blockiert wie rim und mon
  4. Simulationslegende - Name des Molekuels
  5. Formregel - Blocker werden als Quadrat gezeichnet
  6. Querverweis aus Monlunabant heraus

INHALTLICH bewacht der Test das, was bei diesem Stoff am leichtesten verloren
geht: dass die Beleglage MAGER ist und das auch dasteht. Es gibt keine
Primaerpublikation; wuerde jemand die Karte spaeter "aufwerten", waere das die
erste Zeile, die verschwindet. Ebenso der Satz, dass die laufende Studie das
Psyche-Problem konstruktionsgemaess nicht beantworten kann.
Faellt gegen vor-nim.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
i=T.find("{id:'nim',group:")
if i<0:
    print('FEHLER: Stoff-Eintrag nim fehlt'); sys.exit(1)
d=0;k=i
while True:
    if T[k]=='{': d+=1
    elif T[k]=='}':
        d-=1
        if d==0: break
    k+=1
O=T[i:k+1]
# 1. Vollstaendigkeit des Eintrags
for sch in ['name:','short:','color:','route:','target:','kind:','what:','steps:','status:','organs:','obasisEv:','obasis:','sim:']:
    if sch not in O: F.append('Eintrag ohne %s'%sch)
felder=re.findall(r"(\w+):\[(\d),",O[O.find('organs:'):])
if len(felder)<3: F.append('Nur %d Organfelder'%len(felder))
if 'extra:{type:\'nim\'' not in O: F.append('sim ohne eigenes Molekuel')
# 2-5. die Verdrahtung
for was,anker in [('COL',"nim:'block'"),('PERM','nim:1'),
                  ('Simulationslegende',"nim:'Nimacimab'"),('Formregel','rim|mon|nim')]:
    if anker not in T: F.append('%s fehlt (%s)'%(was,anker))
# 6. Querverweis aus Monlunabant
j=T.find("{id:'mon',group:")
d=0;k2=j
while True:
    if T[k2]=='{': d+=1
    elif T[k2]=='}':
        d-=1
        if d==0: break
    k2+=1
if 'data-sub="nim"' not in T[j:k2+1]:
    F.append('Monlunabant verweist nicht auf die Nimacimab-Karte')
# Belegstufe: NICHT "am Menschen gescheitert" - die Studie laeuft
ev=re.search(r"obasisEv:'(\w)'",O)
if ev and ev.group(1)=='x':
    F.append('obasisEv steht auf "x" (am Menschen gescheitert) - die Studie laeuft aber noch')
# Inhalt: die magere Beleglage muss dastehen
if 'mager' not in O: F.append('Die duenne Beleglage ist nicht als solche benannt')
if 'keine einzige Arbeit' not in O and 'keine Arbeit' not in O:
    F.append('Dass es keine Primaerpublikation gibt, steht nicht da')
if '[[42618986]]' not in O: F.append('Der einzige Beleg fehlt')
if 'nicht widerlegen' not in O and 'nicht beantworten' not in O:
    F.append('Dass die laufende Studie das Psyche-Problem nicht beantworten kann, fehlt')
if 'Cannabis konsumiert' not in O: F.append('Der Cannabis-Ausschluss des Pruefplans fehlt')
# keine Dosisangaben
if re.search(r'\d+\s*mg\b',O): F.append('Dosisangabe auf der Karte')
# Register statt erfundener Quelle
if 'ClinicalTrials.gov' not in O: F.append('Die Registerangabe fehlt')
print('FEHLER' if F else 'OK','Nimacimab-Karte vollstaendig (%d Zeichen, %d Organfelder)'%(len(O),len(felder)))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
