# -*- coding: utf-8 -*-
"""Leber, Niere, Bauchspeicheldruese.
LEBER: die drei Fettleber-Studien muessen in der Reihenfolge stehen, die den
Befund erklaert - der grosse Effekt aus Abrechnungsdaten, dann das Nichts aus
gemessenen Lebern. Der 52-Prozent-Befund darf NIE ohne diese Einordnung
dastehen.
PANKREAS: der Widerspruch zwischen den beiden Inselzell-Versuchen muss sichtbar
sein, samt dem Befund, dass die Blocker nicht blockierten.
NIERE: Humangewebe und Humangenetik muessen da sein.
Faellt gegen vor-drei.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
def tafel(k,name):
    m=re.search(r"%s:\{name:'%s'.*?a:'\w+'\}"%(k,name),T,re.S)
    return m.group(0) if m else ''
L=tafel('liver','Leber'); N=tafel('niere','Niere'); P=tafel('pankreas','Bauchspeicheldrüse')
for k,H in [('liver',L),('niere',N),('pankreas',P)]:
    if not H: F.append('Tafel %s nicht gefunden'%k)
# --- Leber
for pm in ['28441459','39286879','42115075']:
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    if '[[%s]]'%pm not in L: F.append('Beleg %s nicht an der Leber-Tafel'%pm)
if '52 Prozent' in L:
    if 'Abrechnungsdaten' not in L: F.append('Der 52-Prozent-Befund steht ohne den Hinweis auf Abrechnungsdaten')
    if 'Elastografie' not in L and 'gemessen' not in L: F.append('Die Gegenprobe mit gemessener Leber fehlt')
    # Reihenfolge: der grosse Effekt muss VOR seiner Entkraeftung stehen
    if L.index('52 Prozent') > L.index('Abrechnungsdaten'): F.append('Reihenfolge: die Einordnung steht vor dem Befund')
if 'UK-Biobank' not in L and 'Biobank' not in L: F.append('Die vorausschauende Kohorte fehlt an der Leber')
# --- Niere
for pm in ['21810593','36949158','29399721']:
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    if '[[%s]]'%pm not in N: F.append('Beleg %s nicht an der Nieren-Tafel'%pm)
if 'Nierenproben' not in N: F.append('Das Humangewebe fehlt an der Nieren-Tafel')
if 'genomweit' not in N: F.append('Die Humangenetik fehlt an der Nieren-Tafel')
if 'Typ 1' not in N: F.append('Die Einschraenkung (nur Typ-2-Diabetes) fehlt')
# --- Pankreas
if "['21564460'," not in T: F.append('Beleg 21564460 fehlt im Verzeichnis')
if '[[21564460]]' not in P: F.append('Beleg 21564460 nicht an der Pankreas-Tafel')
if '[[18092149]]' not in P: F.append('Der aeltere Inselzell-Beleg fehlt an der Pankreas-Tafel')
if 'widersprechen' not in P: F.append('Der Widerspruch der beiden Inselzell-Versuche ist nicht benannt')
if 'Blocker' not in P: F.append('Der Befund, dass die Blocker nicht blockierten, fehlt')
print('FEHLER' if F else 'OK','Leber %d / Niere %d / Pankreas %d Zeichen'%(len(L),len(N),len(P)))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
