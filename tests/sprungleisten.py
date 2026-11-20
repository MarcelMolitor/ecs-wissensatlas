# -*- coding: utf-8 -*-
"""Dauertest: JEDER Sprungknopf in JEDEM Reiter muss ein vorhandenes Ziel haben.

WARUM DIESER TEST GEBRAUCHT WIRD: Die Sprungleisten oben in einem Reiter
(.jumps .qchip mit data-jump) zeigen auf Karten-ids. Diese Seite wird alle drei
Stunden von einer anderen Sitzung weitergebaut; wird eine Karte umbenannt,
verschoben oder zusammengefasst, zeigt ihr Sprungknopf ins Leere - und zwar
lautlos: Der Knopf bleibt sichtbar, das Antippen tut nichts, und kein
bestehender Test merkt es.

WAS VORHER FEHLTE: leisten.py prueft GENAU ZWEI Reiter und darin je EINEN
Knopf. audit2.py prueft Querverweise ([data-tab]/[data-card]) und Verweise auf
Organe und Hirnregionen, aber keine Sprungknoepfe. Die Sprungleisten waren
damit als Gruppe ungeprueft - dieselbe Art Luecke wie die vier, die vorher
schon gefunden wurden: eine Stichprobe statt der Gesamtmenge.

Geprueft wird dreifach, weil ein Knopf auf drei verschiedene Weisen kaputt
sein kann:
 1. Das Ziel existiert im Dokument.
 2. Das Ziel ist sichtbar (Hoehe > 0) - eine Karte in einem ausgeblendeten
    Reiter waere sonst ein Treffer, der dem Leser nichts bringt.
 3. Das Antippen bewegt die Karte wirklich in den Blick (top-Wert im Fenster).
Dazu: Beschriftung nicht leer, und data-jump gesetzt.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1700)
        probleme = []
        gezaehlt = 0
        mit_leiste = 0

        gruppen = await pg.locator('#groups button').count()
        for g in range(gruppen):
            await pg.locator('#groups button').nth(g).click()
            await pg.wait_for_timeout(220)
            anzahl = await pg.locator('#tabs button').count()
            for k in range(anzahl):
                await pg.locator('#groups button').nth(g).click()
                await pg.wait_for_timeout(180)
                tb = pg.locator('#tabs button').nth(k)
                reiter = (await tb.inner_text()).strip()
                await tb.click()
                await pg.wait_for_timeout(260)

                chips = await pg.evaluate("""() => [...document.querySelectorAll(
                    '#tabpanel .jumps .qchip')].map(e => ({
                        ziel: e.getAttribute('data-jump'),
                        text: (e.textContent || '').trim()
                    }))""")
                if not chips:
                    continue
                mit_leiste += 1
                for nr, chip in enumerate(chips):
                    gezaehlt += 1
                    ziel, text = chip['ziel'], chip['text']
                    if not ziel:
                        probleme.append('[%s] Knopf "%s" ohne data-jump' % (reiter, text))
                        continue
                    if not text:
                        probleme.append('[%s] Knopf -> %s ohne Beschriftung' % (reiter, ziel))
                    # Reiter neu aufschlagen, damit jeder Knopf aus dem
                    # Ausgangszustand geprueft wird.
                    await pg.locator('#groups button').nth(g).click()
                    await pg.wait_for_timeout(160)
                    await pg.locator('#tabs button').nth(k).click()
                    await pg.wait_for_timeout(240)
                    lage = await pg.evaluate("""(id) => {
                        const c = document.getElementById(id);
                        if (!c) return 'FEHLT';
                        return c.getBoundingClientRect().height > 0 ? 'da' : 'unsichtbar';
                    }""", ziel)
                    if lage != 'da':
                        probleme.append('[%s] "%s" -> %s %s' % (reiter, text, ziel, lage))
                        continue
                    await pg.locator('#tabpanel .jumps .qchip').nth(nr).click()
                    # Auf Stillstand warten statt auf eine feste Dauer. Am
                    # 20.11.2026 wechselte Chromium von 1194 auf 1243; das
                    # weiche Scrollen braucht dort rund 1,2 s statt der hier
                    # angesetzten 700 ms. Ergebnis waren 15 gemeldete
                    # Sprungfehler, die keine waren - gemessen mitten in der
                    # Bewegung. scrollY ist der richtige Wert: gemessener
                    # Verlauf 0 -> 6831 -> 14371 -> 16500 -> 17527, dann Halt.
                    _v = None
                    for _ in range(40):                  # hoechstens 6 s
                        await pg.wait_for_timeout(150)
                        _j = await pg.evaluate('Math.round(window.scrollY)')
                        if _j == _v:
                            break
                        _v = _j
                    top = await pg.evaluate("""(id) => {
                        const c = document.getElementById(id);
                        return c ? Math.round(c.getBoundingClientRect().top) : null;
                    }""", ziel)
                    hoehe = await pg.evaluate("() => window.innerHeight")
                    if top is None or top < -40 or top > hoehe:
                        probleme.append('[%s] "%s" -> %s springt nicht in den Blick (top=%s)'
                                        % (reiter, text, ziel, top))

        print('Reiter mit Sprungleiste: %d | Sprungknoepfe geprueft: %d' % (mit_leiste, gezaehlt))
        if gezaehlt == 0:
            probleme.append('kein einziger Sprungknopf gefunden - Selektor veraltet?')
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
