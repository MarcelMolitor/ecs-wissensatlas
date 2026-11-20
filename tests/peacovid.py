# -*- coding: utf-8 -*-
"""Dauertest fuer die Karte c-covid-pea: PEA und OEA nach COVID-19.

DIE FRAGE WAR: Wie haben sich OEA und PEA nach Corona veraendert? DIE ANTWORT
HAT ZWEI HAELFTEN, und die erste ist ein NEIN - genau deshalb gehoert sie auf
die Seite, denn die Frage ist naheliegend und wird oft gestellt.

(a) Die PEGEL von OEA und PEA nach COVID sind NICHT gemessen. Die Messungen am
    Menschen betreffen die klassischen Endocannabinoide 2-AG und Anandamid,
    waehrend der akuten Erkrankung: [[37713293]] (stand schon da) und
    [[36851787]] (neu, 200 Patienten gegen 35 Gesunde). OEA und PEA sind keine
    klassischen Endocannabinoide - sie binden CB1 und CB2 nicht - und waren
    dort nicht die gemessene Groesse.

(b) Gemessen ist PEA als MITTEL: [[36084236]] waehrend der Erkrankung (stand
    seit demselben Tag auf der Seite, aber NUR im Interleukin-Reiter - der
    COVID-Reiter wusste nichts davon) und [[37189728]] danach, bei der
    Riechstoerung: randomisiert, 90 Tage, Ergebnis GESPALTEN - fuer den
    Riechverlust wirksam, fuer die Riechverzerrung kaum. [[36676175]] gibt die
    Grenze derselben Behandlung.

DIE WICHTIGSTE EINSCHRAENKUNG, die dastehen MUSS: Die Riechstudie prueft eine
KOMBINATION aus PEA und Luteolin, und beide Gruppen bekamen Riechtraining. Der
Effekt laesst sich NICHT PEA allein zuschreiben - dieselbe Falle wie bei den
Terpenen und bei Maca.

ZWEI FEHLER BEIM BAU, beim Lesen des gerenderten Texts gefunden:
 1. Der Schlusssatz begann mit 'Fuer deine Frage heisst das' - die Seite kann
    sich nicht auf eine Frage beziehen, die der Leser nicht gestellt hat. (Das
    Du selbst ist in Ordnung, die Seite duzt an 31 Stellen.)
 2. 'zwei von drei Entzuendungswerten gesenkt' war eine erfundene Quote: Die
    Arbeit hatte SECHS Hauptzielwerte. Jetzt stehen die Werte selbst da -
    IL-1beta und IL-2 gesenkt, IL-6 nicht. Das war an diesem und am Vortag der
    fuenfte Zahlenfehler dieser Art.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, io, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'
QUELLE = HIER + '/page.html'   # 15.11.: war die Arbeitsdatei, nicht der Pruefling

NEU = ['36851787', '37189728', '36676175']
MUSS = [
    'keine Messung am Menschen auffindbar',   # die ehrliche erste Haelfte
    'keine klassischen Endocannabinoide',
    'für den Riechverlust wirksam',
    'für die Riechverzerrung kaum',
    'Kombination aus PEA und Luteolin',       # die zentrale Einschraenkung
    'nicht PEA allein zuschreiben',
    'IL-1β und IL-2 senkte, IL-6 aber nicht',
]
VERBOTEN = [
    'Für deine Frage heißt das',          # Bezug auf eine ungestellte Frage
    'zwei von drei Entzündungswerten',    # erfundene Quote
    'PEA senkt die Entzündung nach COVID',  # Wirkung als Tatsache
    'PEA-Spiegel sinken nach',            # behauptete Pegelaenderung
    'PEA hilft gegen Long COVID',
]


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    for p in NEU:
        if ("['%s'," % p) not in S:
            probleme.append('Beleg %s fehlt im Verzeichnis' % p)
        if ('[[%s]]' % p) not in S:
            probleme.append('Beleg %s wird nicht benutzt' % p)

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1200})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)
        auf = False
        for g in range(4):
            await pg.click('#groups button[data-g="%d"]' % g)
            await pg.wait_for_timeout(250)
            if await pg.locator('#tabs button:has-text("COVID-19")').count():
                await pg.locator('#tabs button:has-text("COVID-19")').click()
                await pg.wait_for_timeout(900); auf = True; break
        if not auf:
            print('Probleme: COVID-Reiter nicht gefunden'); await b.close(); sys.exit(1)
        if await pg.locator('#c-covid-pea').count() != 1:
            print('Probleme: Karte c-covid-pea fehlt'); await b.close(); sys.exit(1)

        t = await pg.inner_text('#c-covid-pea')
        if '${' in t:
            probleme.append('unaufgeloeste Vorlage in c-covid-pea')
        for m in MUSS:
            if m not in t:
                probleme.append('Kernaussage fehlt: %s' % m)
        for v in VERBOTEN:
            if v in t:
                probleme.append('unerwuenschte Fassung: %s' % v)
        for d in (' mg', 'Milligramm'):
            if d in t:
                probleme.append('Dosisangabe: %s' % d.strip())
        print('  ok  c-covid-pea: %d Zeichen, alle Kernaussagen, keine Dosisangabe' % len(t))

        # Die Karte muss vier Belegmarken tragen - drei neue plus die vom
        # PEA-Versuch waehrend der Erkrankung.
        n = await pg.locator('#c-covid-pea sup, #c-covid-pea .ref, '
                             '#c-covid-pea button.refbtn').count()
        if n < 4:
            probleme.append('nur %d Belegmarken, erwartet mindestens 4' % n)
        else:
            print('  ok  %d Belegmarken' % n)

        if await pg.locator('.qchip[data-jump="c-covid-pea"]').count() != 1:
            probleme.append('Sprungknopf fehlt')
        # Der Verweis in den Interleukin-Reiter muss tragen - dort steht die
        # Einordnung des Fettsaeureamid-Zweigs.
        kn = pg.locator('#c-covid-pea .xlink[data-tab="interleukine"][data-card="i-bruch"]')
        if await kn.count() != 1:
            probleme.append('Verweis auf i-bruch fehlt')
        else:
            await kn.click()
            await pg.wait_for_timeout(900)
            if not await pg.evaluate("()=>{const c=document.getElementById('i-bruch');"
                                     " return c ? c.getBoundingClientRect().height>0 : false;}"):
                probleme.append('der Verweis auf i-bruch fuehrt ins Leere')
            else:
                print('  ok  Sprungknopf und Verweis funktionieren')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
