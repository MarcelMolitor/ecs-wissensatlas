# -*- coding: utf-8 -*-
"""Dosisregel: Fuer erhaeltliche Stoffe steht keine Milligrammzahl auf der Seite.

Am 20.11.2026 war diese Regel an 16 Stellen verletzt - CBD (300/50 mg und
100 mg/ml), die THC-Tablette bei Demenz (1,5 mg), THCV (10 mg), OEA (200 mg)
und verdampftes THC mit Limonen (30/15 mg). Gefunden wurde das nicht von einem
Test, sondern zufaellig von einer Zusicherung in einem Patch-Skript.

Hereingekommen sind die Zahlen ueber die Kernaussagen neuer Quellen: die Regel
wurde beim Schreiben von Kartentexten angewandt, nicht beim Eintragen von
Quellen - und von dort wanderten sie in die Kartentexte.

Erlaubt bleiben Dosen von Forschungsstoffen, die niemand bekommen kann, und
von Rimonabant. Ob Letzteres so bleibt, ist eine offene Entscheidung von
Marcel; dieser Test setzt den Stand vom 20.11.2026 fest, damit sich nichts
unbemerkt verschiebt.

WICHTIG: Die Seite schreibt Masseinheiten teils mit normalem, teils mit
geschuetztem Leerzeichen (1,5\\xa0mg). Ein Muster mit festem Leerzeichen findet
nur die Haelfte - genau daran waere die Suche am 20.11. fast gescheitert.
"""
import io, re, sys
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))

QUELLE = sys.argv[1].replace('file://', '') if len(sys.argv) > 1 else HIER + '/page.html'
S = io.open(QUELLE, encoding='utf-8').read()

SP = '[  ]?'                       # beide Leerzeichen, auch keines
EINHEIT = r'\d[\d.,]*' + SP + r'(?:mg|Milligramm|µg|mcg|mg/ml|mg/kg|g/kg)\b'

# Stoffe, die man kaufen oder verschrieben bekommen kann. Fuer sie gilt die Regel.
ERHAELTLICH = [
    ('CBD',        r'\bCBD\b|Cannabidiol'),
    ('THC',        r'\bTHC\b|Dronabinol|Nabiximols|Nabilon|Tetrahydrocannabinol'),
    ('THCV',       r'\bTHCV\b'),
    ('CBG/CBN/CBC', r'\bCBG\b|\bCBN\b|\bCBC\b|\bCBDV\b|\bCBDA\b'),
    ('PEA',        r'\bPEA\b|Palmitoylethanolamid'),
    ('OEA',        r'\bOEA\b|Oleoylethanolamid'),
    ('Paracetamol', r'Paracetamol'),
]

# Stoffe, deren Studiendosen stehen duerfen: nicht erhaeltlich oder vom Markt.
AUSNAHMEN = re.compile(
    r'Rimonabant|Monlunabant|Taranabant|AEF0117|PF-04457845|JZP150|'
    r'BIA 10-2474|GW842166|Nimacimab|ZYN002|BMS-986368|Naproxen|Ibuprofen|'
    r'Semaglutid|Metformin|Sulfonylharnstoff'
)

# Das Kopfprotokoll beschreibt Regelbrueche und zitiert die Zahlen dabei. Es ist
# Entwicklungsdokumentation, nicht Seitentext - die Zitate muessen stehen bleiben.
protokoll = re.search(r'ENTWICKLUNGSPROTOKOLL|Kopfprotokoll', S)
UMFANG = 200000   # das Protokoll steht im Kopf der Datei

probleme = []
for m in re.finditer(EINHEIT, S):
    if m.start() < UMFANG:
        continue                       # Kopfprotokoll
    umfeld = S[max(0, m.start() - 190):m.start() + 110]
    if AUSNAHMEN.search(umfeld):
        continue
    for name, muster in ERHAELTLICH:
        if re.search(muster, umfeld):
            probleme.append((m.start(), name, m.group().strip(),
                             umfeld[150:260].replace('\n', ' ')))
            break

print('geprueft:', QUELLE)
print('Mengenangaben insgesamt:', len(re.findall(EINHEIT, S)))
print('davon hinter dem Kopfprotokoll:',
      len([m for m in re.finditer(EINHEIT, S) if m.start() >= UMFANG]))

if probleme:
    print('FEHLER: %d Dosisangabe(n) zu erhaeltlichen Stoffen:' % len(probleme))
    for pos, name, zahl, text in probleme:
        print('  @%-8d %-6s %-10s ...%s...' % (pos, name, zahl, text))
    sys.exit(1)

print('Probleme: keine')

# Gegenprobe, damit der Test nicht stumm gruen wird: eine eingebaute
# Dosisangabe muss er finden. Ohne diese Probe koennte ein kaputtes Muster
# ewig durchlaufen - der Fehler, der 22 Tests eine Woche gruen hielt.
probe = S[:UMFANG + 50] + '\nCBD half bei 300 mg deutlich besser.\n' + S[UMFANG + 50:]
treffer = 0
for m in re.finditer(EINHEIT, probe):
    if m.start() < UMFANG:
        continue
    umfeld = probe[max(0, m.start() - 190):m.start() + 110]
    if AUSNAHMEN.search(umfeld):
        continue
    if any(re.search(mu, umfeld) for _, mu in ERHAELTLICH):
        treffer += 1
assert treffer == 1, 'Gegenprobe: eingebaute Dosisangabe nicht gefunden (%d)' % treffer
print('Gegenprobe: eingebaute Dosisangabe wird gefunden')
