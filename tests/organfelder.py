# -*- coding: utf-8 -*-
"""Jedes Organfeld braucht einen Beleg oder einen genannten Grund.

WARUM ES DIESEN TEST GIBT: Am 27.11.2026 fand ich mit einer einmaligen Suche
ueber alle 33 Stoffe vier Organfelder, die etwas behaupteten, ohne eine Quelle
zu nennen und ohne zu sagen, dass es keine gibt:

    CBDA / Leber     "Abbau ueber die Leber."
    BCP / Haut       "Lokale Entzuendungshemmung."
    Synth. / Darm    "Uebelkeit und Erbrechen."
    Synth. / Lunge   "Aufnahme beim Rauchen."

Sie standen so seit Monaten. Nicht weil jemand sie verteidigt haette, sondern
weil niemand nach ihnen suchte. Das ist die stillste Fehlerart dieser Seite:
Eine Aussage ohne Beleg sieht genauso aus wie eine mit, solange man nicht
nachzaehlt.

Das Darmfeld war dabei nicht nur unbelegt, sondern irrefuehrend: "Uebelkeit
und Erbrechen." ohne Richtung, bei einer Stoffgruppe, deren Verwandter THC
GEGEN Uebelkeit eingesetzt wird. Ein Leser muss es falsch verstehen.

WAS GILT: Ein Organfeld darf alles sagen, was belegt ist - dann steht eine
Quelle als [[pmid]] darin. Oder es darf sagen, dass etwas NICHT gemessen
wurde - dann steht der Grund darin. Was es nicht darf, ist behaupten und
schweigen.

DIESER TEST liest die Quelldatei, nicht die Darstellung: Organfelder sind
Daten, und ihre Form laesst sich im Quelltext genauer pruefen als im
gerenderten Text, wo mehrere Felder zu einem Absatz verschmelzen.


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

# Ein genannter Grund: der Text sagt selbst, dass hier nichts gemessen ist.
GRUND = re.compile(
    r'nicht gemessen|keine Studie|nicht geprüft|nie geprüft|nicht untersucht|'
    r'Registerstand|abgefragt am|keine gemessene|nicht eigens|nicht bekannt|'
    r'ist offen|unbekannt')


def balance(s, i):
    """i zeigt auf '{' -> Index hinter der passenden '}'. Strings werden
    uebersprungen, sonst zaehlt eine Klammer im Text mit."""
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
belegt = 0
mitGrund = 0
bloecke = 0

for m in re.finditer(r'organs:\{', S):
    if m.start() < UMFANG:
        continue
    bloecke += 1
    a = m.end() - 1
    blk = S[a:balance(S, a)]
    # Welcher Stoff? Der naechste id:'...' davor.
    vor = S[max(0, m.start() - 6000):m.start()]
    ids = re.findall(r"id:'([a-z0-9]+)'", vor)
    stoff = ids[-1] if ids else '?'
    for e in re.finditer(r"([a-z]+):\[(\d+),'((?:[^'\\]|\\.)*)'(?:,'(\w+)')?\]", blk):
        organ, stufe, txt = e.group(1), e.group(2), e.group(3)
        felder += 1
        if '[[' in txt:
            belegt += 1
            continue
        if GRUND.search(txt):
            mitGrund += 1
            continue
        probleme.append('%s.%s (Stufe %s) behauptet ohne Beleg und ohne '
                        'genannten Grund: "%s"' % (stoff, organ, stufe, txt[:70]))

if bloecke < 20:
    probleme.append('nur %d organs-Bloecke gefunden – die Suche greift nicht '
                    '(erwartet rund 33)' % bloecke)
if felder < 100:
    probleme.append('nur %d Organfelder gefunden – die Suche greift nicht' % felder)

# --- 27.11.2026: Kein Sammeleintrag, der seine Geschwister nicht kennt ----
# Gefunden beim Durchsehen der 24 Saetze der Form "am Menschen nicht
# geprueft": CB2_USE.entz ("Entzuendung allgemein") sagte "am Menschen nie in
# einer aussagekraeftigen Studie geprueft" - waehrend drei Eintraege DERSELBEN
# Liste gescheiterte Phase-2- und Phase-3-Pruefungen desselben Wirkprinzips
# fuehren (systemische Sklerose, Dermatomyositis, Mukoviszidose, zusammen 986
# Menschen). Aus "geprueft und durchgefallen" wurde "nie geprueft", und zwar
# innerhalb derselben Datenstruktur.
#
# Diese Fehlerart laesst sich maschinell finden, und genau das tut die Regel:
# Sagt ein Eintrag "nie geprueft" (oder gleichbedeutend), waehrend ein
# Geschwistereintrag auf --block steht, muss er das erklaeren - durch einen
# Verweis auf die Geschwister oder durch eine Einschraenkung des Anspruchs.
NIE = re.compile(r'nie (?:in einer \w+ Studie )?geprüft|nie am Menschen|'
                 r'am Menschen nie\b(?![^.]*(?:Zielwert|geprüft wurden|'
                 r'derselben Liste))')
for name in ('CB2_USE', 'LAB_USE', 'MAGL_USE', 'CB1_RUN'):
    m = re.search(r'const %s = \{' % name, S)
    if not m:
        continue
    blk = S[m.end() - 1:balance(S, m.end() - 1)]
    hat_block = "'--block'" in blk
    if not hat_block:
        continue
    for e in re.finditer(r"\n ?'?(\w[\w|]*)'?:\[(.*?)\],?\n(?= ?'?\w|\})", blk, re.S):
        key, inhalt = e.group(1), e.group(2)
        felderL = re.findall(r"'((?:[^'\\]|\\.)*)'", inhalt)
        if not felderL:
            continue
        letzte = felderL[-1]
        if not NIE.search(letzte):
            continue
        # Erklaert der Eintrag, warum "nie" trotz gescheiterter Geschwister?
        if re.search(r'Zielwert|derselben Liste|einzelne Krankheiten|'
                     r'geprüft wurden', letzte):
            continue
        probleme.append(
            '%s.%s sagt "nie geprüft", obwohl in derselben Liste gescheiterte '
            'Prüfungen stehen: "%s"' % (name, key, letzte[:90]))

print('Stoffe mit Organfeldern: %d | Felder: %d' % (bloecke, felder))
print('  mit Quelle: %d | mit genanntem Grund: %d' % (belegt, mitGrund))
print('Probleme:', probleme or 'keine')
if probleme:
    sys.exit(1)
