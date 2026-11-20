# -*- coding: utf-8 -*-
"""Die beiden Schmerz-Tafeln muessen verbunden bleiben.

ANLASS: Am 14.11. habe ich am Rueckenmark die Meta-Analyse 30422266
eingebaut (Unangenehmheit gesenkt, Staerke nicht) und dabei uebersehen, dass
die Gyrus-cinguli-Tafel seit Langem denselben Befund trug (23273106). Das ist
die Geschwister-Fehlerklasse: dieselbe Aussage an zwei Stellen, eine davon
auf neuem Stand, ohne dass die Seite es merkt.

DIESER TEST sorgt dafuer, dass genau das nicht wieder passiert - und dass
keine der beiden Tafeln den Befund kuenftig allein traegt:
1. Beide Tafeln nennen die Unterscheidung Staerke/Unangenehmheit.
2. Beide nennen BEIDE Belege - die Bildgebungsstudie und die Meta-Analyse.
3. Beide verweisen aufeinander.
4. Keine behauptet, der Ort der Wirkung sei geklaert."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
sp=re.search(r"spinal:\{name:'Rückenmark'.*?a:'\w+'\}",T,re.S)
ci=re.search(r"cingulate:\{name:'([^']+)'(.*?)\}(?=,\n|\n)",T,re.S)
if not sp or not ci:
    print('FEHLER: eine der beiden Tafeln nicht gefunden'); sys.exit(1)
SP=sp.group(0); CI=ci.group(2)
for name,H in [('Rückenmark',SP),('Gyrus cinguli',CI)]:
    for pm in ['23273106','30422266']:
        if '[[%s]]'%pm not in H: F.append('%s: Beleg %s fehlt'%(name,pm))
    if 'nicht' not in H or 'unangenehm' not in H.lower():
        F.append('%s: die Unterscheidung Staerke/Unangenehmheit fehlt'%name)
# gegenseitige Verweise
if 'data-region="cingulate"' not in SP: F.append('Rückenmark verweist nicht auf den Gyrus cinguli')
if 'data-organ="spinal"' not in CI: F.append('Gyrus cinguli verweist nicht auf das Rückenmark')
# keine Ueberhoehung des Ortes
for b in ['der Ort ist damit geklärt','entsteht im Gyrus cinguli','beweist, wo']:
    if b in SP or b in CI: F.append('Ueberhoehung: "%s"'%b)
if 'nicht entschieden' not in SP and 'keinem Ort zuordnen' not in SP:
    F.append('Das Rückenmark behauptet nicht mehr, dass der Ort offen ist')
# Die Einzelstudie darf nicht als alleiniger Traeger dastehen
if 'Einzelbefund' not in CI and 'nicht der Einzelbefund' not in CI and '442' not in CI:
    F.append('Gyrus cinguli ordnet die Einzelstudie nicht in die Meta-Analyse ein')
print('FEHLER' if F else 'OK','Schmerzpaar verbunden (Rückenmark %d / Gyrus cinguli %d Zeichen)'%(len(SP),len(CI)))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
