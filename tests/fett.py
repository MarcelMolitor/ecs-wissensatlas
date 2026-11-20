# -*- coding: utf-8 -*-
"""Fettgewebe: Die Tafel muss tragen, worauf die Rimonabant-Geschichte gebaut
war - und darf die Dichtestufe nicht ohne Messung anheben.
Faellt gegen vor-fett.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
m=re.search(r"fat:\{name:'Fettgewebe'.*?a:'\w+'\}",T,re.S)
if not m: print('FEHLER: fat-Eintrag nicht gefunden'); sys.exit(1)
H=m.group(0)
for pm in ['17284627','16684820','22087859','16570103']:
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    if '[[%s]]'%pm not in H: F.append('Beleg %s nicht an der Fett-Tafel'%pm)
# Dichtestufe: ohne eigene Dichtemessung darf sie nicht ueber 1 stehen
d=re.search(r"fat:\{name:'Fettgewebe',rec:'[^']*',d:(\d)",H)
if d and int(d.group(1))>1:
    F.append('Dichtestufe %s, aber eine Dichtemessung im Fettgewebe liegt nicht vor'%d.group(1))
# Der eigentliche Fund muss drinstehen: Rezeptor und Botenstoff gehen auseinander
if 'genauso aktiv' not in H: F.append('Der Negativbefund am Menschen (CB1-Gen gleich aktiv) fehlt')
if not re.search(r'(Botschaften|Endocannabinoide dagegen)',H): F.append('Die Gegenueberstellung Rezeptor/Botenstoff fehlt')
if '96' not in H or '82' not in H: F.append('Die Probenzahlen (96, 82) fehlen')
# Herkunft der Idee
if 'ohne CB1' not in H and 'CB1-freie' not in H: F.append('Woher die Idee kam (Maeuse ohne CB1) fehlt')
# Zellversuch muss als solcher benannt sein
if 'Zellversuch' not in H: F.append('Die Rimonabant-Befunde an Fettzellen sind nicht als Zellversuch gekennzeichnet')
# keine Ueberhoehung
for b in ['beweist','ist bewiesen','eindeutig belegt']:
    if b in H: F.append('Ueberhoehung: "%s"'%b)
print('FEHLER' if F else 'OK','Fett-Tafel, %d Zeichen'%len(H))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
