# -*- coding: utf-8 -*-
"""Renin-Angiotensin in den Nachbarsystemen.

Der Reiter hat eine offengelegte Auswahlregel: Platz nur mit einer Messung am
Menschen - oder, wie bei Histamin, mit einem sauberen Mechanismus MIT
GEGENPROBE und ausdruecklichem Hinweis darauf. Angiotensin ist ueber die
zweite Tuer aufgenommen. Dieser Test haelt fest, dass es dort bleibt, wo es
nach der Regel hingehoert, und nicht stillschweigend aufsteigt.

Besonders bewacht: Die Moeglichkeit einer Wechselwirkung zwischen CBD und
Telmisartan ist eine VERMUTUNG aus einer Uebersicht. Sie darf nicht in den
Wechselwirkungs-Reiter wandern, wo sie neben geprueften Angaben staende und
Menschen beunruhigen wuerde, die Blutdruckmittel nehmen.
Faellt gegen vor-angio.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
N=re.search(r"\{id:'nachbarn'.*?html:\(\) => `(.*?)`\},\n",T,re.S)
if not N: print('FEHLER: Reiter nachbarn nicht gefunden'); sys.exit(1)
N=N.group(1)
for pm in ['35563848','25422468','35683028']:
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    if '[[%s]]'%pm not in N: F.append('Beleg %s nicht im Reiter Nachbarsysteme'%pm)
# Eintrag vorhanden und in der UNTEREN Liste
e=re.search(r"\['Renin-Angiotensin[^']*','([^']*)','(.*?)'\],",N,re.S)
if not e: F.append('Der Eintrag Renin-Angiotensin fehlt')
else:
    stufe,txt=e.group(1),e.group(2)
    unten=N.find('Berührungspunkte, zu denen es weniger gibt')
    if unten<0 or N.find("['Renin-Angiotensin")<unten:
        F.append('Der Eintrag steht nicht in der unteren Liste')
    if 'Mensch' in stufe and 'Tier' not in stufe:
        F.append('Die Stufe behauptet Menschendaten: "%s"'%stufe)
    # die drei Gegenproben sind der Grund fuer die Aufnahme
    if 'drei' not in txt: F.append('Die drei Gegenproben sind nicht benannt')
    for g in ['AT1','AT2','Mas']:
        if g not in txt: F.append('Gegenprobe %s fehlt'%g)
    # der ehrliche Hinweis
    if 'Was fehlt' not in txt and 'Messung am Menschen' not in txt:
        F.append('Der Hinweis auf die fehlende Messung am Menschen fehlt')
    if 'menschlichen' not in txt: F.append('Der Zellbezug zum Menschen fehlt')
    if 'data-organ="niere"' not in txt: F.append('Querverweis auf die Nieren-Tafel fehlt')
    # Telmisartan muss als Vermutung gekennzeichnet sein
    if 'Telmisartan' in txt:
        if 'Gemessen ist das nicht' not in txt and 'Vermutung' not in txt:
            F.append('Die Telmisartan-Moeglichkeit ist nicht als unbelegt gekennzeichnet')
# Telmisartan darf NICHT im Wechselwirkungs-Reiter stehen
W=re.search(r"\{id:'wechsel'.*?html:(.*?)\},\n\s*\{id:'",T,re.S)
if W and 'Telmisartan' in W.group(1):
    F.append('Die unbelegte Telmisartan-Vermutung ist in den Wechselwirkungs-Reiter gewandert')
print('FEHLER' if F else 'OK','Renin-Angiotensin steht in der unteren Liste, mit Gegenproben und Einschraenkung')
for f in F: print(' -',f)
sys.exit(1 if F else 0)
