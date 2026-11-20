# -*- coding: utf-8 -*-
"""Rueckenmark: Die Unterscheidung Schmerzstaerke/Unangenehmheit muss da sein,
und die Tafel darf "daempft auf dem Weg" nicht als am Menschen belegt ausgeben.
Faellt gegen vor-rueck.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
m=re.search(r"spinal:\{name:'Rückenmark'.*?a:'\w+'\}",T,re.S)
if not m: print('FEHLER: spinal-Eintrag nicht gefunden'); sys.exit(1)
H=m.group(0)
for pm in ['30422266','37648266']:
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    if '[[%s]]'%pm not in H: F.append('Beleg %s nicht an der Rueckenmark-Tafel'%pm)
# Der Kernbefund: Staerke nicht gesenkt, Unangenehmheit schon
if 'unangenehm' not in H: F.append('Die Unangenehmheit fehlt')
if not re.search(r'(Stärke des Schmerzes senkten sie dagegen nicht|Stärke.{0,40}nicht)',H):
    F.append('Dass die Schmerzstaerke NICHT gesenkt wurde, fehlt')
if '442' not in H: F.append('Die Teilnehmerzahl der Meta-Analyse fehlt')
# Die Gegenseite muss auch da sein
if '30 Prozent' not in H: F.append('Die Schmerzminderung bei chronisch Schmerzkranken fehlt')
if 'Belastung' not in H: F.append('Die seelische Belastung als Kehrseite fehlt')
# Die Tafel darf die Tierkenntnis nicht als Menschenkenntnis ausgeben
if 'am Tier' not in H: F.append('Dass die Daempfung am Tier gezeigt ist, steht nicht da')
if 'nicht entschieden' not in H and 'keinem Ort zuordnen' not in H:
    F.append('Dass der Ort der Wirkung beim Menschen offen ist, steht nicht da')
# keine Dosisangabe
if re.search(r'\d+\s*(mg|µg|mikrogramm)\b',H,re.I): F.append('Dosisangabe in der Tafel')
print('FEHLER' if F else 'OK','Rueckenmark-Tafel, %d Zeichen'%len(H))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
