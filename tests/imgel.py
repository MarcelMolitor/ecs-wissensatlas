# -*- coding: utf-8 -*-
"""Immunsystem und Gelenke: "gut belegt" muss auf mehr als zwei Belegen ruhen,
und die Einschraenkungen muessen dastehen - beim Immunsystem, dass die
Rangfolge fuer RUHENDE Zellen gilt; beim Gelenk, dass die Wirkung in einer
Gegenprobe NICHT ueber CB1/CB2 lief.
Faellt gegen vor-imgel.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
I=re.search(r"immune:\{name:'Immunsystem'.*?a:'\w+'\}",T,re.S)
G=re.search(r"gelenk:\{name:'Gelenke'.*?a:'\w+'\}",T,re.S)
if not I or not G: print('FEHLER: Tafel nicht gefunden'); sys.exit(1)
I=I.group(0); G=G.group(0)
# Mindestens drei Belege, wenn die Tafel "gut belegt" sagt
for k,H,mind in [('Immunsystem',I,3),('Gelenke',G,3)]:
    if re.search(r"ev:'g'",H):
        pm=set(re.findall(r'\[\[(\d+)\]\]',H))
        if len(pm)<mind: F.append('%s sagt "gut belegt", ruht aber nur auf %d Belegen'%(k,len(pm)))
for pm in ['11448490']:
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    if '[[%s]]'%pm not in I: F.append('Beleg %s nicht an der Immun-Tafel'%pm)
for pm in ['24440992','18799087']:
    if "['%s',"%pm not in T: F.append('Beleg %s fehlt im Verzeichnis'%pm)
    if '[[%s]]'%pm not in G: F.append('Beleg %s nicht an der Gelenk-Tafel'%pm)
# Einschraenkung Immunsystem: Rangfolge gilt fuer ruhende Zellen
if 'ruhende' not in I: F.append('Die Einschraenkung (Rangfolge gilt fuer ruhende Zellen) fehlt')
if 'nicht fest' not in I and 'kein fester Wert' not in I: F.append('Dass die CB2-Menge nicht festliegt, fehlt')
# Einschraenkung Gelenk: die Blocker blockierten nicht
if 'Blocker' not in G: F.append('Die Gegenprobe mit den Blockern fehlt an der Gelenk-Tafel')
if 'nicht über CB1' not in G: F.append('Dass die Wirkung nicht ueber CB1/CB2 lief, ist nicht benannt')
if 'data-organ="pankreas"' not in G: F.append('Der Querverweis auf den gleichen Befund an der Bauchspeicheldruese fehlt')
print('FEHLER' if F else 'OK','Immun %d / Gelenk %d Zeichen'%(len(I),len(G)))
for f in F: print(' -',f)
sys.exit(1 if F else 0)
