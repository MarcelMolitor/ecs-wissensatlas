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
# 27.11.2026 umgebaut: Vorher hing diese Regel an einem einzigen Datum. Das
# geht nur bis zum naechsten Arbeitstag gut - der 27.11. brachte zwei neue
# Stempel, die unbemerkt durchgelaufen waeren, weil nur der 23.11. gezaehlt
# wurde. Jetzt ein Datum pro Eintrag: Wer irgendwann einen Stempel setzt, muss
# unter SEINEM Datum eintragen, was er nachgesehen hat, und ein Datum, das im
# Text auftaucht aber hier fehlt, schlaegt an.
# NACHGETRAGEN am 27.11.2026, und zwar mit Vorbehalt: Diese drei Tage lagen
# vor dieser Regel. Ihre Eintraege sind aus dem beschrieben, WAS DIE SEITE
# SAGT - ich habe diese Abfragen nicht wiederholt. Sie stehen hier, damit die
# Regel greift, nicht als Bestaetigung. Wer einen davon anfasst, sieht neu
# nach und setzt sein eigenes Datum.
NACHGESEHEN = {
    '15.11.2026': [
        'Nimacimab NCT06577090: Pruefplan - was ein peripher begrenzter '
        'Antikoerper messen wuerde und was nicht',
        'Ein Pruefplan mit sechs Teilnehmenden, der ohne Ergebnis blieb: '
        'belegt ist das Prinzip, nicht die Wirkung',
        'Drei Studien, die sich auf Spastik und Unruhe richten - '
        'Registerstand',
        'Ein weiterer Pruefplan-/Registerstand im Organfeld (NICHT '
        'wiederholt, aus dem Seitentext nachgetragen)',
    ],
    '21.11.2026': [
        'Der dritte Zustand - angefasst, ohne berichtetes Ergebnis: '
        'Registerstand',
        'Nimacimab NCT06577090: Absicht klar, Wirkung nicht - daher '
        'niedrige Belegstufe',
        'NCT03900325: Nebenbeobachtung, ohne Ergebnis, Registerstand seit '
        'Jahren unbekannt',
        'NCT05622994: sollte 11/2023 fertig sein, Eintrag seitdem '
        '"unbekannt", nichts berichtet',
    ],
    '22.11.2026': [
        'US-Patent 6.630.507: am 21.04.2019 abgelaufen (Google Patents)',
        'NCT01385124, NCT01596075, NCT02392780, NCT02478424: alle vier auf '
        '"unbekannt", keine berichtet Ergebnisse',
        'NCT03093402: im Register und als Kongressbeitrag, kein Aufsatz',
    ],
    '23.11.2026': [
        'THCP im Studienregister: null Eintraege',
        'Cannabichromen im Studienregister: ein zurueckgezogener Eintrag',
        'Cannabinol im Studienregister: elf Eintraege, keiner zur Abwehr',
        'S-777469 bei Neurodermitis: zwei Studien, keine Ergebnisse',
        'KHK6188 bei Zoster-Neuralgie: eine Studie, keine Ergebnisse',
        'NCT03625453 (MAGL bei Tourette): kein Ergebnisbericht im Register – '
        'die Veroeffentlichung gibt es aber',
        'Die vier unberichteten Rimonabant-Programme (Praediabetes NCT00325650, '
        'Essanfaelle NCT00481975, NASH NCT00576667, Alzheimer NCT00380302): '
        'alle has_results = false, keine Arbeit in PubMed',
    ],
    '27.11.2026': [
        'NCT02889224 (VISECA, Endocannabinoide beim Cushing-Syndrom, '
        'Bordeaux): abgeschlossen 09/2013, has_results = false, keine Arbeit '
        'in PubMed',
        'CB1-Blocker GEGEN das Cushing-Syndrom: keine einzige Studie im '
        'Register – deshalb kein Einsatzgebiet und kein siebtes '
        'Rimonabant-Programm',
    ],
}
gefunden = sorted(set(re.findall(r'abgefragt am (\d{1,2}\.\d{1,2}\.20\d\d)', I)))
for tag in gefunden:
    if tag not in NACHGESEHEN:
        pr.append('Stempel vom %s im Text, aber kein Eintrag in NACHGESEHEN – '
                  'was wurde an dem Tag nachgesehen?' % tag)
for tag, liste in NACHGESEHEN.items():
    n = I.count('abgefragt am ' + tag)
    if n != len(liste):
        pr.append('Stempel vom %s: %d im Text, aber %d Dinge als nachgesehen '
                  'eingetragen – wurde wirklich nachgesehen?'
                  % (tag, n, len(liste)))
heute = sum(I.count('abgefragt am ' + t) for t in NACHGESEHEN)

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

