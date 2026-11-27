# -*- coding: utf-8 -*-
"""Die Regel der Körperkarte gilt für alle 173 Organfelder, nicht nur für die,
die jemand von Hand geprüft hat.

DIE REGEL steht in der Legende der Seite selbst:
    "Die Stufe meint die gemessene Wirkung: Befunde nur aus Tier- oder
     Zellversuch erreichen höchstens „schwach“."

WARUM ES DIESEN TEST GIBT: Die Regel wurde am 23.11.2026 eingeführt, weil fünf
Felder „deutliche Wirkung“ trugen, obwohl ihr eigener Text sagte, am Menschen
sei nichts gemessen. Die fünf wurden damals von Hand gesenkt - aber kein Test
hielt die Regel fest. organstufe.py prüft nur eine Namensliste bestimmter
Stoff/Organ-Paare auf ihre Wendung im Browser, nicht die Regel.

Am 27.11.2026 habe ich alle Felder nachgezählt. Zwei brachen die Regel wieder:

    cbda.gut    Stufe 2 über einem reinen Tierversuch
    cbdv.brain  Stufe 2, obwohl der eigene Text sagt: am Menschen geprüft und
                NICHT besser als Placebo

Das zweite ist die gefährlichere Sorte: nicht eine fehlende Messung, sondern
eine vorhandene, der die Stufe widersprach.

DIE AUSNAHME, und sie ist benannt statt geduldet: Die körpereigenen Stoffe
(Anandamid, 2-AG) tragen hohe Stufen auf Maus- und Rattenbelegen. Das ist
Absicht. Ihre Rolle lässt sich kaum dadurch prüfen, dass man sie einem
Menschen gibt, und dass 2-AG die kurzfristige Bremse an erregten Synapsen ist,
gehört mit Gegenprobe an Tieren ohne das herstellende Enzym zum Bestbelegten
des Feldes. Diese Rolle auf „schwach“ zu setzen wäre genauso irreführend wie
der umgekehrte Fehler. Die Legende sagt das seit dem 27.11.2026 ausdrücklich -
und dieser Test prüft, dass sie es weiter sagt. Eine Ausnahme, die man nennt,
ist keine Lücke.


HINWEIS zum Muster: Seit dem 27.11.2026 darf ein Organfeld ein drittes
Element 'ohne' tragen ("Geprüft, keine Wirkung" - geprüft und nichts
gefunden, nicht ungeprüft). Das Muster erlaubt es deshalb optional. Ohne
diese Erweiterung wäre jedes so markierte Feld für diesen Test unsichtbar
geworden - ein stilles Loch genau in der Prüfung, die es braucht.
"""
import io
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'
if QUELLE.startswith('file://'):
    QUELLE = QUELLE[7:]
S = io.open(QUELLE, encoding='utf-8').read()

# Das Kopfprotokoll zitiert eigene Fehler und dabei Felder der Seite.
UMFANG = 200000

# Die körpereigenen Stoffe: begründete Ausnahme, siehe Kopf dieser Datei.
# Nur die Stoffe, auf die die BEGRÜNDUNG zutrifft: solche, deren Rolle sich
# nicht dadurch prüfen lässt, dass man sie einem Menschen gibt.
#
# Beim Nachsehen standen hier zuerst auch 'oea' und 'pea'. Das war falsch:
# Beide werden als Nahrungsergänzung eingenommen, und die Seite trägt zu
# beiden Studien AM MENSCHEN (PEA bei Nervenschmerzen, OEA zu Leberwerten und
# Körpermaßen [[32217148]]). Sie brauchen die Ausnahme also gar nicht und
# bestehen die Regel aus eigener Kraft - geschützt wurden sie nur durch meine
# zu weit gezogene Liste. Eine Ausnahme darf nicht mehr abdecken, als ihre
# Begründung trägt.
KOERPEREIGEN = {'aea', '2ag', 'pepcan', 'noladin', 'virod'}

# Ein Text, der sich nur auf Tier oder Zelle stützt.
TIER = re.compile(r'Tierbefund|Tierversuch|Tierstudie|bei Mäusen|an Mäusen|'
                  r'Mäuse|Maus|Ratten|Ratte|im Tier\b|am Tier\b|Zellversuch|'
                  r'Zelllinie|Zellkultur|Schweinehirn')
