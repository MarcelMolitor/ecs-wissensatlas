# -*- coding: utf-8 -*-
"""Dauertest gegen den haeufigsten Fehler dieser Seite: 'gut belegt' ueber einem
Tier- oder Zellbefund, ohne dass der Text sagt, dass es einer ist.

WARUM: Am 12.11.2026 ist dieser Fehler an EINEM TAG viermal aufgetreten, drei
davon in Texten, die laenger so dastanden:
 1. l-alter: 'Mit dem Alter nimmt die Aktivitaet dieses Systems ab' - voellig
    ohne Beleg, tatsaechlich aus Tierversuchen, und die einzige Vermessung am
    lebenden Menschen sagt fuer Frauen das Gegenteil [[18077184]].
 2. thc.immune: 'Daempft Immunreaktionen ueber CB2' - am Menschen findet eine
    Sichtung von 40 klinischen Studien keine Aenderung [[39921765]].
 3. thc.fat: 'wird langsam wieder abgegeben' - ein Rattenbefund [[19681888]].
 4. Und einer davon war MEINER, zwanzig Minuten nach dem Veroeffentlichen:
    Im Interleukin-Reiter stand 'PEAs Hauptwirkung laeuft ueber PPAR-alpha' bei
    Belegstufe 'gut belegt' - gestuetzt auf einen Maeuse-Knockout [[15465922]],
    waehrend der Satz einen Weg AM MENSCHEN behauptete. Dieselbe Karte argumen-
    tiert gegen genau diesen Schluss bei anderen. Das faellt beim Schreiben
    nicht auf; es faellt beim Messen auf.

DIE REGEL, die daraus folgt und die dieser Test durchsetzt:
  Wenn ALLE Belege einer Aussage vom Typ Tierstudie, Zellversuch, Grundlagen
  oder Modellrechnung sind, und die Aussage mit 'gut belegt' ausgezeichnet ist,
  dann MUSS der Text der Aussage selbst die Versuchsart nennen - Maus, Ratte,
  Zellversuch, Struktur, Hefe, Knockout und so weiter.

Das verbietet den Befund nicht. Eine Aussage ueber Maeuse darf 'gut belegt'
sein - sie muss nur sagen, dass sie von Maeusen handelt. Verboten ist nur der
unmarkierte Sprung von der Maus zum Menschen.

STAND BEI EINFUEHRUNG: 0 Verstoesse bei 185 belegten Aussagen. Es gibt also
keine Ausnahmeliste, und es soll keine geben. Wer eine braucht, hat
wahrscheinlich den Satz falsch geschrieben, nicht den Test.

BEWUSST NICHT GEPRUEFT: Belegstufe 'teils belegt' auf Tierdaten. Das ist die
schwaechere Auszeichnung und traegt den Vorbehalt schon im Namen. Falls diese
Stufe einmal auffaellt, gehoert sie hier dazu - bisher ist sie es nicht.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io, re, sys

QUELLE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'

# Typen, die KEINE Aussage ueber Menschen tragen.
NICHT_MENSCH = {'Tierstudie', 'Zellversuch', 'Grundlagen', 'Modellrechnung'}
# Woerter, mit denen ein Text seine Versuchsart selbst offenlegt.
NENNT = re.compile(r'Maus|Mäus|Ratte|Hamster|Meerschwein|Schwein|Tier|Zell|Struktur'
                   r'|Röntgen|Hefe|Anatomie|Labor|Knockout|im Versuch', re.I)


def main():
    S = io.open(QUELLE, encoding='utf-8').read()
    typ = {m.group(1): m.group(7) for m in re.finditer(
        r"\['(\d{7,8})',(\d{4}),'([^']*)','([^']*)','((?:[^'\\]|\\.)*)','([^']*)','([^']*)'", S)}
    if len(typ) < 400:
        print('Probleme: nur %d Belege erkannt - das Muster passt nicht mehr' % len(typ))
        sys.exit(1)

    paare = re.compile(r"cite\('((?:[^'\\]|\\.)*)'\)\}\s*\$\{ev\('(\w)'\)").findall(S)
    if len(paare) < 150:
        print('Probleme: nur %d belegte Aussagen gefunden - das Muster passt nicht mehr'
              % len(paare))
        sys.exit(1)
    print('  %d Belege im Verzeichnis, %d belegte Aussagen' % (len(typ), len(paare)))

    probleme = []
    geprueft = 0
    for txt, lvl in paare:
        ps = re.findall(r'\[\[(\d{7,8})\]\]', txt)
        if not ps or lvl != 'g':
            continue
        arten = {typ.get(p, '?') for p in ps}
        if not arten or not arten <= NICHT_MENSCH:
            continue
        geprueft += 1
        if not NENNT.search(txt):
            probleme.append('"gut belegt" auf %s, ohne die Versuchsart zu nennen: %s (%s)'
                            % (sorted(arten), re.sub(r'\s+', ' ', txt)[:150], ps))
    print('  %d Aussagen mit "gut belegt" ruhen allein auf Tier/Zelle/Grundlagen' % geprueft)
    if not probleme:
        print('  ok  jede davon nennt ihre Versuchsart im eigenen Text')

    print('Probleme:', probleme or 'keine')
    if probleme:
        sys.exit(1)


main()
