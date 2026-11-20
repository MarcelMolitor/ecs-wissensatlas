# -*- coding: utf-8 -*-
"""Dauertest fuer die Immunfelder aller Stoffe - und gegen Wartungsgeschichte
im Lesetext.

TEIL 1: KEIN IMMUNFELD OHNE BELEG.
Das Immunfeld war das haeufigste unbelegte Organfeld der Seite: acht Stoffe.
Nach dem Interleukin-Reiter ist klar, warum das brisant ist - eine Sichtung von
40 klinischen Studien [[39921765]] findet bei Cannabis am Menschen KEINE
Aenderung von Botenstoffen, T-Zell-Zahlen oder Entzuendungswerten. Ein
unbelegtes Immunfeld ist deshalb eher eine UEBERZIEHUNG als eine fehlende
Quelle. Am 13.11.2026 geschlossen, ohne eine einzige neue Quelle - es fehlten
nicht Belege, sondern deren richtige Zuordnung.

Der schwerste Fund dabei: Nabiximols trug den Satz 'THC daempft Immunreaktionen
ueber CB2' - also genau den, der am 12.11. fuer THC zurueckgebaut wurde. Ich
hatte THCs Feld korrigiert und das gleichlautende Feld des
Kombinationspraeparats stehen gelassen. Der Test prueft diesen Satz
ausdruecklich.

DREI DICHTESTUFEN WAREN FALSCH:
  bcp  3 -> 2  'Starke Wirkung' bei einem Stoff, dessen eigene Begruendung
               sagt: 'Am Menschen fehlen Studien zu diesen Wirkungen.'
               (Am 14.11.2026 weiter auf 1 - der Schritt auf 2 war zu kurz.)
  lena 2 -> 1  zwei grosse Studien am Menschen ohne Wirkung
  mtz  1 -> 0  die Stufe sagte 'Schwache Wirkung', der Text sagte, die
               Blutbildstoerung laufe NICHT ueber dieses System

TEIL 2: KEINE WARTUNGSGESCHICHTE IM LESETEXT.
Diese Fehlerklasse ist viermal aufgetreten: 'stand hier lange ohne Beleg'
(Kleinhirn), 'das stand bisher nirgends' (Kalzium), 'deshalb steht hier keine
starke Wirkung' (beta-Caryophyllen, 13.11.) und 'Er stand hier bisher
ueberhaupt nicht' (Oestrogen-Karte, ein aelterer Fall, erst bei dieser
Gesamtpruefung gefunden). Ein Leser will wissen, was belegt ist - nicht, was
die Seite frueher nicht hatte.

ABGRENZUNG, damit der Test nicht das Falsche verbietet: Saetze, die begruenden,
WARUM ein Befund aufgenommen wurde ('Sie steht hier, weil Weglassen auch eine
Aussage waere'), sind erwuenscht und bleiben. Verboten sind nur Aussagen ueber
den FRUEHEREN Zustand der Seite. Deshalb prueft der Test konkrete Wendungen und
keine Muster wie 'steht hier'.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, io, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'
QUELLE = sys.argv[1].replace('file://', '') if len(sys.argv) > 1 else HIER + '/page.html'

# Erwartete Dichtestufen der drei korrigierten Felder.
# bcp am 14.11.2026 weiter von 2 auf 1 gesenkt: Die Skala hat seither eine
# erklaerte Bedeutung (reine Tier- und Zellbefunde hoechstens 'schwach'), und
# bcp/immune sagt selbst 'Am Menschen fehlen Studien'. Siehe t/wirkstufe.py.
STUFEN = {'bcp': '1', 'lena': '1', 'mtz': '0'}
# Der Satz, der fuer THC zurueckgebaut wurde und nirgends zurueckkommen darf.
UEBERZOGEN = [
    'THC dämpft Immunreaktionen über CB2.',
    'Dämpft Immunreaktionen über CB2.',
]
# Aussagen ueber den FRUEHEREN Zustand der Seite.
WARTUNG = [
    'stand hier lange', 'stand bisher', 'stand hier bisher', 'das stand bisher',
    'deshalb steht hier keine', 'fehlte bis zu dieser Karte', 'bis zu dieser Karte',
    'war bisher nicht belegt', 'stand hier überhaupt nicht',
]


def stoffbloecke(S):
    """id -> organs-Block, mit Klammerzaehlen statt Regex."""
    out = {}
    for m in re.finditer(r"\{id:'(\w+)',", S):
        sid = m.group(1)
        i = m.start(); d = 0; k = i
        while True:
            if S[k] == '{': d += 1
            elif S[k] == '}':
                d -= 1
                if d == 0: break
            k += 1
        o = S[i:k + 1]
        if 'organs:{' in o:
            out[sid] = o
    return out


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    bl = stoffbloecke(S)
    if len(bl) < 25:
        print('Probleme: nur %d Stoffe erkannt - das Muster passt nicht mehr' % len(bl))
        sys.exit(1)

    ohne = []
    for sid, o in bl.items():
        f = re.search(r"\bimmune:\[(\d),'((?:[^'\\]|\\.)*)'\]", o)
        if not f:
            continue
        stufe, txt = f.group(1), f.group(2)
        if '[[' not in txt:
            ohne.append(sid)
        if sid in STUFEN and stufe != STUFEN[sid]:
            probleme.append('%s.immune steht auf Stufe %s, erwartet %s'
                            % (sid, stufe, STUFEN[sid]))
    print('  %d Stoffe mit Immunfeld, davon ohne Beleg: %d' % (
        sum(1 for o in bl.values() if 'immune:[' in o), len(ohne)))
    if ohne:
        probleme.append('Immunfelder ohne Beleg: %s' % sorted(ohne))
    else:
        print('  ok  jedes Immunfeld traegt einen Beleg')
    if not [p for p in probleme if 'Stufe' in p]:
        print('  ok  die drei korrigierten Dichtestufen stehen richtig')

    # Der zurueckgebaute Satz darf in KEINEM Stoff wieder auftauchen.
    for sid, o in bl.items():
        for u in UEBERZOGEN:
            if u in o:
                probleme.append('%s traegt den zurueckgebauten Satz: %s' % (sid, u))

    # Wartungsgeschichte im Seitentext - ABER die Aenderungsliste const NEU
    # ausgenommen: Sie fuehrt absichtlich, was sich zuletzt geaendert hat
    # ('Korrekturen zuerst - sie sind die ehrlichere Information'), und genau
    # dort IST der fruehere Zustand die Information. Beim ersten Lauf hat dieser
    # Test sie als Fehler gemeldet; das war ein Fehlalarm, und ohne diese
    # Ausnahme haette er dazu verleitet, eine bewusste Einrichtung der Seite
    # abzubauen. Ein Test darf nicht strenger sein als die Regel, die er schuetzt.
    B = S[S.find('<title>'):]
    mneu = re.search(r'const NEU\s*=\s*\[', B)
    if mneu:
        i = mneu.end(); d = 1; k = i
        while d:
            if B[k] == '[': d += 1
            elif B[k] == ']': d -= 1
            k += 1
        B = B[:mneu.start()] + B[k:]
    for w in WARTUNG:
        n = B.count(w)
        if n:
            i = B.find(w)
            probleme.append('Wartungsgeschichte im Lesetext (%dx): "%s" bei: %s'
                            % (n, w, re.sub(r'\s+', ' ', B[max(0, i - 60):i + 80]).strip()))
    if not [p for p in probleme if 'Wartungsgeschichte' in p]:
        print('  ok  keine Aussage ueber den frueheren Zustand der Seite')

    # Gerendert: die acht Felder muessen Belegmarken zeigen.
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1100})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)
        for sid in ('aea', 'cbd', 'bcp', 'inh', 'cbn', 'mtz', 'lena', 'nbx'):
            kn = pg.locator('button.chip[data-id="%s"]' % sid)
            if not await kn.count():
                probleme.append('kein Auswahlknopf fuer %s' % sid); continue
            await kn.first.evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(380)
            await pg.locator('#or-immune').evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(340)
            t = await pg.inner_text('#organInfo')
            if '${' in t:
                probleme.append('%s: unaufgeloeste Vorlage im Immunfeld' % sid)
            if sid == 'mtz' and 'Agranulozytose' not in t:
                probleme.append('die Agranulozytose-Warnung ist aus dem Immunfeld verschwunden')
        print('  ok  alle acht Immunfelder rendern')
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