# ... und einer, der eine Messung am Menschen nennt.
MENSCH = re.compile(r'Teilnehmend|Teilnehmer|randomisiert|doppelblind|'
                    r'Patient|Freiwillige|Befragung|Proben|Fallserie|'
                    r'Notaufnahme|Erwachsenen|Menschen mit|Studie an|'
                    r'Phase-\d|Phase \d|gestillt|Konsument')
# WIE DIE REGEL GEPRÜFT WIRD, und das ist nach zwei Fehlversuchen die
# einfachste Fassung: Stufe 2 oder 3 verlangt eine POSITIVE Messung am
# Menschen. Nicht das Fehlen einer Verneinung - eine vorhandene Messung.
#
# Die beiden Fehlversuche, beide zu streng:
#   (1) Jedes "nicht gemessen" hob den Menschbeleg auf. Damit meldete der Test
#       thc.brust (54 Milchproben, 63 Prozent nachweisbar) und mon.fat (243
#       Teilnehmende, Phase 2a) - Felder, die eine echte Messung UND eine
#       Verneinung zu einer NEBENFRAGE enthalten ("Die Folgen für das Kind
#       sind nicht gemessen"). So bestraft der Test gerade die Felder, die
#       ihre eigenen Grenzen nennen.
#   (2) Dieselbe Verneinung näher an "am Menschen" gebunden - traf weiter
#       cbd.brain, wo zwei Humanbelege stehen und die Verneinung nur die
#       Angst betrifft, nicht die Anfälle.
#
# Mit der positiven Fassung entfällt die Auslegung: Wer Stufe 2 behauptet,
# muss eine Messung am Menschen nennen. Menschliche ZELLEN zählen dabei
# ausdrücklich nicht - die Legende nennt Zellversuche gleichauf mit Tieren.
# DRITTER UND LETZTER ANSATZ. Der zweite war, Stufe 2 müsse eine positive
# Messung am Menschen NENNEN. Das klang richtig und war unbrauchbar: Es
# meldete 26 Felder, von denen fast alle in Ordnung sind - "bei 18 gesunden
# Menschen", "In 41 Placebo-Studien mit 1020 Gelegenheitskonsumenten", "in der
# Zusammenschau von 25 Studien", "0,6 Punkte stärker gesenkt als unter
# Placebo". Menschliche Befunde werden in zu vielen Wendungen beschrieben,
# als dass eine Wortliste sie alle kennen könnte, und ein Test, der bei 26
# gesunden Feldern Alarm schlägt, wird abgeschaltet statt gelesen.
#
# Zuverlässig erkennbar ist die UMGEKEHRTE Richtung: ein Feld, dessen eigener
# Text sagt, dass es am Menschen keine Messung gibt - oder eine, die nichts
# ergab. Das waren alle fünf Fälle vom 23.11.2026, der Paracetamol-Fall und
# alle vier von heute. Diese Fassung ist eng, aber sie trifft genau die
# Fehlerart, die hier wirklich auftritt.
TOTAL_NEG = re.compile(
    # "Am Menschen geprüft wurde nicht das Gehirn, sondern das Verhalten"
    r'(?:Am|am|Beim|beim) Menschen geprüft wurde nicht|'
    # "Am Menschen ist das nicht geprüft", "beim Menschen ist nichts gemessen"
    # Gross-/Kleinschreibung: Beim Sabotieren blieb cbda.gut still, weil
    # sein Satz mit "Am Menschen ist das nicht geprüft" BEGINNT und das
    # Muster nur 'am' kannte. Eine Regel, die am Satzanfang aussetzt, ist
    # keine Regel.
    r'[AaBb](?:m|eim) Menschen (?:ist |war |)(?:das |es |)'
    r'(?:nichts|nicht) (?:gemessen|geprüft|untersucht)|'
    # Gesamtwirkung belegt, Anteil über dieses System nicht - Paracetamol und
    # Metamizol
    r'nicht beziffert|'
    # geprüft und nichts gefunden: trägt keine "deutliche Wirkung"
    r'nicht besser als Placebo|'
    r'ohne signifikanten Unterschied zu Placebo|'
    r'kein(?:en)? (?:signifikanten )?Unterschied zu Placebo')

