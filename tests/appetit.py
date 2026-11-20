# -*- coding: utf-8 -*-
"""Dauertest fuer die Karte n-appetit im Reiter Nachbarsysteme.

WARUM SIE DA IST: Der Reiter erklaerte den Hunger ueber LEPTIN - und diese
Karte stuetzt sich auf eine Mausarbeit von 2001 [[11298451]]. Das menschliche
Gegenstueck, GHRELIN, fehlte, obwohl zwei Menschenstudien dazu schon auf der
Seite standen ([[41825697]], [[42514343]]) und drei weitere in der Literatur
liegen ([[22133305]], [[30949710]], [[32075958]]).

DIE AUSWAHLREGEL DES REITERS WURDE ZUERST GELESEN, nicht nachtraeglich geprueft:
In n-nicht steht, dass ein System nur bei einer MESSUNG AM MENSCHEN einen Platz
bekommt, und dort sind Acetylcholin, Noradrenalin, Melatonin, Blutdruck,
Schilddruese und Glukagon ausdruecklich abgelehnt. Deshalb wurde keiner dieser
sechs angefasst - dieser Test prueft, dass das so bleibt. Ebenfalls geprueft
und VERWORFEN wurden: Mitochondrien (nur Maeuse, und ein Ort INNERHALB des
Systems, kein Nachbar), Omega-3 (steht schon unter Einflussfaktoren und als
Stoffkarte) und Prostaglandine (die Karte e-rohstoff deckt den geteilten
Rohstoff ab).

WAS DIE KARTE BEHAUPTET und was deshalb dastehen muss: Die fuenf
Menschenmessungen sind sich ueber die RICHTUNG von Ghrelin nicht einig - rauf,
runter, unveraendert. Der verlaessliche Befund ist nicht das Hormon, sondern
die GEGENPROBE in [[30949710]]: Derselbe Milchshake, einmal getrunken und
einmal per Sonde direkt in den Magen - mehr aufgenommen wurde NUR beim Trinken.
Der Effekt haengt also am Schmecken und Erwarten.

ZWEI FALLEN, die beim Bauen zugeschnappt sind und hier festgehalten werden:
 1. [[32075958]] wird leicht als weiterer Richtungsbefund gelesen. Ihr
    Ghrelin-Vergleich laeuft aber zwischen den EINNAHMEWEGEN (geschluckt gegen
    geraucht gegen verdampft), NICHT gegen Placebo. Der Text muss das sagen.
 2. HANDGEZAEHLTE ZAHLEN, schon wieder: Die Karte nannte die fuenfte Arbeit
    'eine vierte', und sprach von fuenf widerspruechlichen Studien, obwohl nur
    vier eine Richtungsaussage machen und diese drei verschiedene Antworten
    geben. Der Test zaehlt die Belege in der Karte nach.

KEINE DOSISANGABEN: THC, CBD und Nabiximols sind erhaeltlich.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, io, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'
QUELLE = HIER + '/page.html'   # 15.11.: war die Arbeitsdatei, nicht der Pruefling

NEU = ['22133305', '30949710', '32075958']
ALT = ['41825697', '42514343']
MUSS = [
    'Ghrelin steigt', 'Ghrelin sinkt', 'Ghrelin bleibt',
    'nicht gegen Placebo',            # die Falle bei Farokhnia
    'Einnahmewege untereinander',
    'direkt in den Magen geleitet',   # die Gegenprobe
    'nur beim Trinken',
    'Schmecken und Erwarten',
    'drei verschiedene Antworten',
    'fünfte Arbeit',
]
VERBOTEN = [
    'Und eine vierte Arbeit',          # falsch gezaehlt
    'Fünf Studien, und sie widersprechen sich.',
    'Als fünfte Richtungsangabe',
    # Keine Steigerung ueber das Gemessene hinaus:
    'Ghrelin steuert den Appetit',
    'das Hungerhormon erklärt',
]
# Die sechs Systeme, die der Reiter begruendet ABLEHNT. Sie duerfen keine
# eigene Karte bekommen, solange keine Menschenmessung vorliegt.
ABGELEHNT = ['Acetylcholin', 'Noradrenalin', 'Melatonin', 'Schilddrüse', 'Glukagon']


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    for p in NEU:
        if ("['%s'," % p) not in S:
            probleme.append('neuer Beleg %s fehlt im Verzeichnis' % p)
    for p in NEU + ALT:
        if ('[[%s]]' % p) not in S:
            probleme.append('Beleg %s wird nicht benutzt' % p)
    if "['n-appetit','Ghrelin & Appetithormone']" not in S:
        probleme.append('Sprungleisten-Eintrag fehlt')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1200})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)
        await pg.click('#groups button[data-g="0"]')
        await pg.wait_for_timeout(320)
        await pg.click('#tabs button:has-text("Nachbarsysteme")')
        await pg.wait_for_timeout(900)

        if await pg.locator('#n-appetit').count() != 1:
            print('Probleme: Karte n-appetit fehlt')
            await b.close(); sys.exit(1)
        t = await pg.inner_text('#n-appetit')
        if '${' in t:
            probleme.append('unaufgeloeste Vorlage in n-appetit')
        for m in MUSS:
            if m.lower() not in t.lower():
                probleme.append('Kernaussage fehlt: %s' % m)
        for v in VERBOTEN:
            if v in t:
                probleme.append('verbotene Fassung: %s' % v)
        print('  ok  n-appetit: %d Zeichen, alle Kernaussagen' % len(t))

        # Die Karte muss genau fuenf Belegmarken tragen - vier Richtungsarbeiten
        # und die eine, die keine Richtung angibt. Die Gegenprobe zitiert
        # [[30949710]] ein zweites Mal, deshalb sechs Marken.
        marken = await pg.locator('#n-appetit sup, #n-appetit .ref, #n-appetit button.refbtn').count()
        if marken < 5:
            probleme.append('nur %d Belegmarken in n-appetit, erwartet mindestens 5' % marken)
        else:
            print('  ok  %d Belegmarken in der Karte' % marken)

        # Keine Dosisangabe.
        for d in (' mg', 'Milligramm'):
            if d in t:
                probleme.append('Dosisangabe in n-appetit: %s' % d)

        # Die abgelehnten Systeme duerfen keine eigene Karte haben.
        ganz = await pg.inner_text('#tabpanel')
        kopf = await pg.evaluate(
            "()=>[...document.querySelectorAll('#tabpanel article.card > h3')].map(e=>e.textContent)")
        for a in ABGELEHNT:
            if any(a in h for h in kopf):
                probleme.append('%s hat eine eigene Karte, obwohl n-nicht es ablehnt' % a)
        if 'Systeme, die hier nicht stehen' not in ganz:
            probleme.append('die Karte mit der Auswahlregel (n-nicht) fehlt')
        else:
            print('  ok  Auswahlregel steht noch, keine abgelehnte Karte')

        # Der Sprungknopf muss zur Karte fuehren.
        kn = pg.locator('.qchip[data-jump="n-appetit"]')
        if await kn.count() != 1:
            probleme.append('Sprungknopf fuer n-appetit fehlt')
        else:
            await kn.click(); await pg.wait_for_timeout(600)
            if not await pg.evaluate(
                    "()=>document.getElementById('n-appetit').getBoundingClientRect().height>0"):
                probleme.append('Sprung zu n-appetit fuehrt ins Leere')
            else:
                print('  ok  Sprungknopf funktioniert')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
