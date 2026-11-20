# -*- coding: utf-8 -*-
"""Die Herz-Tafel muss beide Richtungen tragen - und darf die
Kokain-Arbeit nicht als Entwarnung lesen lassen.

Dieser Test waere gegen vor-herz.html durchgefallen: dort fehlte die Frage
nach Herzinfarkt und Schlaganfall vollstaendig.

Gepruefte Zusagen:
1. Beide Richtungen stehen da: das signifikante Sammelmass UND dass die
   Einzelendpunkte es nicht waren.
2. Die Gegenprobe an Menschen mit bestehender Herzkrankheit steht da.
3. Die Kokain-Arbeit wird NIE ohne den Hinweis genannt, dass sie zwei
   Konsumgruppen vergleicht und nicht gegen Nichtkonsum.
4. Keine Ueberhoehung: Die Tafel behauptet nicht, der Zusammenhang sei
   belegt - und die Belegstufe steht nicht auf "gut".
5. Alle vier Belege sind im Verzeichnis und am Herzen verlinkt."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
m=re.search(r"heart:\{.*?a:'\w+'\}",T,re.S)
if not m: print('FEHLER: Herz-Eintrag nicht gefunden'); sys.exit(1)
H=m.group(0)
for pm in ['39800612','40686207','32752884','41638249']:
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    if '[[%s]]'%pm not in H: F.append('Beleg %s nicht an der Herz-Tafel'%pm)
# 1 beide Richtungen
if not re.search(r'nicht statistisch sicher',H): F.append('Die nicht signifikanten Einzelendpunkte fehlen')
if not re.search(r'(zusammenfass|zusammengefasst)',H): F.append('Das zusammengefasste Mass fehlt')
if 'Herzinfarkt' not in H or 'Schlaganfall' not in H: F.append('Herzinfarkt/Schlaganfall fehlen')
# 2 Gegenprobe
if '4285' not in H or 'koronare' not in H: F.append('Gegenprobe an Herzkranken fehlt')
if not re.search(r'kein Zusammenhang',H): F.append('Das Nullergebnis ist nicht benannt')
# 3 Kokain nur mit Einschraenkung
if 'Kokain' in H:
    if 'Nichtkonsum' not in H: F.append('Kokain-Vergleich ohne den Hinweis auf das fehlende Nichtkonsum-Vergleichsgruppe')
    if 'Entwarnung' not in H: F.append('Kokain-Vergleich nicht ausdruecklich als keine Entwarnung markiert')
# auch der Verzeichniseintrag selbst muss die Einschraenkung tragen
e=re.search(r"\['41638249',.*?\],\n",T,re.S)
if e and 'nicht Konsum mit Nichtkonsum' not in e.group(0) and 'nicht Cannabis mit Nichtkonsum' not in e.group(0):
    F.append('Verzeichniseintrag 41638249 ohne Hinweis auf die fehlende Nichtkonsum-Gruppe')
# 4 keine Ueberhoehung
if re.search(r"heart:\{[^}]*?ev:'g'",H): F.append("Belegstufe steht auf 'gut', obwohl die Kernfrage umstritten ist")
for b in ['Cannabis verursacht Herzinfarkt','erhöht das Herzinfarktrisiko','führt zu Herzinfarkten','ist belegt, dass Cannabis']:
    if b in H: F.append('Ueberhoehung: "%s"'%b)
print('FEHLER' if F else 'OK','Herz-Tafel, %d Zeichen'%len(H))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
