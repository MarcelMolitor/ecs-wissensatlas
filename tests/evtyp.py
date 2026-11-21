# -*- coding: utf-8 -*-
"""Prueft zwei Dinge, die die bisherigen Skripte nicht abdecken:
   1. Stoffe mit der Belegstufe 'gut belegt', deren obasis nur Tier- oder
      Zellbelege nennt - also eine Stufe, die die Belegart nicht traegt.
   2. Stoff-Status ohne jeden Beleg.
   Arbeitet am Quelltext, weil die Belegart nur im KEY-Verzeichnis steht."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import re, sys
P = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'
s = open(P).read()
i = s.index('const KEY = ['); j = s.index('\n];', i)
KEY = {}
for m in re.finditer(r"\[\s*'(\d+)'\s*,\s*(\d{4})\s*,(?:\s*'(?:[^'\\]|\\.)*'\s*,){4}\s*'((?:[^'\\]|\\.)*)'", s[i:j]):
    KEY[m.group(1)] = m.group(3)
NUR_LABOR = {'Tierstudie', 'Zellversuch', 'Grundlagen', 'Modellrechnung'}

# 21.11.2026: Beim Nachzaehlen der Quellen fuer das README fiel auf, dass es 624
# KEY-Eintraege, aber nur 623 verschiedene PMIDs gab: Agarwal u. a. 2007
# (17558404) stand zweimal, mit zwei Kernaussagen und demselben DOI. Die
# Zuordnung KEY oben ist ein Woerterbuch und verliert solche Doppel still - der
# zweite Eintrag ueberschreibt den ersten, und niemand merkt es. Gezaehlt wird
# darum auf der Liste, nicht im Woerterbuch.
# Warum das zaehlt: cite() schlaegt die Nummer in einer Zuordnung PMID->Nummer
# nach, die Quellenliste berechnet sie mit findIndex. Bei einem Doppel laufen
# die beiden auseinander, und dieselbe Arbeit belegt zwei Nummern.
from collections import Counter as _C
_alle = [_m.group(1) for _m in re.finditer(r"\['(\d{6,8})',\d{4},", s[i:j])]
_dop = sorted(p for p, n in _C(_alle).items() if n > 1)
if _dop:
    print('FEHLER: PMID doppelt im Quellenverzeichnis:', _dop)
print('KEY-Eintraege:', len(_alle), '| verschiedene PMIDs:', len(set(_alle)))

t1 = t2 = 0
for m in re.finditer(r"\{id:'([a-z0-9]+)',group:'([^']+)',name:'([^']+)'", s):
    nxt = s.find("\n {id:'", m.start())
    blk = s[m.start(): nxt if nxt > 0 else m.start() + 7000]
    ev = re.search(r"obasisEv:'(\w)'", blk)
    ob = re.search(r"obasis:'((?:[^'\\]|\\.)*)'", blk)
    st = re.search(r"status:'((?:[^'\\]|\\.)*)'", blk)
    if st and not re.search(r'\[\[\d+\]\]', st.group(1)):
        print('STATUS OHNE BELEG:', m.group(3)); t2 += 1
    if ev and ob and ev.group(1) == 'g':
        pm = re.findall(r'\[\[(\d+)\]\]', ob.group(1))
        arten = {KEY.get(p) for p in pm if p in KEY}
        if pm and arten and arten <= NUR_LABOR:
            print('STUFE g, NUR LABORBELEGE:', m.group(3), '->', arten); t1 += 1
print('KEY-Belege mit Typ:', len(KEY))
print('Stufe g ohne Humanbeleg:', t1)
print('Status ohne Beleg:', t2)
