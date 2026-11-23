# -*- coding: utf-8 -*-
"""Haelt die Verneinungen fest, die ein ganzes Forschungsprogramm bestreiten.

WARUM ES DIESEN TEST GIBT: Die Seite sagt an vielen Stellen "dazu gibt es
keine Studie". Das ist ihre fragilste Klasse von Aussagen - sie wird falsch,
ohne dass sich auf der Seite etwas aendert. Zweimal ist das binnen einer Woche
passiert:

  cbn.skin sagte "zur Wirkung auf die Haut gibt es keine Studie". Es gab eine
  abgeschlossene Phase 2 (NCT04908215).

  Rimonabant stand als abgeschlossene Geschichte da. Es laufen vier Studien.

Beide wurden von Hand gefunden, beide zufaellig. Am 23.11.2026 sind die drei
Saetze, die ein ganzes Programm bestreiten, nachgesehen und mit Datum versehen
worden. Dieser Test haelt fest, dass sie ihr Datum und ihre Registerbelege
behalten - und dass die Abfragen, mit denen man sie prueft, auf der Seite
stehen.

WAS DIESER TEST NICHT KANN: nachsehen. Die Suite laeuft ohne Netz, und eine
Registerabfrage ergibt nicht bei jedem Lauf dasselbe. Geprueft wird also die
FORM: Steht ein Datum dabei? Ist die Registernummer genannt? Hat der Stoff eine
Abfrage? Das eigentliche Nachsehen bleibt Handarbeit - die Arbeitsliste dafuer
liegt in scratchpad/verneinungen.py und sortiert nach Dringlichkeit.

WER EINE DIESER AUSSAGEN AENDERT, muss das Datum mitaendern. Genau das soll
dieser Test erzwingen: Ein Stempel ist eine Behauptung darueber, wann jemand
geschaut hat.
"""
import io
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'
S = io.open(QUELLE, encoding='utf-8').read()

# Das Kopfprotokoll zitiert eigene Fehler und dabei Saetze der Seite.
UMFANG = 200000
I = S[UMFANG:]

pr = []

# --- 1) Die drei Verneinungen: Aussage, Beleg, Datum ----------------------
# Form: (Name, Kernsatz, Dinge die im Umfeld stehen muessen, Umfeldgroesse)
FEST = [
    ('THCP', 'keine einzige Studie am Menschen',
     ['null Einträge', 'ClinicalTrials.gov', 'abgefragt am 23.11.2026'], 400),
    ('CBC', 'Es gibt keine klinischen Studien</b>',
     ['NCT07087938', 'zurückgezogen', 'abgefragt am 23.11.2026',
      'complete blood count'], 1500),
    ('CBN-Abwehr', 'Am Menschen selbst ist zur Abwehr nichts gemessen',
     ['elf Einträge', 'Um die Abwehr geht es in keinem',
      'abgefragt am 23.11.2026'], 700),
]
for name, kern, pflicht, weite in FEST:
    i = I.find(kern)
    if i < 0:
        pr.append('%s: die Aussage selbst ist weg ("%s")' % (name, kern[:40]))
        continue
    umfeld = I[max(0, i - weite):i + weite]
    for p in pflicht:
        if p not in umfeld:
            pr.append('%s: "%s" fehlt im Umfeld der Aussage' % (name, p))

# --- 2) Die Abfragen, mit denen man sie nachprueft ------------------------
# Ohne Abfrage ist eine Verneinung nicht nachpruefbar - genau daran lag es
# bei CBC und THCP, bis zum 23.11.2026.
for stoff, begriff in [('cbc', 'cannabichromene'),
                       ('thcp', 'tetrahydrocannabiphorol'),
                       ('cbn', 'cannabinol')]:
    m = re.search(r"\b%s:\{pm:'((?:[^'\\]|\\.)*)'"
                  r"(?:,\s*ct:\{intervention:'((?:[^'\\]|\\.)*)'\})?\}" % stoff, S)
    if not m:
        pr.append('%s: keine Abfrage auf der Seite' % stoff)
        continue
    if begriff not in (m.group(1) or ''):
        pr.append('%s: die PubMed-Abfrage nennt "%s" nicht' % (stoff, begriff))
    if not m.group(2):
        pr.append('%s: keine Registerabfrage' % stoff)
    elif begriff not in m.group(2):
        pr.append('%s: die Registerabfrage nennt "%s" nicht' % (stoff, begriff))

# --- 3) Kein Stempel ohne Nachsehen --------------------------------------
# Drei Aussagen wurden am 23.11. geprueft. Wer einen vierten Stempel von
# diesem Tag setzt, ohne nachgesehen zu haben, soll hier anschlagen.
heute = I.count('abgefragt am 23.11.2026')
if heute != 3:
    pr.append('Stempel vom 23.11.2026: %d statt 3 – wurde wirklich nachgesehen?'
              % heute)

# --- 4) Die alten Verneinungen, die schon einmal versagt haben -----------
# cbn.skin darf nie wieder "keine Studie" sagen: Es gibt eine.
i = I.find('NCT04908215')
if i < 0:
    pr.append('cbn.skin: die Studie NCT04908215 ist nicht mehr genannt')
else:
    umfeld = I[max(0, i - 900):i + 300]
    for schlecht in ['keine Studie', 'nie geprüft', 'nicht geprüft']:
        if schlecht in umfeld:
            pr.append('cbn.skin: "%s" steht wieder neben einer Studie, die es gibt'
                      % schlecht)

print('Verneinungen mit Beleg und Datum geprüft: %d' % len(FEST))
print('Abfragen geprüft: 3 | Stempel vom 23.11.2026: %d' % heute)
print('Probleme:', pr or 'keine')
if pr:
    sys.exit(1)
