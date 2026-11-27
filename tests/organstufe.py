# -*- coding: utf-8 -*-
"""Dauertest: die Stufe 0 der Koerperkarte bedeutet "Nicht untersucht", und die
Stufen 1-3 sowie Organe ganz ohne Eintrag sagen weiter genau dasselbe wie vorher.

WARUM: Die Skala der Koerperkarte kannte nur 1-3, also musste JEDES Organfeld
eine Wirkstaerke behaupten. Dadurch stand bei Monlunabant unter "Leber"
"Deutliche Wirkung" ueber einem Text, der sagt, dass dort nie gemessen wurde.
Gefunden wurde das nur im GERENDERTEN Text - in der Quelldatei steht bloss eine
Zahl. Stufe 0 drueckt jetzt das Fehlen einer Messung aus. Dieser Test haelt
beides fest: dass die neue Stufe die richtige Wendung zeigt UND dass die
Einfuehrung an den alten Stufen nichts verschoben hat.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright
EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

# (Stoff, Organ, erwartete Wendung)
PFLICHT = [('mon', 'liver',    'Nicht untersucht.'),
           ('mon', 'muskel',   'Nicht untersucht.'),
           ('mon', 'pankreas', 'Nicht untersucht.'),
           ('mon', 'fat',      'Deutliche Wirkung.'),
           ('rim', 'brain',    'Starke Wirkung.'),
           ('rim', 'muskel',   'Schwache Wirkung.'),
           ('2ag', 'brain',    'Starke Wirkung.'),
           ('2ag', 'pankreas', 'Schwache Wirkung.'),
           # 27.11.2026: der vierte Zustand. "nie geprueft" ist nicht dasselbe
           # wie "geprueft und nichts gefunden" - die Skala konnte das nicht
           # ausdruecken, und mon.niere stand deshalb auf "Deutliche Wirkung"
           # ueber einem Ergebnis ohne Unterschied zu Placebo. Ein Organfeld
           # darf jetzt ein drittes Element 'ohne' tragen.
           ('mon', 'niere',    'Geprüft, keine Wirkung.')]
# Ein Organ, fuer das der Stoff gar keinen Eintrag hat: muss die alte Wendung zeigen.
OHNE_EINTRAG = ('rim', 'auge', 'Keine nennenswerte Wirkung.')


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1000})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1700)
        probleme = []
        for sub, organ, erwartet in PFLICHT + [OHNE_EINTRAG]:
            ch = pg.locator('.chip[data-id="%s"]' % sub)
            if await ch.count() != 1:
                probleme.append('Chip %s fehlt' % sub); continue
            await ch.click(); await pg.wait_for_timeout(450)
            o = pg.locator('#or-%s' % organ)
            if await o.count() != 1:
                probleme.append('Organ %s fehlt' % organ); continue
            await o.evaluate("e => e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(420)
            t = await pg.inner_text('#organInfo')
            # Die Wendung steht fett am Anfang der letzten Beschreibungszeile.
            if erwartet not in t:
                got = [z for z in t.split('\n') if 'Wirkung' in z or 'untersucht' in z]
                probleme.append('%s.%s: erwartet "%s", gefunden %s' % (sub, organ, erwartet, got[-2:]))
            else:
                print('  ok  %-4s %-9s %s' % (sub, organ, erwartet))
        # Stufe 0 darf nicht als "keine Wirkung" durchgehen.
        await pg.locator('.chip[data-id="mon"]').click(); await pg.wait_for_timeout(400)
        await pg.locator('#or-liver').evaluate(
            "e => e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(400)
        t = await pg.inner_text('#organInfo')
        for weg in ('Deutliche Wirkung', 'Keine nennenswerte Wirkung',
                    'Für diesen Stoff ist hier keine nennenswerte Wirkung beschrieben'):
            if weg in t:
                probleme.append('mon.liver zeigt weiter "%s"' % weg)
        if 'nicht gemessen' not in t:
            probleme.append('mon.liver sagt nicht, dass nicht gemessen wurde')
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)

asyncio.run(main())
