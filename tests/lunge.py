# -*- coding: utf-8 -*-
"""Lungen-Tafel (14.11.2026) - und der Widerspruch, der stehen bleiben muss.

ZWEI UEBERSICHTEN VON 2022 WIDERSPRECHEN SICH: Die eine sieht im Querschnitt
keinen deutlichen Abfall des Einsekundenwerts und in den meisten Studien kein
erhoehtes Lungenkrebsrisiko [[35609784]]; die andere haelt einen negativen
Einfluss auf die Lungenfunktion samt beschleunigtem Abfall fuer gezeigt und
nennt zusammen mit Tabak mehr COPD und Emphysem [[36115751]].

WARUM DER TEST BEIDE SEITEN VERLANGT: Es ist verlockend, eine davon zu
uebernehmen - die beruhigende, wenn man Cannabis verteidigen will, die
alarmierende, wenn man warnen will. Beide allein waeren eine Luege durch
Auswahl. Der Test prueft, dass BEIDE Positionen dastehen UND die
Hauptschwierigkeit, die beide nennen: Fast alle Rauchenden rauchen auch Tabak.

DIE BELEGSTUFE: Die Tafel stand auf "gut belegt", waehrend ihre Kernaussage
lautet, dass die Uebersichten sich widersprechen. Das passte nicht zusammen und
steht jetzt auf "teils belegt". Der Test haelt das fest.

DER BEFUND, DER INS MUSTER PASST: Gerauchtes Cannabis erweitert kurzfristig die
Atemwege, auch bei Asthma - gemessen seit den 1970er Jahren, nie eine
Behandlung geworden. Dasselbe wie beim Augeninnendruck; ohne den zweiten
Halbsatz liest es sich als Therapieaussicht.
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

NEU = ['35609784', '36115751', '39984952']
MUSS = [
    'erweitert kurzfristig die Atemwege',
    'eine Behandlung ist daraus nie geworden',
    'Einig sind sich die Übersichten bei den Beschwerden einer chronischen Bronchitis',
    'keinen deutlichen Abfall des Einsekundenwerts',           # Position A
    'kein erhöhtes Lungenkrebsrisiko',                          # Position A
    'negativen Einfluss auf die Lungenfunktion samt beschleunigtem Abfall',  # Position B
    'mehr COPD und Emphysem',                                   # Position B
    'Fast alle Rauchenden rauchen auch Tabak',                  # die gemeinsame Einschraenkung
    'teils belegt',                                             # Belegstufe passend zum Inhalt
]
VERBOTEN = [
    'schadet der Lunge nicht',
    'ist für die Lunge unbedenklich',
    'verursacht Lungenkrebs',
    'führt zu COPD',
    'hilft bei Asthma',
]


async def main():
    probleme = []
    T = io.open(QUELLE, encoding='utf-8').read()
    T = T[T.find('<title>'):]
    for p in NEU:
        if ("['%s'," % p) not in T: probleme.append('Beleg %s fehlt im Verzeichnis' % p)
        if ('[[%s]]' % p) not in T: probleme.append('Beleg %s wird nicht benutzt' % p)

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1080})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1800)
        await pg.locator('button.chip[data-id="thc"]').first.evaluate(
            "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(280)
        await pg.locator('#or-lung').evaluate(
            "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(300)
        t = await pg.inner_text('#organInfo')
        if '${' in t or '[[' in t: probleme.append('Vorlagenrest in der Lungentafel')
        for s in MUSS:
            if s not in t: probleme.append('fehlt: »%s«' % s)
        for v in VERBOTEN:
            if v in t: probleme.append('unerwuenscht: »%s«' % v)
        for d in (' mg', 'Milligramm'):
            if d in t: probleme.append('Dosisangabe in der Lungentafel')
        # Beide Belege muessen in DIESER Tafel benutzt sein, nicht nur im
        # Verzeichnis stehen - sonst steht nur eine Seite des Widerspruchs da.
        pm = await pg.evaluate("""()=>[...document.querySelectorAll('#organInfo sup.cite a[data-pm]')]
            .map(a=>a.dataset.pm)""")
        for p2 in ('35609784', '36115751'):
            if p2 not in pm: probleme.append('Beleg %s wird in der Lungentafel nicht benutzt' % p2)
        kn = pg.locator('#organInfo .xlink[data-tab="covid"]')
        if await kn.count() != 1: probleme.append('Verweis auf den COVID-Reiter fehlt')
        print('  ok  Lungentafel: beide Positionen, die Einschraenkung und die Belegstufe')
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler: sys.exit(1)

asyncio.run(main())
