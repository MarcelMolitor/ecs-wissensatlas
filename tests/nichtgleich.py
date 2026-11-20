# -*- coding: utf-8 -*-
"""Dauertest fuer die Karte g-nichtgleich und die Korrektur in l-alter.

WARUM: Am 12.11.2026 nach weiteren Hirnregionen gesucht. Gegen die eigenen
Ankerarbeiten [[2308954]] und [[9472392]] ist der Bestand vollstaendig - der
einzige ernsthafte Kandidat, der VAGUSKERN, wurde geprueft und VERWORFEN, weil
die Hirnstamm-Tafel ihn bereits vollstaendig erzaehlt (Doppelung, derselbe
Fehler wie bei aea.repro am 09.11.).

Die Suche fand dafuer etwas anderes: Die Karte l-alter begann mit dem Satz,
dass die Aktivitaet des Systems mit dem Alter abnimmt - OHNE JEDEN BELEG und
als allgemeine Tatsache, obwohl er aus Tierversuchen stammt. Die einzige
Vermessung am lebenden Menschen [[18077184]] (50 Freiwillige, 18-69 Jahre,
radioaktiv markierter Messstoff) sagt fuer Frauen das GEGENTEIL: Die Bindung
an CB1 steigt mit dem Alter, bei Maennern nicht.

GEPRUEFT WERDEN DESHALB DREI DINGE, die beim Einbau alle schiefgehen koennten:
 1. l-alter darf die Abnahme nie wieder als unbelegte Tatsache behaupten. Der
    Test verlangt die Zuschreibung an Tierversuche UND den Menschenbefund.
 2. Die neue Karte darf die zweite Angabe derselben Arbeit (hoehere Werte bei
    Maennern) nicht ohne ihren Vorbehalt fuehren - sie ist nicht fuer die Zahl
    der gleichzeitig verglichenen Hirnorte korrigiert.
 3. Die Karte darf die beiden Messarten nicht gegeneinander ausspielen.
    Bindungsstellen in totem Gewebe und Aufnahme am Lebenden sind zwei
    verschiedene Groessen; wer sie gleichsetzt, baut aus der Korrektur einen
    neuen Fehler.
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

# Kernaussagen der neuen Karte, wortgenau gegen den gerenderten Text geprueft.
MUSS_NICHTGLEICH = [
    'Gewebe nach dem Tod',          # die Grundlage der ganzen Karte
    '50 Freiwillige',               # die Menschenmessung, nicht Tier
    'Alterseffekt nicht',           # bei Maennern nicht - keine Verallgemeinerung
    'nicht dafür korrigiert',       # der Vorbehalt zur zweiten Angabe
    'fehlende Dimension',           # die Pointe: kein Hirnteil, eine Dimension
    # Am 13.11.2026 ergaenzt: Die Karte sagte nicht, dass sie eine
    # ERWACHSENENkarte ist. Der groesste Altersunterschied von allen stand nur
    # in der Basalganglien-Tafel - dieselbe Ankerarbeit hat ein foetales und
    # zwei Saeuglingsgehirne vermessen, mit deutlich hoeheren Dichten.
    'acht erwachsene',
    'Erwachsenenkarte',
    'Säuglingsgehirne',
    'Ein Kindergehirn würde diese Karte',
]
# Formulierungen, die aus der Korrektur einen neuen Fehler machen wuerden.
VERBOTEN_NICHTGLEICH = [
    'widerlegt die Karte',
    'die Karte ist falsch',
    'bei Frauen und Männern gleich',
]
MUSS_ALTER = [
    'stammt aus Tierversuchen',     # die Zuschreibung, die vorher fehlte
    'nur bei den Frauen',           # der Menschenbefund steht daneben
]
# Die beiden GESCHWISTERSTELLEN. Sie standen zuerst unveraendert da, waehrend
# l-alter schon korrigiert war - die Seite widersprach sich also selbst, und
# zwar sichtbarer als vorher. Deshalb werden sie mitgeprueft.
MUSS_FAZIT = [
    'an Tieren gemessen',           # nicht mehr blankes "ist gemessen"
    'je nach Geschlecht',           # der Menschenbefund gehoert dazu
]
VERBOTEN_FAZIT = [
    'Dass es im Alter nachlässt, ist gemessen.',
]
MUSS_INTRO = ['im Tierversuch nimmt es im Alter ab']
VERBOTEN_INTRO = ['und es nimmt im Alter ab']


# Am 13.11.2026 ergaenzt: die Karte g-abbau. Sie erweitert die Hirnkarte auf
# einer Achse, die es vorher nicht gab - die BRAIN-Eintraege nennen FAAH und
# MAGL null Mal, obwohl die Seite sonst 263 bzw. 73 Nennungen hat. Der Befund
# [[27345297]] verhaelt sich umgekehrt zur Rezeptorkarte: Die Senkung des
# abbauenden Enzyms bei Konsumenten ist NICHT regionsspezifisch. Genau das ist
# der Grund, warum es KEINE zweite Kartenebene gibt - ein Umschalter wuerde
# eine Ortsabhaengigkeit behaupten, die niemand gemessen hat.
MUSS_ABBAU = [
    '14 bis 20 Prozent niedriger',
    'in allen untersuchten Regionen',
    'zehn Konsumenten',            # die kleine Gruppe steht dabei
    'vorausgeht oder aus ihm folgt',   # Ursache offen, von den Autoren selbst
    'keine gezeigte Ursache',      # Impulsivitaet
    'Eine Karte kann nur zeigen, was sich örtlich unterscheidet',
]
VERBOTEN_ABBAU = [
    'liegt ein Vielfaches',        # unbelegtes Verhaeltnis, ersetzt
    'Dauerkonsum senkt den Abbau',  # Ursache als Tatsache
    'FAAH-Karte',                   # es gibt keine regionale Enzymkarte
]


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()

    # Der Beleg muss im Verzeichnis stehen, mit DOI - nicht nur im Kartentext.
    if not re.search(r"18077184.*?10\.1016/j\.neuroimage\.2007\.10\.053", S):
        probleme.append('KEY-Eintrag 18077184 fehlt oder ohne DOI')
    else:
        print('  ok  Beleg 18077184 im Verzeichnis, mit DOI')
    if "['g-nichtgleich','Nicht bei allen gleich']" not in S:
        probleme.append('Sprungleisten-Eintrag fuer g-nichtgleich fehlt')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1200})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)

        # Die Reiter werden erst beim Oeffnen erzeugt - ohne diesen Schritt ist
        # die Karte gar nicht im Dokument, und der Test wuerde sie als fehlend
        # melden, obwohl sie da ist.
        await pg.click('#groups button[data-g="0"]')
        await pg.wait_for_timeout(300)
        await pg.click('#tabs button:has-text("Im Gehirn")')
        await pg.wait_for_timeout(700)

        async def karte(kid, muss, verboten):
            el = pg.locator('#' + kid)
            if await el.count() != 1:
                probleme.append('Karte %s fehlt' % kid)
                return
            txt = await el.inner_text()
            if not txt.strip():
                probleme.append('Karte %s ist leer - falscher Reiter offen?' % kid)
                return
            # Ein nicht aufgeloestes Template waere ein stiller Totalausfall.
            if '${' in txt:
                probleme.append('%s: unaufgeloeste Vorlage im Text' % kid)
            for m in muss:
                if m not in txt:
                    probleme.append('%s fehlt: %s' % (kid, m))
            for v in verboten:
                if v in txt:
                    probleme.append('%s: Formulierung ueber das Gemessene hinaus: %s' % (kid, v))
            print('  ok  %s: %d Zeichen geprueft' % (kid, len(txt)))

        await karte('g-nichtgleich', MUSS_NICHTGLEICH, VERBOTEN_NICHTGLEICH)
        await karte('g-abbau', MUSS_ABBAU, VERBOTEN_ABBAU)

        # Der Verweis auf die Region muss die Hirnkarte oeffnen UND die Tafel
        # zeigen - sonst steht der Kinderbefund ohne Weg dorthin.
        rg = pg.locator('#g-nichtgleich .xlink[data-region="striatum"]')
        if await rg.count() != 1:
            probleme.append('Verweis auf die Basalganglien-Region fehlt')
        else:
            await rg.click()
            await pg.wait_for_timeout(800)
            info = await pg.inner_text('#organInfo')
            if 'Basalganglien' not in info:
                probleme.append('der Verweis oeffnet die Basalganglien-Tafel nicht')
            elif 'Säuglingsgehirn' not in info:
                probleme.append('die Basalganglien-Tafel hat den Kinderbefund verloren')
            else:
                print('  ok  Verweis oeffnet die Tafel mit dem Kinderbefund')
            # zurueck in den Reiter fuer die naechsten Pruefungen
            await pg.click('#groups button[data-g="0"]')
            await pg.wait_for_timeout(300)
            await pg.click('#tabs button:has-text("Im Gehirn")')
            await pg.wait_for_timeout(700)

        # Der Beleg muss als anklickbare Fussnote erscheinen, nicht als nackte
        # Zahl im Text.
        n = await pg.locator('#g-nichtgleich .ref, #g-nichtgleich .cite,'
                             ' #g-nichtgleich sup, #g-nichtgleich button.refbtn').count()
        if n == 0:
            probleme.append('g-nichtgleich: kein anklickbarer Beleg gerendert')
        else:
            print('  ok  g-nichtgleich: %d Beleg-Marke(n) gerendert' % n)

        # Der Querverweis traegt gleich die Pruefung von l-alter: Der Sprung
        # muss den Reiter wechseln UND die Karte zeigen.
        kn = pg.locator('#g-nichtgleich .xlink[data-card="l-alter"]')
        if await kn.count() != 1:
            probleme.append('Querverweis von g-nichtgleich nach l-alter fehlt')
        else:
            await kn.first.click()
            await pg.wait_for_timeout(900)
            hoch = await pg.evaluate("() => { const c = document.getElementById('l-alter');"
                                     " return c ? c.getBoundingClientRect().height > 0 : 'FEHLT'; }")
            if hoch is not True:
                probleme.append('Sprung nach l-alter tot (%s)' % hoch)
            else:
                print('  ok  Sprung g-nichtgleich -> l-alter funktioniert')
                # Der Sprung hat den Reiter Lebensphasen geoeffnet - jetzt sind
                # auch seine Einleitung und sein Fazit da.
                await karte('l-alter', MUSS_ALTER, [])
                await karte('l-fazit', MUSS_FAZIT, VERBOTEN_FAZIT)
                intro = await pg.inner_text('#tabpanel .intro')
                for m in MUSS_INTRO:
                    if m not in intro:
                        probleme.append('Einleitung Lebensphasen fehlt: %s' % m)
                for v in VERBOTEN_INTRO:
                    if v in intro:
                        probleme.append('Einleitung Lebensphasen behauptet die Abnahme'
                                        ' wieder ungestuetzt: %s' % v)
                if all(m in intro for m in MUSS_INTRO):
                    print('  ok  Einleitung Lebensphasen schreibt die Abnahme den Tieren zu')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
