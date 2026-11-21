# -*- coding: utf-8 -*-
"""Prueft die ANORDNUNG der Hirnteile zueinander.

WARUM ES DIESEN TEST GIBT: Am 21.11.2026 fragte Marcel, ob die Anordnung jetzt
stimme. Ich hatte an diesem Tag zwei Fehler darin behoben - aber nur die zwei,
die mir aufgefallen WAREN. Eine Zeichnung anzuschauen und "sieht richtig aus"
zu sagen, ist keine Pruefung; und ich hatte am selben Tag dreimal etwas ueber
diese Karte behauptet, das sich beim Nachmessen als falsch erwies.

Die beiden Fehler, die es gab:
 - Das Mittelhirn stand auf dem Kopf: Substantia nigra bei y=204, Hoehlengrau
   bei y=222, also das Hoehlengrau UNTER beiden, auf Hoehe der Bruecke.
   Dorsoventral gehoert es umgekehrt.
 - Die Inselrinde lag bei cx=247 HINTER dem Thalamus (cx=202). Sie gehoert
   vorn-unten in die seitliche Hirnfurche.

WIE HIER GEPRUEFT WIRD: In dieser Seitenansicht ist kleineres x weiter vorn und
kleineres y weiter oben. Jede Zeile in REGELN ist eine anatomische Behauptung
in genau dieser Sprache. Geprueft wird der Punkt, auf den die
Beschriftungslinie zeigt (ax/ay) - das ist der Punkt, den die Karte selbst als
"hier ist diese Region" ausgibt.

NACHGEWIESEN WIRKSAM: Gegen die Fassung von vor der Korrektur melden diese
Regeln vier Verletzungen - beide Fehler, jeder aus zwei Richtungen. Ein Test,
der nie rot war, ist nicht bewiesen.

WAS DIESER TEST NICHT KANN: Er prueft Lagebeziehungen, keine Entfernungen und
keine Form. Dass ein Teil in der richtigen Richtung vom anderen liegt, heisst
nicht, dass es gut aussieht. Die Pruefung, dass die Grosshirnregionen im
Umriss liegen, steht in hirnteile.py.
"""
import io
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'

S = io.open(QUELLE, encoding='utf-8').read()
i = S.find('const BRAIN')
if i < 0:
    print('FEHLT: const BRAIN nicht gefunden')
    sys.exit(1)
blk = S[i:S.find('\n};', i)]

P, N = {}, {}
for m in re.finditer(r'^ ([a-z]+):\{', blk, re.M):
    k = m.group(1)
    seg = blk[m.start():blk.find('},\n ', m.start())]
    ax = re.search(r'\bax:(-?[\d.]+)', seg)
    ay = re.search(r'\bay:(-?[\d.]+)', seg)
    nm = re.search(r"name:'([^']*)'", seg)
    if not (ax and ay and nm):
        print('FEHLT: %s ohne ax/ay/name' % k)
        sys.exit(1)
    P[k] = (float(ax.group(1)), float(ay.group(1)))
    N[k] = nm.group(1)

VORN = lambda a, b: P[a][0] < P[b][0]
OBEN = lambda a, b: P[a][1] < P[b][1]

