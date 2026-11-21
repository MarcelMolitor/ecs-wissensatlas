# -*- coding: utf-8 -*-
"""Prueft Untertitel, die etwas ZAEHLEN, gegen das Gezaehlte.

WARUM ES DIESEN TEST GIBT: Die Seite schreibt ihre Anzahlen aus - "Fuenf
Dinge, bei denen eine Verschiebung am Menschen belegt ist", "Sieben Produkte
und Zutaten". Wer eine Zeile hinzufuegt, muss das Zahlwort mitziehen, und
genau das vergisst man. Am 14.11.2026 stand eine Woche lang ein Satz ueber
"die drei Zustaende" der CB1-Matrix auf der Seite, nachdem ein vierter
dazugekommen war. Am 21.11. hatte ich dieselbe Falle vor mir, als eine sechste
Zeile in die Tabelle "Am Menschen gemessen" kam - diesmal vorher gesehen, und
daraus wurde dieser Test.

HINWEIS ZUR LAENGE: Der erste Versuch begrenzte den Untertitel auf 40
Zeichen. "Fuenf Dinge, bei denen eine Verschiebung am Menschen belegt ist" hat
61 - der Test fand zwei von zwoelf Untertiteln, keinen davon an einer Tabelle,
und schlug gegen eine absichtliche Sabotage NICHT an. Eine gruene Pruefung,
die nichts prueft. Darum 160 Zeichen, und darum steht die Zahl der geprueften
Untertitel in der Ausgabe.

WAS GEPRUEFT WIRD: Jeder Untertitel, der mit einem ausgeschriebenen Zahlwort
beginnt und innerhalb von 900 Zeichen von einem <tbody> gefolgt wird. Dort
laesst sich das Zahlwort gegen die Zahl der <tr> halten.

WAS NICHT GEPRUEFT WERDEN KANN, und das sagt der Test selbst an: Die meisten
zaehlenden Untertitel zaehlen Dinge im Fliesstext ("Drei Schluesse", "Vier
Einschraenkungen"). Was dort eine Einheit ist, weiss nur, wer den Text liest.
Der Test nennt ihre Zahl, damit die Luecke sichtbar bleibt und niemand sein
Gruen fuer mehr nimmt, als es ist.
"""
import io
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'
S = io.open(QUELLE, encoding='utf-8').read()

# Das Kopfprotokoll beschreibt eigene frueherere Fehler und zitiert dabei
# Saetze der Seite. Es darf nicht mitzaehlen.
UMFANG = 200000
INHALT = S[UMFANG:]

ZAHL = {'Zwei': 2, 'Drei': 3, 'Vier': 4, 'Fünf': 5, 'Sechs': 6, 'Sieben': 7,
        'Acht': 8, 'Neun': 9, 'Zehn': 10, 'Elf': 11, 'Zwölf': 12}

pr = []
mit_tabelle = 0
ohne_tabelle = []

for m in re.finditer(r'<span class="sub">(%s)\s+([^<]{0,160})</span>' % '|'.join(ZAHL), INHALT):
    wort, rest = m.group(1), m.group(2).strip()
    gesagt = ZAHL[wort]
    tb = INHALT.find('<tbody>', m.end())
    if tb < 0 or tb - m.end() > 900:
        ohne_tabelle.append('%s %s' % (wort, rest[:28]))
        continue
    te = INHALT.find('</tbody>', tb)
    if te < 0:
        pr.append('%s %s: <tbody> ohne Ende' % (wort, rest[:28]))
        continue
    zeilen = INHALT.count('<tr>', tb, te)
    mit_tabelle += 1
    if zeilen != gesagt:
        pr.append('»%s %s«: Untertitel sagt %d, Tabelle hat %d Zeilen'
                  % (wort, rest[:34], gesagt, zeilen))

print('Zählende Untertitel: %d | davon an einer Tabelle prüfbar: %d'
      % (mit_tabelle + len(ohne_tabelle), mit_tabelle))
print('Nicht prüfbar (zählen im Fließtext): %d – %s'
      % (len(ohne_tabelle), '; '.join(ohne_tabelle) if ohne_tabelle else 'keine'))
print('Probleme:', pr or 'keine')
if pr:
    sys.exit(1)
