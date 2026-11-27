# -*- coding: utf-8 -*-
"""Auge-Tafel und zwei Augenfelder (14.11.2026).

WARUM DAS AUGE BESONDERS IST: Es ist das Lehrstueck der ganzen Seite. Seit den
1970er Jahren ist am Menschen gemessen, dass Cannabinoide den Augeninnendruck
senken - und bis heute ist daraus keine Behandlung geworden. Die Tafel muss
BEIDES sagen: die Wirkung UND warum sie nicht reicht (kurz, keine brauchbare
Zubereitung, Gewoehnung). Faellt der zweite Teil weg, liest sich die Tafel wie
eine Empfehlung gegen den Gruenen Star.

DIE FALLE: "Trockene Augen von Cannabis" ist eine bekannte Alltagsbeobachtung.
Die Mausbefunde zum Traenenfluss verleiten dazu, sie als belegt hinzustellen.
Auf dieser Seite steht dazu KEINE Messung am Menschen - die Tafel sagt das
ausdruecklich, und der Test verlangt diesen Satz.

GESCHLECHTSABHAENGIGKEIT: Der Traenenbefund gilt bei Maeusen nur fuer Weibchen
in dieser Form. Wer das weglaesst, verallgemeinert eine Messung, die
ausdruecklich zwischen den Geschlechtern unterscheidet.

DIE ZWEI FELDER sagten vorher beide "Wie THC". Das ist kein Beleg fuer einen
anderen Stoff - dieselbe Fehlerklasse wie am 13.11. bei Nabiximols und dem
Immunsystem. Jetzt steht dort, dass fuer den Stoff SELBST keine Augenstudie
vorliegt.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, io, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'
QUELLE = SEITE.replace('file://', '')

# 27.11.2026: vier Humanbelege und ein zweiter Tierbefund dazu.
NEU = ['39474241', '40838892', '39630463',
       '32852544',   # THC senkt den Traenenfluss bei MAENNLICHEN Maeusen
       '20805210',   # trockene Augen als gemeldete Nebenwirkung, randomisiert
       '42524865',   # OSDI gemessen, kein Unterschied (gegen ein Opioid)
       '885679']     # der einzige objektive Traenenmesswert: eher MEHR Traenen
TAFEL_MUSS = [
    'Seit den 1970er Jahren ist gemessen',
    'eine Behandlung ist daraus bis heute nicht geworden',
    'nicht ausreichend, um Cannabinoide gegen den Grünen Star zu empfehlen',
    'nur am Tier gemessen ist und dort vom Geschlecht abhängt',
    # 27.11.2026: Hier stand bis heute "Ob Cannabis beim Menschen die Augen
    # trocken macht, ist auf dieser Seite nicht belegt". Streng gelesen war das
    # wahr - eine Aussage ueber die Seite, nicht ueber die Welt. Als
    # Wissensaussage war es zu eng: Am Menschen ist gemeldet, gemessen und
    # teils nie geprueft, und der einzige objektive Traenenmesswert zeigt in
    # die ANDERE Richtung. Die Tafel traegt jetzt die Dreiteilung, und dieser
    # Test haelt alle drei Teile fest - fehlt einer, ist die Aussage wieder
    # schiefer als die Belege.
    'Am Menschen ist die Lage dreigeteilt',
    'Gemeldet, aber nicht gemessen',
    'Gemessen und berichtet',
    'Nie geprüft',
    'in die andere Richtung',
    'Schirmer-Test',
    'abgefragt am 27.11.2026',
]
TAFEL_VERBOTEN = [
    'hilft gegen den Grünen Star',
    'wirksam gegen Glaukom',
    'macht die Augen trocken',          # Alltagsbeobachtung als Befund
    'Cannabis trocknet die Augen aus',
    # Die alte, zu enge Verneinung darf nicht zurueckkommen.
    'die Augen trocken macht, ist auf dieser Seite nicht belegt',
]
FELD_MUSS = {
    'nab': ['Für Nabilon selbst trägt diese Seite keine Augenstudie'],
    'nbx': ['Für Nabiximols selbst trägt diese Seite keine Augenstudie'],
}


async def main():
    probleme = []
    T = io.open(QUELLE, encoding='utf-8').read()
    T = T[T.find('<title>'):]
    for p in NEU:
        if ("['%s'," % p) not in T: probleme.append('Beleg %s fehlt im Verzeichnis' % p)
        if ('[[%s]]' % p) not in T: probleme.append('Beleg %s wird nicht benutzt' % p)
    # "Wie THC" als Begruendung bei einem anderen Stoff - die Geschwisterregel
    for m in re.finditer(r"\bauge:\[\d,'((?:[^'\\]|\\.)*)'\]", T):
        if m.group(1).startswith('Wie THC') or m.group(1).startswith('Wie bei THC'):
            probleme.append('Ein Augenfeld begruendet wieder mit "Wie THC": %s' % m.group(1)[:70])

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1050})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1800)

        for sid in ('thc', 'nab', 'nbx'):
            await pg.locator('button.chip[data-id="%s"]' % sid).first.evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(260)
            await pg.locator('#or-auge').evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(280)
            t = await pg.inner_text('#organInfo')
            if '${' in t or '[[' in t: probleme.append('%s: Vorlagenrest in der Augentafel' % sid)
            if sid in FELD_MUSS:
                m = re.search(r'\n(Nicht untersucht|Schwache Wirkung|Deutliche Wirkung|Starke Wirkung)\.', t)
                if not m or m.group(1) != 'Schwache Wirkung':
                    probleme.append('%s/auge steht auf "%s", erwartet "Schwache Wirkung"'
                                    % (sid, m.group(1) if m else '??'))
                for s in FELD_MUSS[sid]:
                    if s not in t: probleme.append('%s/auge: fehlt »%s«' % (sid, s))
            if sid == 'thc':
                for s in TAFEL_MUSS:
                    if s not in t: probleme.append('Augentafel: fehlt »%s«' % s)
                for v in TAFEL_VERBOTEN:
                    if v in t: probleme.append('Augentafel: unerwuenscht »%s«' % v)
                for d in (' mg', 'Milligramm'):
                    if d in t: probleme.append('Augentafel: Dosisangabe')
                # Die Druesenreihe muss zusammenhaengen: Speichel und Schweiss
                for ziel, erw in (('mund', 'Mund'), ('skin', 'Haut')):
                    kn = pg.locator('#organInfo .xlink[data-organ="%s"]' % ziel)
                    if await kn.count() != 1:
                        probleme.append('Verweis auf %s fehlt' % ziel); continue
                    await kn.first.click(); await pg.wait_for_timeout(650)
                    titel = (await pg.inner_text('#organInfo')).split('\n')[0]
                    if erw not in titel:
                        probleme.append('Verweis %s fuehrt zu: %s' % (ziel, titel))
                    await pg.locator('#or-auge').evaluate(
                        "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
                    await pg.wait_for_timeout(250)
        print('  ok  Augentafel und zwei Felder geprueft')
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler: sys.exit(1)

asyncio.run(main())
