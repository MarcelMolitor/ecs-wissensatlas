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
# Jeder Stempel vom 23.11.2026 muss zu einer Sache gehoeren, die an diesem Tag
# wirklich nachgesehen wurde. Darum keine nackte Zahl, sondern eine Liste: Wer
# einen Stempel setzt, traegt hier ein, WAS er nachgesehen hat. Sonst schlaegt
# der Test an - und genau das ist am 23.11. passiert, als die vier neuen
# CB2-Einsatzgebiete zwei weitere Stempel brachten.
NACHGESEHEN_23_11 = [
    'THCP im Studienregister: null Eintraege',
    'Cannabichromen im Studienregister: ein zurueckgezogener Eintrag',
    'Cannabinol im Studienregister: elf Eintraege, keiner zur Abwehr',
    'S-777469 bei Neurodermitis: zwei Studien, keine Ergebnisse',
    'KHK6188 bei Zoster-Neuralgie: eine Studie, keine Ergebnisse',
]
heute = I.count('abgefragt am 23.11.2026')
if heute != len(NACHGESEHEN_23_11):
    pr.append('Stempel vom 23.11.2026: %d, aber %d Dinge als nachgesehen '
              'eingetragen – wurde wirklich nachgesehen?'
              % (heute, len(NACHGESEHEN_23_11)))

# --- 3b) Die zwei Programme, die geprueft und nie berichtet wurden --------
# Diese Klasse ist das Gegenstueck zur Verneinung: Nicht "niemand hat
# geprueft", sondern "jemand hat geprueft, und niemand erfaehrt es". Sie darf
# nicht stillschweigend zu einem "gescheitert" werden.
# Geprueft wird der EINTRAG, nicht ein Zeichenfenster: Beim ersten Versuch
# nahm ich 1200 Zeichen um die Registernummer und erwischte damit das Wort
# "gescheitert" aus dem NACHBAREINTRAG (Reizdarm, der wirklich gescheitert
# ist). Ein gruener Test waere das nicht gewesen, aber ein falscher Alarm, und
# die kosten dasselbe Vertrauen.
def cb2_eintrag(key):
    m = re.search(r"\bCB2_USE\s*=", S[UMFANG:])
    if not m:
        return None
    a = UMFANG + m.start()
    j = S.find('{', a)
    tief, k = 0, j
    while k < len(S):
        if S[k] == '{':
            tief += 1
        elif S[k] == '}':
            tief -= 1
        if tief == 0:
            break
        k += 1
    for t in re.split(r"\n (?=\w+:)", S[j:k + 1]):
        if re.match(r"\{?\s*%s:" % key, t):
            return t
    return None

for name, key, nct, pflicht in [
        ('S-777469 / Neurodermitis', 'neuro', 'NCT00703573',
         ['keine Ergebnisse hinterlegt', '209']),
        ('KHK6188 / Zoster-Neuralgie', 'zoster', 'NCT01544296',
         ['null Treffer', '42 Menschen'])]:
    t = cb2_eintrag(key)
    if not t:
        pr.append('%s: das Einsatzgebiet "%s" gibt es nicht mehr' % (name, key))
        continue
    if nct not in t:
        pr.append('%s: %s ist nicht mehr genannt' % (name, nct))
    for p in pflicht:
        if p not in t:
            pr.append('%s: "%s" fehlt' % (name, p))
    if 'gescheitert' in t:
        pr.append('%s: wird als "gescheitert" dargestellt, obwohl kein '
                  'Ergebnis berichtet wurde' % name)

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
print('Am 23.11.2026 nachgesehen: %d Dinge' % len(NACHGESEHEN_23_11))
print('Abfragen geprüft: 3 | Stempel im Text: %d' % heute)
print('Probleme:', pr or 'keine')
if pr:
    sys.exit(1)
