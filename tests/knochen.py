# -*- coding: utf-8 -*-
"""Knochen-Tafel (14.11.2026) - gegen den Rueckfall in einen Selbstwiderspruch.

DER FUND: Die Tafel sagte "Am Menschen fehlen Daten", waehrend der Gen-Reiter
derselben Seite beim CB2-Gen CNR2 die KNOCHENDICHTE auffuehrt. Am Menschen gibt
es zwei Genstudien - die Erstbeschreibung und eine Wiederholung an 3121 Frauen
nach den Wechseljahren - und dazu Beobachtungsdaten zu starkem Cannabiskonsum.

DREI DINGE MUESSEN STEHEN BLEIBEN:
 1. Die Genspur am Menschen, samt dem Gegenstueck: Beim CB1-Gen zeigte sich der
    Zusammenhang NICHT. Wer das weglaesst, macht aus einem gezielten Befund
    einen allgemeinen.
 2. Die Beobachtung in die ungünstige Richtung (weniger Dichte, mehr Brueche).
    Sie ist leicht zu verlieren, weil sie nicht ins Bild "Rezeptor schuetzt
    Knochen" passt.
 3. Die Luecke: Es gibt KEINE Studie, in der ein Wirkstoff gezielt gegen
    Knochenschwund geprueft wurde. Ohne diesen Satz liest sich die Tafel wie
    eine Behandlungsaussicht.
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

NEU = ['16204352', '26055357', '41658673']
MUSS = [
    'Varianten des CB2-Gens CNR2 hängen mit Osteoporose',
    'Wiederholung an 3121 Frauen',
    'Varianten des CB1-Gens zeigten diesen Zusammenhang nicht',
    'niedrigerer Knochendichte, mehr Brüchen und schlechterer Bruchheilung',
    'keine Studie, in der ein Wirkstoff gezielt gegen Knochenschwund geprüft wurde',
]
VERBOTEN = [
    'Am Menschen fehlen Daten',      # der aufgeloeste Widerspruch
    'schützt die Knochen',
    'hilft gegen Osteoporose',
    'stärkt die Knochen',
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
        await pg.locator('#or-bone').evaluate(
            "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(300)
        t = await pg.inner_text('#organInfo')
        if '${' in t or '[[' in t: probleme.append('Vorlagenrest in der Knochentafel')
        for s in MUSS:
            if s not in t: probleme.append('fehlt: »%s«' % s)
        for v in VERBOTEN:
            if v in t: probleme.append('unerwuenscht: »%s«' % v)
        m = re.search(r'\n(Nicht untersucht|Schwache Wirkung|Deutliche Wirkung|Starke Wirkung)\.', t)
        if not m or m.group(1) != 'Schwache Wirkung':
            probleme.append('thc/bone steht auf "%s", erwartet "Schwache Wirkung"'
                            % (m.group(1) if m else '??'))
        # Der Verweis muss die beiden Stellen zusammenhalten
        kn = pg.locator('#organInfo .xlink[data-tab="gene"]')
        if await kn.count() != 1:
            probleme.append('Verweis in den Gen-Reiter fehlt')
        else:
            await kn.first.click(); await pg.wait_for_timeout(900)
            akt = await pg.evaluate("()=>{const b=document.querySelector('#tabs button[aria-selected=\"true\"],"
                                    "#tabs button.on');return b?b.textContent.trim():''}")
            if 'Gene' not in akt: probleme.append('Verweis fuehrt zu: %s' % akt)
        # Und der Gen-Reiter muss die Knochendichte weiter nennen, sonst
        # verliert die Tafel ihren Bezugspunkt.
        if 'Knochendichte' not in T: probleme.append('der Gen-Reiter nennt die Knochendichte nicht mehr')
        print('  ok  Knochentafel, Genspur, Beobachtung und Luecke geprueft')
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler: sys.exit(1)

asyncio.run(main())
