# -*- coding: utf-8 -*-
"""Die Dichtestufe einer Organtafel darf ihrem eigenen Belegtext nicht
widersprechen.

WARUM ES DIESEN TEST GIBT: Am 14.11. fanden sich DREI Tafeln, deren Stufe
hoeher stand, als ihr eigener Text hergab - Fettgewebe stand auf "mittel" und
sagte selbst, die Rezeptordichte im Fettgewebe sei nie gemessen worden;
Rueckenmark stand auf "mittel" und sagte selbst, die Bindung dort sei im
Menschen "sehr gering". Das ist eine Fehlerklasse, nicht ein Einzelfall: Die
Stufe wird beim Anlegen gesetzt, der Text wird spaeter genauer - und niemand
geht zurueck und senkt die Stufe.

REGEL: Sagt der eigene Text der Tafel, dass dort wenig, sehr wenig oder
nichts nachgewiesen ist oder dass die Dichte nie gemessen wurde, dann darf die
Stufe hoechstens 1 ("gering") sein."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
DENS=['nicht nachgewiesen','gering','mittel','hoch']
# Phrasen, die eine niedrige oder fehlende Dichte behaupten
ARM=['sehr gering','nicht zu den dichten','nicht unter den CB1-reichen',
     'steht nicht unter den','nicht die Rezeptordichte','wenig CB1',
     'Wenige Bindungsstellen','nicht nachgewiesen','nie gemessen',
     'keine Dichtemessung','nicht gemessen worden']
org=re.findall(r"(\w+):\{name:'([^']+)'(.*?)a:'\w+'\}",T,re.S)
print('Organtafeln geprueft:',len(org))
for k,n,rest in org:
    d=re.search(r"\bd:(\d),",rest)
    if not d: continue
    d=int(d.group(1))
    txt=rest
    treffer=[p for p in ARM if p in txt]
    if treffer and d>1:
        F.append('%s (%s): Stufe %d ("%s"), aber der eigene Text sagt: %s'%(n,k,d,DENS[d],', '.join('„%s“'%t for t in treffer)))
# Gegenprobe: der Test muss ueberhaupt etwas sehen koennen
gesehen=[n for k,n,r in org if any(p in r for p in ARM)]
if not gesehen: F.append('Die Phrasenliste trifft keine einzige Tafel - der Test prueft nichts')
print('  Tafeln mit Aussage "wenig/nicht nachgewiesen":',len(gesehen))
print('FEHLER' if F else 'OK','keine Stufe widerspricht ihrem Belegtext')
for f in F: print(' -',f)
sys.exit(1 if F else 0)