REGELN = [
    # --- vorn/hinten ---------------------------------------------------------
    (VORN, 'prefrontal', 'striatum',     'Stirnhirn liegt vor den Basalganglien'),
    (VORN, 'striatum', 'thalamus',       'Basalganglien liegen vor dem Thalamus'),
    (VORN, 'thalamus', 'cerebellum',     'Thalamus liegt vor dem Kleinhirn'),
    (VORN, 'olf', 'amygdala',            'Riechkolben liegt vor der Amygdala'),
    (VORN, 'accumbens', 'striatum',      'Nucleus accumbens liegt vor dem Rest der Basalganglien'),
    (VORN, 'striatum', 'pallidum',       'Putamen-Seite liegt vor dem Globus pallidus'),
    (VORN, 'insula', 'thalamus',         'Inselrinde liegt vor dem Thalamus'),
    (VORN, 'hypothalamus', 'thalamus',   'Hypothalamus liegt vor dem Thalamus'),
    (VORN, 'amygdala', 'hippocampus',    'Amygdala liegt vor dem Hippocampus'),
    (VORN, 'amygdala', 'entorhinal',     'Amygdala liegt vor der Entorhinalrinde'),
    (VORN, 'entorhinal', 'hippocampus',  'Entorhinalrinde liegt vor dem Hippocampus'),
    (VORN, 'brainstem', 'cerebellum',    'Hirnstamm liegt vor dem Kleinhirn'),
    (VORN, 'nigra', 'vta',               'Substantia nigra liegt vor dem Tegmentum'),
    (VORN, 'vta', 'pag',                 'Tegmentum liegt vor dem Hoehlengrau'),
    # --- oben/unten ----------------------------------------------------------
    (OBEN, 'cingulate', 'thalamus',      'Gyrus cinguli liegt ueber dem Thalamus'),
    (OBEN, 'cortex', 'thalamus',         'Grosshirnrinde liegt ueber dem Thalamus'),
    (OBEN, 'striatum', 'accumbens',      'Nucleus accumbens liegt unter den Basalganglien'),
    (OBEN, 'striatum', 'pallidum',       'Globus pallidus liegt unter dem oberen Striatum'),
    (OBEN, 'thalamus', 'hypothalamus',   'Hypothalamus liegt unter dem Thalamus'),
    (OBEN, 'striatum', 'insula',         'Inselrinde liegt unter den Basalganglien'),
    (OBEN, 'insula', 'amygdala',         'Amygdala liegt unter der Inselrinde'),
    (OBEN, 'prefrontal', 'olf',          'Riechkolben liegt unter dem Stirnhirn'),
    (OBEN, 'thalamus', 'hippocampus',    'Hippocampus liegt unter dem Thalamus'),
    (OBEN, 'hippocampus', 'entorhinal',  'Entorhinalrinde liegt unter dem Hippocampus'),
    (OBEN, 'amygdala', 'entorhinal',     'Entorhinalrinde liegt unter der Amygdala'),
    (OBEN, 'hypothalamus', 'pag',        'Mittelhirn liegt unter dem Hypothalamus'),
    (OBEN, 'pag', 'vta',                 'Tegmentum liegt unter dem Hoehlengrau'),
    (OBEN, 'vta', 'nigra',               'Substantia nigra liegt unter dem Tegmentum'),
    (OBEN, 'nigra', 'brech',             'Brechzentrum liegt unter dem Mittelhirn'),
    (OBEN, 'cerebellum', 'brainstem',    'unteres Ende des Hirnstamms liegt unter dem Kleinhirn'),
    (OBEN, 'thalamus', 'brech',          'Brechzentrum liegt unter dem Thalamus'),
]

pr = []
for f, a, b, satz in REGELN:
    if a not in P or b not in P:
        pr.append('Regel nennt unbekannte Region: %s / %s' % (a, b))
        continue
    if not f(a, b):
        pr.append('%s -- %s (%g,%g) / %s (%g,%g)'
                  % (satz, N[a], P[a][0], P[a][1], N[b], P[b][0], P[b][1]))

# Jede Region muss in mindestens einer Regel vorkommen, sonst ist sie
# ungeprueft und niemand merkt es.
drin = set()
for f, a, b, s in REGELN:
    drin.add(a)
    drin.add(b)
offen = sorted(set(P) - drin)
if offen:
    pr.append('in keiner Regel geprueft: %s' % ', '.join(N[k] for k in offen))

print('Hirnteile: %d | Lagebeziehungen: %d' % (len(P), len(REGELN)))
print('Probleme:', pr or 'keine')
if pr:
    sys.exit(1)
