# -*- coding: utf-8 -*-
"""Der Satz zur Fahrtuechtigkeit muss die Einschraenkungen SELBST tragen,
nicht nur der Verzeichniseintrag dahinter.

WARUM: Aus diesem Satz leitet jemand ab, ob er faehrt. Wer nur liest, dass
die Beeintraechtigung "eher 0,5 als 0,2 Promille" entspricht, nimmt etwas
Falsches mit, solange nicht danebensteht, dass sie nach gut vier Stunden
nicht mehr nachweisbar war und dass CBD-reiches Cannabis sich gar nicht von
Placebo unterschied. Beides steht in derselben Studie.
Faellt gegen vor-fahren.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
m=re.search(r"cite\('0,2 Promille entsprechen in diesem Test.*?\[\[33258890\]\]'\)",T,re.S)
if not m:
    print('FEHLER: Fahrtuechtigkeits-Satz nicht gefunden'); sys.exit(1)
Satz=m.group(0)
if '0,5 als 0,2 Promille' in Satz:
    if '240' not in Satz: F.append('Der Satz nennt den Alkoholvergleich, aber nicht das Abklingen nach 240 bis 300 Minuten')
    if 'CBD-reiches' not in Satz: F.append('Der Satz nennt nicht, dass CBD-reiches Cannabis sich nicht von Placebo unterschied')
    if 'vorübergehend' not in Satz and 'nicht mehr sicher' not in Satz:
        F.append('Die Einordnung "deutlich, aber voruebergehend" fehlt')
# Der Verzeichniseintrag muss beides weiterhin tragen
e=re.search(r"\['33258890',.*?\],\n",T,re.S)
if e:
    for teil in ['240 bis 300','CBD-reiches','8,5 Prozent']:
        if teil not in e.group(0): F.append('Verzeichniseintrag 33258890 ohne "%s"'%teil)
# Keine Dosisangabe im Lesersatz (THC/CBD-Mengen der Studie)
if re.search(r'\d+,\d+\s*mg|\d+\s*mg',Satz): F.append('Dosisangabe im Lesersatz')
print('FEHLER' if F else 'OK','Fahrtuechtigkeits-Satz, %d Zeichen'%len(Satz))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
