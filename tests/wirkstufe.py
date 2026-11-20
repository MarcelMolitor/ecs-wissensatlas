# -*- coding: utf-8 -*-
"""Die Regel der Wirkungs-Skala (14.11.2026).

REGEL, die seit dem 14.11.2026 in der Legende der Koerperkarte steht:
Die Stufe meint die GEMESSENE Wirkung; Befunde nur aus Tier- oder Zellversuch
erreichen hoechstens "Schwache Wirkung".

WARUM ES DIESEN TEST GIBT: Vorher stand die Bedeutung der Stufen nirgends, und
ich hatte sie in verschiedenen Runden ungleich vergeben - Metamizol/Immunsystem
Stufe 0 fuer "nichts gemessen", beta-Caryophyllen/Darm Stufe 2, obwohl sein
eigener Text sagt "Am Menschen ist das nicht geprueft". Der grosse Ring auf der
Karte behauptete dann das Gegenteil der Tafel darunter.

WARUM WORTLISTE STATT MUSTER: Mein erster Versuch war ein Regex auf
"am Menschen ... geprueft/gemessen". Der hat die POSITIVFORM mitgelesen und zwei
Felder gemeldet, in denen "Am Menschen geprueft" steht (zyn/brain, aef/brain).
Eine Verneinung erkennt man hier nur an der konkreten Wendung.

ABGRENZUNG: mon/fat traegt Stufe 2 und enthaelt "wurde nicht gemessen" - dort
ist aber die Gewichtsabnahme am Menschen sehr wohl gemessen (243 Teilnehmer),
offen ist nur, WELCHES Fettdepot schrumpfte. Solche Saetze duerfen nicht
greifen, deshalb verlangt jede Wendung der Liste den Bezug "am Menschen" (oder
bei aea/repro die ausdrueckliche Form "ist damit nicht gemessen" hinter
"Zellversuch").

NACHTRAG 15.11.2026 - DIE LUECKE DIESES TESTS, und sie war gross:
Dieser Test pruefte die Regel nur dort, wo der FELDTEXT den Menschenbeleg
ausdruecklich verneint, plus eine festgeschriebene Liste von fuenf Feldern.
Felder, die einfach nur Tierbelege zitieren OHNE das im Text zu sagen, kamen
gar nicht vor. Beim Nachmessen standen NEUN solche Felder auf Stufe 2 oder 3:
apap/brain (3), apap/spinal (2), apap/liver (2), pea/immune (2), mtz/brain (2),
prop/brain (2), pet/brain (3), pet/spinal (2), olo/immune (2). Alle gesenkt.
Pruefung 5 unten prueft jetzt die REGEL statt einer Liste: Fuer jedes Feld ab
Stufe 2 werden die TYPEN seiner Belege im Verzeichnis nachgesehen; sind alle
Tierstudie oder Zellversuch, ist das ein Verstoss.

AUSNAHME, und zwar eine begruendete: Anandamid und 2-AG sind koerpereigene
Botenstoffe. Man kann sie einem Menschen nicht geben, also KANN es dort keine
Messung am Menschen geben - die Regel wortwoertlich angewandt wuerde die
rueckwaerts laufende Daempfung von 2-AG zur "schwachen Wirkung" machen, obwohl
sie zu den bestbelegten Befunden des Gebiets gehoert. Diese Felder stehen in
KOERPEREIGEN und sind von Pruefung 5 ausgenommen, bis Marcel entscheidet, ob
die Skala fuer koerpereigene Stoffe anders gelesen werden soll. Die Ausnahme
ist eine offene Frage, kein Freibrief: Waechst die Liste, ist das ein Zeichen,
dass die Entscheidung nachgeholt werden muss.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io, re, sys

# 15.11.2026: Der Standard war '/home/claude/ecs-atlas.html' - die ARBEITSDATEI.
# Alle anderen Tests der Suite lesen 'page.html', die Kopie des Prueflings. Damit
# prueffte dieser Test im Suitelauf eine andere Datei als der Rest, und jede
# Gegenprobe "gegen die alte Fassung" lief ins Leere, weil er sie nie ansah.
# Standard jetzt page.html; ein Pfad als Argument geht weiter vor (fuer Gegenproben).
QUELLE = sys.argv[1].replace('file://', '') if len(sys.argv) > 1 else HIER + '/page.html'

VERNEIN = ['am Menschen nicht geprüft', 'Am Menschen nicht geprüft',
           'am Menschen nicht gemessen', 'Am Menschen ist das nicht geprüft',
           'am Menschen ist nichts gemessen', 'Am Menschen ist nichts gemessen',
           'Am Menschen fehlen Studien', 'Am Menschen fehlen Daten',
           'am Menschen fehlen Studien', 'am Menschen nicht untersucht',
           'Am Menschen nicht untersucht', 'am Menschen nicht wiederzufinden',
           'ist damit nicht gemessen', 'am Menschen nicht nachgewiesen']
STUFE = ['Nicht untersucht', 'Schwache Wirkung', 'Deutliche Wirkung', 'Starke Wirkung']
# Die fuenf am 14.11.2026 gesenkten Felder muessen auf 1 bleiben.
GESENKT = {('aea', 'repro'): 1, ('cbda', 'brain'): 1, ('bcp', 'immune'): 1,
           ('bcp', 'gut'): 1, ('thcp', 'brain'): 1}
# mon/fat ist der Gegenfall: Stufe 2 ist dort richtig und muss bleiben.
BLEIBT = {('mon', 'fat'): 2}
# Koerpereigene Botenstoffe - siehe NACHTRAG im Kopf. Von Pruefung 5 ausgenommen.
KOERPEREIGEN = {'aea', '2ag'}
NUR_TIER = {'Tierstudie', 'Zellversuch'}


def felder(S):
    """(stoff, organ) -> (stufe, text), per Klammerzaehlung im Stoffobjekt."""
    out = {}
    for m in re.finditer(r"\{id:'(\w+)',group:'", S):
        sid = m.group(1); i = m.start(); d = 0; k = i
        while True:
            if S[k] == '{': d += 1
            elif S[k] == '}':
                d -= 1
                if d == 0: break
            k += 1
        o = S[i:k + 1]
        g = re.search(r'organs:\{', o)
        if not g: continue
        j = g.end(); d = 1; e = j
        while d:
            if o[e] == '{': d += 1
            elif o[e] == '}': d -= 1
            e += 1
        for f in re.finditer(r"\b(\w+):\[(\d),'((?:[^'\\]|\\.)*)'\]", o[j:e - 1]):
            out[(sid, f.group(1))] = (int(f.group(2)), f.group(3))
    return out


probleme = []
S = io.open(QUELLE, encoding='utf-8').read()
T = S[S.find('<title>'):]
F = felder(T)
if len(F) < 150:
    print('Probleme: nur %d Organfelder erkannt - das Muster passt nicht mehr' % len(F))
    sys.exit(1)

# 1. Die Regel selbst: keine Stufe ab 2, wenn der Text den Menschenbeleg verneint.
verstoss = []
for (sid, org), (st, txt) in sorted(F.items()):
    tr = [v for v in VERNEIN if v in txt]
    if st >= 2 and tr:
        verstoss.append('%s/%s steht auf "%s", sagt aber selbst: »%s«'
                        % (sid, org, STUFE[st], tr[0]))
probleme += verstoss
print('  %d Organfelder geprueft, Regelverstoesse: %d' % (len(F), len(verstoss)))

# 2. Der Test muss ueberhaupt unterscheiden koennen: dieselbe Wendung kommt in
#    Feldern mit Stufe 0/1 vor, die bleiben duerfen. Findet er davon keines,
#    greift die Wortliste ins Leere und der Test kann nicht mehr fehlschlagen.
tief = [k for k, (st, txt) in F.items() if st <= 1 and any(v in txt for v in VERNEIN)]
if not tief:
    probleme.append('Die Wortliste trifft kein einziges Feld mit Stufe 0/1 mehr - '
                    'der Test kann nicht mehr pruefen, ob er nach Stufe unterscheidet')
else:
    print('  ok  die Wortliste trifft auch %d Felder mit Stufe 0/1 (die bleiben duerfen)' % len(tief))

# 3. Die fuenf gesenkten Felder und der Gegenfall namentlich.
for (sid, org), soll in list(GESENKT.items()) + list(BLEIBT.items()):
    if (sid, org) not in F:
        probleme.append('Feld %s/%s gibt es nicht mehr' % (sid, org)); continue
    ist = F[(sid, org)][0]
    if ist != soll:
        probleme.append('%s/%s steht auf Stufe %d, erwartet %d' % (sid, org, ist, soll))
if not [p for p in probleme if 'erwartet' in p]:
    print('  ok  die fuenf gesenkten Felder stehen auf 1, mon/fat bleibt auf 2')

# 4. Die Regel muss fuer den Leser dastehen - sonst ist die Stufe wieder unerklaert.
if 'Die Stufe meint die gemessene Wirkung' not in T:
    probleme.append('Die Regel fehlt in der Legende der Koerperkarte')
else:
    print('  ok  die Regel steht in der Legende')

# 5. DIE REGEL SELBST, an den Belegtypen statt am Wortlaut geprueft.
#    Ein Feld ab Stufe 2, dessen Belege alle Tier- oder Zellversuche sind,
#    verstoesst gegen die Legende - auch wenn sein Text das nicht sagt.
TYP = {m.group(1): m.group(2) for m in
       re.finditer(r"\['(\d{4,9})',\d{4},'[^']*','[^']*','[^']*','[^']*','([^']*)','[^']*'\]", S)}
if len(TYP) < 400:
    probleme.append('Nur %d Belegtypen gelesen - das Verzeichnismuster passt nicht mehr' % len(TYP))
else:
    nurtier = []
    for (sid, org), (st, txt) in sorted(F.items()):
        if st < 2 or sid in KOERPEREIGEN:
            continue
        pm = sorted(set(re.findall(r'\[\[(\d+)\]\]', txt)))
        if not pm:
            continue
        typen = {TYP.get(p) for p in pm}
        if typen and typen <= NUR_TIER:
            nurtier.append('%s/%s steht auf "%s", aber alle Belege (%s) sind %s'
                           % (sid, org, STUFE[st], ', '.join(pm),
                              '/'.join(sorted(t for t in typen if t))))
    probleme += nurtier
    print('  %d Belegtypen gelesen, Felder ab Stufe 2 nur mit Tier-/Zellbelegen: %d'
          % (len(TYP), len(nurtier)))
    # Gegenprobe: die Ausnahme darf nicht unbemerkt wachsen.
    offen = []
    for (sid, org), (st, txt) in sorted(F.items()):
        if st < 2 or sid not in KOERPEREIGEN:
            continue
        pm = sorted(set(re.findall(r'\[\[(\d+)\]\]', txt)))
        typen = {TYP.get(p) for p in pm}
        if pm and typen and typen <= NUR_TIER:
            offen.append('%s/%s' % (sid, org))
    print('  offen (koerpereigen, Entscheidung steht aus): %s'
          % (', '.join(offen) if offen else 'keine'))
    if len(offen) > 6:
        probleme.append('Die Ausnahmeliste fuer koerpereigene Stoffe ist auf %d Felder '
                        'gewachsen - die offene Entscheidung muss nachgeholt werden' % len(offen))

print('Probleme:', probleme or 'keine')
if probleme:
    sys.exit(1)
