# -*- coding: utf-8 -*-
"""Prueft die Rueckkehr von Rimonabant - und die Dosisentscheidung dazu.

WARUM ES DIESEN TEST GIBT: Die Seite nannte Rimonabant an 79 Stellen als
abgeschlossene Geschichte und trug im Zeitstrahl den Eintrag "Das endgueltige
Ende von Rimonabant". Seit November 2026 stimmt das nicht mehr: im Register
stehen vier neue Studien. Schlimmer noch - die Seite fragt fuer diesen Stoff
LIVE bei ClinicalTrials.gov ab. Ein Leser konnte also vier laufende Studien in
der Live-Liste sehen, waehrend daneben "Ehemaliges Medikament" stand und eine
Uebersicht von 2013 zitiert wurde, nach der niemand die Entwicklung mehr
unterstuetzt. Diesen Widerspruch erzeugte die Seite gegen sich selbst.

DIE DOSISENTSCHEIDUNG, die dieser Test festhaelt:
dosis.py ERLAUBT Milligramm-Angaben zu Rimonabant ausdruecklich (er steht in
seiner Ausnahmeliste), weil der Stoff nirgends zugelassen ist. Fuer DIESE
Passagen gilt das trotzdem nicht, und zwar aus einem anderen Grund als bei
erhaeltlichen Mitteln: Hier steht nicht mehr "so wurde damals abgenommen",
sondern "so wird gerade gegen Lahmheit nach Schlaganfall geprueft". Rimonabant
ist im Graumarkt zu bekommen, und "X Milligramm verbessern das Gehen nach
Schlaganfall" ist ein Satz, nach dem gehandelt wird. Der wissenschaftliche
Punkt - ein Viertel der damaligen Dosis - steht als VERHAELTNIS da. Das
Verhaeltnis traegt die Aussage vollstaendig; die Zahl traegt nichts bei, wonach
sich aber jemand richten koennte.

Die sieben aelteren Stellen mit Milligramm bleiben unberuehrt. Ob die Regel
auch fuer sie gilt, ist eine offene Entscheidung von Marcel; dieser Test
entscheidet sie nicht, er haelt nur die neuen Passagen frei.

WAS SONST FESTGEHALTEN WIRD: dass nicht behauptet wird, es wirke. Keine der
vier Studien hat ein Ergebnis, die Vorlaeuferstudie hat nach drei Jahren keines
berichtet, und zur angegebenen Begruendung findet PubMed keine Arbeit. Ein
Zeitstrahl-Eintrag "Rimonabant kommt zurueck" ohne diese drei Saetze waere
eine Werbeaussage.
"""
import io
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'
S = io.open(QUELLE, encoding='utf-8').read()

# Das Kopfprotokoll der Seite beschreibt eigene frueherere Fehler und nennt
# dabei dieselben Nummern und Saetze. Es darf nicht mitzaehlen.
UMFANG = 200000
INHALT = S[UMFANG:]

pr = []

# --- 1) Die widerlegte Behauptung ist weg ----------------------------------
if 'Das endgültige Ende von Rimonabant' in INHALT:
    pr.append('die widerlegte Behauptung "endgültige Ende" ist zurück')

# --- 2) Der 2010-Eintrag nennt den Stoff und behaelt seine Zahlen ----------
# Es gibt ZWEI Einträge für 2010 - der andere handelt von Taranabant. Darum
# nicht nach dem Jahr suchen, sondern nach der Studie, um die es geht: die mit
# den 18.695 Teilnehmenden. Der erste Versuch griff den falschen Eintrag und
# meldete, die Zahlen seien verloren, während sie unberührt dastanden.
gross = [x for x in re.finditer(r"\['2010','([^']*)','([^']*)'\]", INHALT)
         if '18.695' in x.group(2)]
if len(gross) != 1:
    pr.append('Eintrag zur großen Studie (18.695) nicht eindeutig gefunden: %d' % len(gross))
else:
    titel, text = gross[0].group(1), gross[0].group(2)
    if 'Rimonabant' not in titel + text:
        pr.append('Eintrag zur großen Studie nennt den Stoff nicht: %r' % titel)
    if 'vier Suizide' not in text:
        pr.append('Eintrag zur großen Studie hat die Suizidzahlen verloren')

# --- 3) Die Rueckkehr steht an beiden Stellen ------------------------------
STELLEN = {}
mz = re.search(r"\['2026','(Rimonabant kommt zurück[^']*)','([^']*)'\]", INHALT)
if not mz:
    pr.append('Zeitstrahl-Eintrag zur Rückkehr fehlt')
else:
    STELLEN['Zeitstrahl'] = mz.group(1) + ' ' + mz.group(2)

ir = INHALT.find("{id:'rim',")
if ir < 0:
    pr.append('Stoffeintrag rim nicht gefunden')
else:
    seg = INHALT[ir:ir + 7000]
    j = seg.find('Und seit November 2026')
    if j < 0:
        pr.append('Stoffeintrag rim erwähnt die Rückkehr nicht')
    else:
        STELLEN['Stoffeintrag'] = seg[j:seg.find('organs:', j)]
    if 'wieder in Studien' not in seg[:400]:
        pr.append('Gattung sagt noch, es sei nur ein ehemaliges Medikament')

# --- 4) Alle vier Studien, und die Vorlaeuferstudie ------------------------
for nct in ['NCT07843108', 'NCT07913763', 'NCT07941479', 'NCT07930637']:
    if INHALT.count(nct) < 2:
        pr.append('%s fehlt an einer der beiden Stellen' % nct)
if INHALT.count('NCT05622994') < 2:
    pr.append('die Vorläuferstudie NCT05622994 fehlt')

# --- 5) KEINE Milligramm-Angabe in diesen Passagen ------------------------
SP = '[  ]?'
DOSIS = re.compile(r'\d[\d.,]*' + SP + r'(mg|µg|mcg|g|ml)\b')
for wo, txt in STELLEN.items():
    d = DOSIS.search(txt)
    if d:
        pr.append('%s nennt eine Dosis: %r' % (wo, d.group(0)))
    if 'Viertel' not in txt:
        pr.append('%s nennt das Verhältnis zur damaligen Dosis nicht' % wo)

# --- 6) Es wird nicht behauptet, dass es wirkt -----------------------------
for wo, txt in STELLEN.items():
    if not re.search(r'(Ergebnisse gibt es aus keiner|noch nichts gezeigt)', txt):
        pr.append('%s sagt nicht, dass kein Ergebnis vorliegt' % wo)
    if 'unbekannt' not in txt:
        pr.append('%s verschweigt, dass die Vorläuferstudie nichts berichtet hat' % wo)
    if '2026' not in txt:
        pr.append('%s nennt keinen Registerstand' % wo)

# --- 7) Die Schutzmassnahmen gegen den Schaden von 2008 -------------------
sa = STELLEN.get('Stoffeintrag', '')
if sa:
    for was, wort in [('Ausschluss bei Suizidrisiko', 'Suizidrisiko'),
                      ('besondere Beobachtung der Psyche', 'besonderem Interesse')]:
        if wort not in sa:
            pr.append('Stoffeintrag nennt %s nicht' % was)

print('Stellen geprüft: %d | Probleme:' % len(STELLEN), pr or 'keine')
if pr:
    sys.exit(1)