# --- 5) Ein Einzelbefund darf nicht ohne seine Gegenprobe stehen ---------
# Am 23.11.2026 stand auf der Seite: eine Einzeldosis senkte Tics, und die
# groessere Studie sei "weder veroeffentlicht noch berichtet". Die
# Veroeffentlichung gab es seit 2021 - mit umgekehrtem Ergebnis, zugunsten von
# Placebo. Der Leser nahm mit: vielversprechend, niemand hat nachgesehen. In
# Wahrheit hatte jemand zwoelf Wochen lang nachgesehen.
#
# Das ist die Schwester der veralteten Verneinung: ein frueher Befund, dessen
# Widerlegung fehlt. Darum die Regel: Wo der Einzeldosis-Befund zitiert wird,
# muss die zwoelfwoechige Studie im selben Atemzug stehen - und mit ihrer
# RICHTUNG, nicht nur mit ihrer Nummer.
EINZEL, GROSS = '34847610', '34117788'
stellen = [m.start() for m in re.finditer(r'\[\[%s\]\]' % EINZEL, I)]
if not stellen:
    pr.append('Der Tourette-Einzeldosis-Befund (%s) ist nicht mehr zitiert' % EINZEL)
for i in stellen:
    if GROSS not in I[max(0, i - 200):i + 700]:
        pr.append('Einzeldosis-Befund ohne die zwölfwöchige Studie: …%s…'
                  % re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', I[max(0, i - 110):i + 150])))
for i in [m.start() for m in re.finditer(r'\[\[%s\]\]' % GROSS, I)]:
    umfeld = I[max(0, i - 700):i + 120]
    if 'zugunsten von Placebo' not in umfeld and 'negativ' not in umfeld:
        pr.append('Die zwölfwöchige Studie wird ohne ihre Richtung zitiert')
# ... und die Seite darf sie nirgends wieder als unveroeffentlicht fuehren
j = I.find('NCT03625453')
if j < 0:
    pr.append('NCT03625453 ist nicht mehr genannt')
else:
    umfeld = I[max(0, j - 1200):j + 600]
    for schlecht in ['unveröffentlicht', 'nie veröffentlicht', 'keine Veröffentlichung',
                     'weder eine Veröffentlichung']:
        if schlecht in umfeld:
            pr.append('NCT03625453 gilt wieder als unveröffentlicht ("%s") – '
                      'die Arbeit ist 2021 erschienen' % schlecht)

# --- 6) Das unberichtete Programm: Summe und Einordnung ------------------
# Am 23.11.2026 dazugekommen. Zwei Dinge koennen hier verrotten, ohne dass
# jemand die Seite anfasst:
#   a) Die handgeschriebene Summe. Steht einmal eine Zahl mehr oder weniger in
#      der Liste, stimmt sie nicht mehr. Darum wird sie nachgerechnet und nicht
#      nur gesucht - dieselbe Lehre wie bei den vier veralteten Zahlen im
#      Aenderungsprotokoll.
#   b) Die Einordnung. Diese vier Studien sind NICHT gescheitert, sie sind nie
#      berichtet. Wer das zu "gescheitert" verkuerzt, macht aus Schweigen einen
#      Befund - genau der Fehler, den die Seite an anderer Stelle anprangert.
j = I.find('Ein ganzes Programm')
if j < 0:
    pr.append('Der Abschnitt über das unberichtete Rimonabant-Programm ist weg')
else:
    block = I[j:j + 6000]
    for nct in ['NCT00325650', 'NCT00481975', 'NCT00576667', 'NCT00380302']:
        if block.count(nct) != 1:
            pr.append('%s steht %dx im Abschnitt (erwartet 1x)'
                      % (nct, block.count(nct)))
    # Die Summe nachrechnen: die Teilnehmerzahlen stehen in den <dt>-Zeilen
    teil = [int(x) for x in re.findall(r'·\s*(\d{2,5}) Menschen</dt>', block)]
    summe = re.search(r'Das sind ([\d  ]+) Menschen', block)
    if len(teil) != 4:
        pr.append('%d Teilnehmerzahlen im Abschnitt gefunden (erwartet 4): %s'
                  % (len(teil), teil))
    elif not summe:
        pr.append('die Summe steht nicht mehr im Abschnitt')
    else:
        gesagt = int(re.sub(r'\D', '', summe.group(1)))
        if gesagt != sum(teil):
            pr.append('Summe stimmt nicht: Seite sagt %d, die vier Zahlen '
                      'ergeben %d (%s)' % (gesagt, sum(teil), teil))
    # Schweigen darf nicht zu einem Befund werden
    for schlecht in ['vier gescheiterten', 'sind gescheitert',
                     'es gibt keine Studie', 'wurde nie untersucht']:
        if schlecht in block:
            pr.append('das unberichtete Programm wird als Befund dargestellt: '
                      '"%s"' % schlecht)
    # Und die beiden Einschraenkungen muessen stehenbleiben
    for muss in ['nennt das Register nicht', 'PubMed']:
        if muss not in block:
            pr.append('Einschränkung fehlt im Abschnitt: ' + muss)

print('Verneinungen mit Beleg und Datum geprüft: %d' % len(FEST))
print('Einzelbefunde mit Pflicht-Gegenprobe: 1 (Tourette, %d Fundstellen)'
      % len(stellen))
for tag in sorted(NACHGESEHEN):
    print('Am %s nachgesehen: %d Dinge' % (tag, len(NACHGESEHEN[tag])))
print('Abfragen geprüft: 3 | Stempel im Text: %d (Tage: %s)'
      % (heute, ', '.join(gefunden)))
print('Probleme:', pr or 'keine')
if pr:
    sys.exit(1)