# Ein lockerer Menschbeleg - absichtlich großzügig. Er muss nur verhindern,
# dass ein Feld mit Humanbezug als "nur Tier" gilt; strenger zu sein hieße,
# wieder 26 gesunde Felder zu melden.
MENSCH_LOSE = re.compile(
    r'Mensch|Patient|Teilnehm|Studie|Placebo|randomisiert|doppelblind|'
    r'Prozent|zugelassen|Meta-Analyse|Zusammenschau|Erwachsene|Kinder|'
    r'Freiwillige|Proben|Konsument|Phase[- ]\d|Befragung|Register|'
    # syn.heart stützt sich auf eine Fallserie - das IST ein Humanbeleg,
    # und ohne dieses Wort meldete der Test ihn als "nur Tier oder Zelle".
    r'Fallserie|Einzelfäll|jedem fünften Fall')


def balance(s, i):
    """i zeigt auf '{' -> Index hinter der passenden '}'."""
    t, k, instr, q = 0, i, False, ''
    while k < len(s):
        c = s[k]
        if instr:
            if c == '\\':
                k += 2
                continue
            if c == q:
                instr = False
        else:
            if c in '"\'':
                instr = True
                q = c
            elif c == '{':
                t += 1
            elif c == '}':
                t -= 1
                if t == 0:
                    return k + 1
        k += 1
    return k


probleme = []
felder = 0
hoch = 0
ausnahmen = 0

for m in re.finditer(r'organs:\{', S):
    if m.start() < UMFANG:
        continue
    a = m.end() - 1
    blk = S[a:balance(S, a)]
    vor = S[max(0, m.start() - 6000):m.start()]
    ids = re.findall(r"id:'([a-z0-9]+)'", vor)
    stoff = ids[-1] if ids else '?'
    for e in re.finditer(r"([a-z]+):\[(\d+),'((?:[^'\\]|\\.)*)'(?:,'(\w+)')?\]", blk):
        organ, stufe, txt = e.group(1), int(e.group(2)), e.group(3)
        felder += 1
        if stufe < 2:
            continue
        hoch += 1
        if stoff in KOERPEREIGEN:
            ausnahmen += 1
            continue
        stufen_wort = ['', 'schwach', 'deutlich', 'stark'][stufe]
        if TOTAL_NEG.search(txt):
            probleme.append(
                '%s.%s steht auf Stufe %d ("%s"), sagt im eigenen Text aber, '
                'dass am Menschen nichts gemessen wurde oder die Messung '
                'nichts ergab: "%s"'
                % (stoff, organ, stufe, stufen_wort,
                   re.sub(r'\s+', ' ', txt)[:130]))
        elif TIER.search(txt) and not MENSCH_LOSE.search(txt):
            probleme.append(
                '%s.%s steht auf Stufe %d ("%s"), stützt sich im eigenen Text '
                'aber allein auf Tier oder Zelle: "%s"'
                % (stoff, organ, stufe, stufen_wort,
                   re.sub(r'\s+', ' ', txt)[:130]))

if felder < 100:
    probleme.append('nur %d Organfelder gefunden – die Suche greift nicht' % felder)

# Die Regel muss in der Legende stehen, sonst ist sie keine Regel.
I = S[UMFANG:]
# Die Regel steht an ZWEI Stellen: in der Legende der Körperkarte und im
# Korrekturprotokoll, das ihre Einführung beschreibt. Gesucht wird die
# Legende - sonst erfüllt die Kopie im Protokoll die Prüfung, während die
# Legende schweigt. (Beim Sabotieren aufgefallen: der Anker war zweimal da.)
_b = S.find('id="bodySvg"')
_legende = S[_b:_b + 2500] if _b > 0 else ''
if not _legende:
    probleme.append('Die Körperkarte (id="bodySvg") ist nicht zu finden')
elif 'Befunde nur aus Tier- oder Zellversuch erreichen höchstens' not in _legende:
    probleme.append('Die Legende der Körperkarte nennt die Regel nicht mehr')
# Und die Ausnahme muss benannt bleiben, sonst duldet die Seite sie stumm.
if 'Für die körpereigenen Stoffe gilt das nicht' not in _legende:
    probleme.append('Die Legende nennt die Ausnahme der körpereigenen Stoffe '
                    'nicht mehr – dann stehen fünf Felder ohne Begründung über '
                    'ihrer eigenen Regel')

print('Organfelder: %d | davon Stufe 2 oder 3: %d | begründete Ausnahmen '
      '(körpereigen): %d' % (felder, hoch, ausnahmen))
print('Probleme:', probleme or 'keine')
if probleme:
    sys.exit(1)
