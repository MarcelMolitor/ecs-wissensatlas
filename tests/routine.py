# -*- coding: utf-8 -*-
"""Das Fazit aus 41856154 muss wiedergeben, was dort steht: ROUTINEMAESSIGER
Einsatz, und zwar bei psychischen UND bei Suchterkrankungen.

ANLASS: Auf der Seite stand "der verbreitete Einsatz ... gegen psychische
Erkrankungen". "Verbreitet" sagt, wie haeufig etwas vorkommt; die Autoren
sagen, ob es Standardvorgehen sein soll. Und die Suchterkrankungen fehlten -
ausgerechnet der Bereich, in dem dieselbe Arbeit einen Nutzen fand.
Faellt gegen vor-routine.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
m=re.search(r"Das Fazit der Autoren.{0,700}?\[\[41856154\]\]",T,re.S)
if not m:
    print('FEHLER: Fazit-Satz zu 41856154 nicht gefunden'); sys.exit(1)
Z=m.group(0)
if 'verbreitete Einsatz' in Z: F.append('"verbreiteter Einsatz" statt "routinemaessiger Einsatz"')
if 'routinemäßig' not in Z: F.append('Das Wort "routinemaessig" fehlt')
if 'Sucht' not in Z: F.append('Die Suchterkrankungen fehlen im Geltungsbereich')
# Das Fazit darf nicht strenger wirken als es ist
if 'Cannabisentzug' not in Z and 'durchaus Wirkungen' not in Z:
    F.append('Die gefundenen Wirkungen derselben Arbeit fehlen als Gegengewicht')
if 'Belegqualität' not in Z: F.append('Die niedrige Belegqualitaet fehlt')
print('FEHLER' if F else 'OK','Fazit 41856154 wortgetreu (%d Zeichen)'%len(Z))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
