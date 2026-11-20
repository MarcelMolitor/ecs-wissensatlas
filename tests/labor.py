# -*- coding: utf-8 -*-
"""Das Wirkstoff-Labor nennt fuer jeden CB1-Weg einen echten Verwandten. Der
Weg 'peri' hat ZWEI - und ihr Unterschied ist der Lernwert dieses Reglers.

ANLASS: Nach dem Bau der Nimacimab-Karte nannte der peri-Weg weiter nur
Monlunabant. Ein Labor, das einen von zwei realen Vertretern verschweigt, ist
kein Lernmodell, sondern eine Luecke mit Erklaerung daneben.
Faellt gegen vor-labor.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
# Die Vorgabe muss es geben
if "['Nimacimab', 'CB1', {mode:'cb1', cb1how:'peri'" not in T:
    F.append('Nimacimab fehlt unter den Vorgaben "Wie ein echter Stoff"')
# Der peri-Zweig muss beide nennen und den Unterschied erklaeren
i=T.find("if (LAB.cb1how === 'peri')")
if i<0:
    F.append('Der peri-Zweig nennt weiter nur einen Verwandten')
else:
    Z=T[i:i+2000]
    for s,w in [("SUBLINK('mon'",'Verweis auf Monlunabant'),("SUBLINK('nim'",'Verweis auf Nimacimab'),
                ('zwei','die Zahl zwei'),('zu <i>groß</i>','die Molekuelgroesse als Grund'),
                ('soll','die Absicht bei Monlunabant'),('keine veröffentlichten Ergebnisse','der Preis bei Nimacimab')]:
        if s not in Z: F.append('peri-Zweig ohne %s'%w)
    # Der Zweig darf nicht behaupten, die Frage sei entschieden
    for b in ['ist damit gelöst','hat sich bewährt','ist der bessere']:
        if b in Z: F.append('Anmassung im peri-Zweig: "%s"'%b)
    if 'offen' not in Z: F.append('Dass offen ist, welche Loesung traegt, steht nicht da')
# Die vier Wege muessen alle noch einen Verwandten haben
for weg in ['block','peri','signal','nam']:
    if "%s:"%weg not in T: F.append('CB1-Weg %s verschwunden'%weg)
print('FEHLER' if F else 'OK','Labor: peri-Weg nennt beide Vertreter')
for f in F: print(' -',f)
sys.exit(1 if F else 0)
