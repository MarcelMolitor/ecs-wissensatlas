# -*- coding: utf-8 -*-
"""MESSUNG, keine Dauerpruefung: Wie viele Absaetze in KARTEN tragen die Stufe
'gut belegt', obwohl die Belege im selben Absatz nur aus Labor, Tier oder
Grundlagen stammen? t/evtyp.py prueft diese Regel nur bei Stoffen (obasisEv) -
Kartenabsaetze fallen durch das Raster."""
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

# Jeden <p>...</p> mit ev('g') einsammeln, samt der PMIDs darin.
treffer = []
for m in re.finditer(r"<p[^>]*>(.{0,4000}?)</p>", s, re.S):
    blk = m.group(1)
    if "ev('g')" not in blk:
        continue
    pm = re.findall(r'\[\[(\d+)\]\]', blk)
    arten = {KEY.get(p) for p in pm if p in KEY}
    if pm and arten and arten <= NUR_LABOR:
        k = s.rfind('<article class="card" id="', 0, m.start())
        cid = re.match(r'<article class="card" id="([a-z0-9-]+)"', s[k:k + 60])
        txt = re.sub(r'<[^>]+>', '', blk)
        txt = re.sub(r'\$\{[^}]*\}', '', txt)[:110]
        treffer.append((cid.group(1) if cid else '?', sorted(arten), pm, txt.strip()))

print('Absaetze mit ev(g):', sum(1 for _ in re.finditer(r"ev\('g'\)", s)))
print('davon nur mit Labor-/Tierbelegen:', len(treffer))
for t in treffer:
    print('  [%s] %s  %s' % (t[0], '/'.join(x or '?' for x in t[1]), t[2]))
    print('      ', t[3])
