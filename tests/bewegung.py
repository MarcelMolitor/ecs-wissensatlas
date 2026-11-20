# -*- coding: utf-8 -*-
"""Dauertest: der Reiter "Im Gehirn" behandelt die Bewegung, und die Karte
bleibt bei dem, was die Arbeiten hergeben.

WARUM: Gezaehlt am 12.11.2026 ueber 29 Hirnbegriffe: Huntington 0, Chorea 0,
Dyskinesie 0, Tremor 0, Bewegungsstoerung 0, Motorik 1, Koordination 1 -
dagegen Schlaf 109 und Angst 105. Die ZWEI der drei am dichtesten besetzten
Hirnregionen, die fuer Bewegung zustaendig sind, hatten auf der ganzen Seite
kein Kapitel; die Parkinson-Meta-Analyse [[42138778]] kam genau einmal vor, in
der Neuigkeiten-Liste, in keiner Karte.

DER PUNKT, den dieser Test schuetzt, ist nicht die Karte selbst, sondern ihre
Ehrlichkeit an zwei Stellen:
 1. Die Huntington-Studie darf NICHT als Scheitern dargestellt werden. 24
    Teilnehmende ueber zwoelf Wochen koennen einen Effekt dieser
    Groessenordnung nicht zeigen, und die Autoren schreiben das selbst. Faellt
    der Vorbehalt heraus, steht dort ein Ergebnis, das es nicht gibt.
 2. Die Fazit-Tabelle muss die vierte Zeile als AUSNAHME fuehren. Der Reiter
    war ein geschlossenes Argument ueber drei Funktionen; die vierte bricht
    das Muster. Ein Muster, das man nur zeigt, wo es passt, ist keins.

UND EIN SACHFEHLER, den das Korrekturlesen am gerenderten Text gefunden hat:
Die Karte behauptete zuerst, die dichtesten Regionen seien "nicht die fuer
Gedaechtnis zustaendigen, sondern die fuer Bewegung". Falsch - Basalganglien,
Hippocampus UND Kleinhirn teilen sich die hoechste Dichtestufe. Der Test
rechnet das jetzt aus dem BRAIN-Objekt nach, statt es zu glauben.
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

MUSS = ['Huntington', 'als Erstes', 'nahezu vollständig verschwunden',
        'denselben drei Autoren', 'weniger als 20 Prozent', '24 schlossen ab',
        'nicht dasselbe wie Scheitern', 'zu klein', 'Parkinson', 'elf randomisierte']
VERBOTEN = [
    # Die Huntington-Studie als Fehlschlag auszugeben, waere falsch.
    'bei Huntington gescheitert', 'Huntington gescheitert', 'wirkungslos bei Huntington',
    # Und die Mausdaten duerfen nicht zur Menschenaussage werden.
    'beim Menschen bestätigt', 'im Modell bestätigt',
    # Keine Dosis fuer einen verschreibbaren Stoff.
    'Sprühstöße', 'Sprühstoss', 'Hübe pro Tag',
]


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    # Die Behauptung ueber die Dichtestufen gegen das BRAIN-Objekt rechnen.
    m = re.search(r'const BRAIN = \{', S); j = m.end(); t = 1; k = j
    while t:
        if S[k] == '{': t += 1
        elif S[k] == '}': t -= 1
        k += 1
    d3 = re.findall(r"\n \w+:\{name:'([^']*)', d:3,", S[j:k - 1])
    print('  Hoechste Dichtestufe:', d3)
    # Seit 13.11.2026 nennt der Text KEINE Zahl mehr ('Drei Regionen' war eine
    # Handzahl und waere mit dem Globus pallidus falsch geworden - dieser Test
    # hat das gemeldet). Er nennt die Regionen beim Namen; geprueft wird, dass
    # genau diese die Stufe 3 tragen und die Zahl nicht zurueckkommt.
    if sorted(d3) != ['Basalganglien', 'Globus pallidus', 'Hippocampus', 'Kleinhirn', 'Substantia nigra']:
        probleme.append('Dichtestufen haben sich geaendert: %s - der Text der Karte nennt'
                        ' Hippocampus, Basalganglien, Globus pallidus und Kleinhirn' % d3)
    if 'Drei Regionen tragen' in S[S.find('<title>'):]:   # das Protokoll im Seitenkopf zitiert sie
        probleme.append("die Handzahl 'Drei Regionen tragen' ist zurueck")
    if 'daraus eigens herausgehoben der Globus pallidus und die Substantia nigra' not in S:
        probleme.append('g-bewegung nennt den Globus pallidus nicht')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1000})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1700)
        await pg.click('#groups button[data-g="0"]')
        await pg.wait_for_timeout(300)
        await pg.click('#tabs button:has-text("Im Gehirn")')
        await pg.wait_for_timeout(700)

        if await pg.locator('#g-bewegung').count() != 1:
            probleme.append('Karte g-bewegung fehlt')
        else:
            txt = await pg.inner_text('#g-bewegung')
            print('  Karte g-bewegung: %d Zeichen' % len(txt))
            for muss in MUSS:
                if muss not in txt:
                    probleme.append('g-bewegung fehlt: %s' % muss)
            # Die drei Belegstufen der Karte.
            for stufe in ('gut belegt', 'teils belegt', 'schwach belegt', 'am Menschen gescheitert'):
                if stufe not in txt:
                    probleme.append('Belegstufe "%s" fehlt in g-bewegung' % stufe)
            if 'teils belegt' in txt and txt.count('schwach belegt') < 1:
                pass

        ganz = await pg.inner_text('#tabpanel')
        for weg in VERBOTEN:
            if weg in ganz:
                probleme.append('Formulierung, die die Arbeiten nicht tragen: %s' % weg)
        # Keine handgezaehlte Zahl mehr in Einleitung, Sprungknopf, Ueberschrift.
        for zahl in ('Drei Aufgaben', 'Was die drei zeigen', 'Was die drei zusammen zeigen'):
            if zahl in ganz:
                probleme.append('handgezaehlte Zahl wieder da: %s' % zahl)
        # Sprungknopf vorhanden
        if await pg.locator('.qchip[data-jump="g-bewegung"]').count() != 1:
            probleme.append('Sprungknopf fuer g-bewegung fehlt')
        else:
            print('  ok  Sprungknopf vorhanden')
        # Die vierte Tabellenzeile und ihre Einordnung als Ausnahme
        fz = await pg.inner_text('#g-fazit')
        if 'Bewegung' not in fz:
            probleme.append('Fazit-Tabelle ohne Zeile Bewegung')
        for muss in ('bricht es', 'nicht einmal die zählbare Einzelgröße'):
            if muss not in fz:
                probleme.append('Fazit ohne die Einordnung als Ausnahme: %s' % muss)
        if 'bricht es' in fz:
            print('  ok  Fazit fuehrt die vierte Zeile als Ausnahme')
        # Der Querverweis aus der Hirnkarte
        await pg.click('#viewSeg button[data-v="brain"]')
        await pg.wait_for_timeout(700)
        await pg.locator('#rg-striatum').evaluate(
            "e => e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(500)
        kn = pg.locator('#organInfo button.xlink[data-card="g-bewegung"]')
        if await kn.count() != 1:
            probleme.append('Hirnkarte verweist nicht auf g-bewegung')
        else:
            await kn.click(); await pg.wait_for_timeout(900)
            da = await pg.evaluate("() => { const c = document.getElementById('g-bewegung');"
                                   " return c ? c.getBoundingClientRect().height > 0 : 'FEHLT'; }")
            if da is not True:
                probleme.append('Verweis aus der Hirnkarte tot (%s)' % da)
            else:
                print('  ok  Verweis Basalganglien -> g-bewegung springt')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
