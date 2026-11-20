# -*- coding: utf-8 -*-
"""Prueft die Suchhilfen (SYN) der Seite.

Zwei Fragen, beide hart:
 1. Findet jedes Suchhilfe-Wort jetzt mindestens einen Eintrag? Ein Alias,
    der auf nichts zeigt, waere ein Versprechen ohne Deckung.
 2. Treffen die Treffer zum Thema? Dafuer wird zu jedem Wort ein Begriff
    angegeben, der in mindestens einem Treffer vorkommen MUSS.
Zusaetzlich: Begriffe, die absichtlich NICHT aufgenommen wurden (ADHS,
Krankenkasse), muessen weiterhin 0 Treffer liefern - sonst haette jemand
einen Alias auf nicht vorhandenen Inhalt gelegt.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

# Suchwort -> Wort, das in mindestens einem Treffer stehen muss
PRUEF = [
    ('multiple sklerose', 'spastik'),
    ('sativex',           'nabiximols'),
    ('canemes',           'nabilon'),
    ('marinol',           'dronabinol'),
    ('epidiolex',         'epidyolex'),
    ('marihuana',         'cannabis'),
    ('haschisch',         'cannabis'),
    ('weed',              'cannabis'),
    ('kiffen',            'cannabis'),
    ('joint',             'cannabis'),
    ('vaporisieren',      'inhal'),
    ('verdampfen',        'inhal'),
    ('bong',              'rauch'),
    ('munchies',          'appetit'),
    ('heißhunger',        'appetit'),
    ('führerschein',      'fahrt'),
    ('autofahren',        'fahrt'),
    ('arachidonoylethanolamid', 'anandamid'),
    ('endocannabinoidsystem', 'endocannabinoid'),
    ('ecs',               'endocannabinoid'),
    ('runnershigh',       'runner'),
    ('insomnie',          'schlafstör'),
    ('schlaflosigkeit',   'schlafstör'),
    ('panikattacke',      'panik'),
    ('neuropathie',       'neuropathisch'),
    ('hospiz',            'palliativ'),
    ('sterbebegleitung',  'palliativ'),
    ('psoriasis',         'schuppenflechte'),
    ('adipositas',        'übergewicht'),
    ('fettleibigkeit',    'übergewicht'),
    ('pubertät',          'jugend'),
    ('senioren',          'ältere'),
    ('longcovid',         'long covid'),
    ('osteoporose',       'knochenabbau'),
    ('mikrobiom',         'darmbakterien'),
    ('mikrobiota',        'darmbakterien'),
    ('kachexie',          'auszehrung'),
    ('schizophrenie',     'psychose'),
    ('drogentest',        'schnelltest'),
    ('urintest',          'urinprobe'),
    ('faah-gen',          'c385a'),
    ('vererbung',         'cnr1'),
]
# Diese Begriffe bleiben absichtlich leer: Dazu steht auf der Seite nichts.
# Sie stehen hier, damit niemand spaeter einen Alias auf fremden Inhalt legt.
#
# 09.11.2026 nachgezogen: 'adhs' und 'krankenkasse' sind HERAUSGENOMMEN, weil
# die Seite dazu inzwischen belegten Inhalt hat und die Treffer berechtigt
# sind - nachgesehen, nicht angenommen: ADHS steht in einer Meta-Analyse zu
# psychischen Erkrankungen ('kaum oder keine Wirkung bei Depression, ADHS,
# Psychose, Tourette'), Krankenkasse im Status zu Medizinalcannabis ('die
# Krankenkasse zahlt auf Antrag'). Die Leerprobe war veraltet, nicht die Seite.
# Wer hier wieder etwas eintraegt, pruefe erst, ob der Begriff auf der Seite
# wirklich fehlt.
LEER = ['aufmerksamkeitsdefizit', 'akne', 'statine',
        'arbeitsplatz', 'haaranalyse', 'burnout', 'muskelkater']


async def tippen(pg, wort):
    """Sucht ueber die Oberflaeche, nicht ueber Innereien: tippen und lesen."""
    await pg.fill('#findQ', '')
    await pg.wait_for_timeout(160)
    await pg.fill('#findQ', wort)
    await pg.wait_for_timeout(420)
    # Nur echte Treffer zaehlen. Die Meldung "Nichts gefunden" steht ebenfalls
    # in #findRes und wuerde jede Leerprobe falsch bestehen lassen.
    return await pg.evaluate("""() => [...document.querySelectorAll('#findRes [role=option]')]
        .map(e => (e.textContent || '').toLowerCase()).filter(t => t.trim().length > 3)""")


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(2000)
        probleme = []
        for wort, muss in PRUEF:
            r = await tippen(pg, wort)
            if not r:
                probleme.append('OHNE TREFFER: "%s"' % wort)
            elif not any(muss in t for t in r):
                probleme.append('THEMA VERFEHLT: "%s" -> kein Treffer enthaelt "%s" (1. Treffer: %s)'
                                % (wort, muss, r[0][:70]))
            else:
                print('  ok  %-26s %d Treffer' % (wort, len(r)))

        for wort in LEER:
            r = len(await tippen(pg, wort))
            if r:
                probleme.append('SOLLTE LEER SEIN: "%s" -> %d Treffer' % (wort, r))
            else:
                print('  ok  %-26s leer, wie vorgesehen' % wort)

        print('\nSuchhilfen geprueft:', len(PRUEF), '| Leerproben:', len(LEER))
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)

asyncio.run(main())
