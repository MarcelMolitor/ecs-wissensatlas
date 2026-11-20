# -*- coding: utf-8 -*-
"""Prueft die Karte bo-pepcan im Reiter Botenstoffe.

Zwei Dinge soll dieser Test auf Dauer halten:

1. DIE VERBOTSLISTE. Der Stoff kommt aus dem Haemoglobin, wirkt an beiden
   Rezeptoren mit entgegengesetztem Vorzeichen und wird in der Nebenniere
   vorgehalten - aus jedem dieser drei Punkte laesst sich muehelos eine
   Gesundheitsaussage machen, die keine der fuenf Arbeiten traegt. Verboten
   sind deshalb Formulierungen, die aus dem Blutfarbstoff ein Mittel machen
   ("Haemoglobin wirkt auf", "Blutspende"), die eine Wirkung am Menschen
   behaupten, und - in die andere Richtung - die eine Kontroverse ueber die
   Endogenitaet behaupten, die ich in der Literatur NICHT gefunden habe.

2. DIE DREI ZEIGER. Die Karte widerspricht b-chemie und praezisiert r-allo.
   Beide Stellen muessen auf sie zurueckverweisen, sonst steht die Regel ohne
   ihre Ausnahme da - das war genau der Zustand, den diese Runde behoben hat.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['Eiweißschnipsel', 'zwölf Aminosäuren', 'Hämoglobin', 'Pepcan-12 bis Pepcan-23',
        'Blutplasma von Maus', 'niedrigen Nanomol-Bereich', 'Vorgeschlagen war das Peptid',
        'nur teilweise', 'dämpfenden Modulators', 'Am CB2 wirkt dasselbe Molekül umgekehrt',
        'Fünf- bis Zehnfache', 'zwei Vorzeichen', 'Noradrenalin', 'Locus coeruleus',
        'chromaffinen Zellen des Nebennierenmarks', 'Entfernen der Nebennieren', 'zwei verschiedene Fragen',
        'Dass er dort wirkt, ist damit nicht gezeigt',
        'steht er quer zu drei Sätzen dieser Seite', 'Sie beschreibt nur nicht alle',
        'Hemopressin', 'Lipoxin A4', 'Pregnenolon',
        'ob er dort gebildet wird, wo er wirkt', 'nur ohne Ausspülen messbar',
        'eigenen Antikörpern', 'hat niemand untersucht']
VERBOTEN = ['stärkste Färbung von allen', 'prüften zwei Gegenproben',
            'Hämoglobin wirkt auf', 'Blutspende', 'Eisenmangel', 'beim Menschen wirksam',
            'hilft beim Menschen', 'umstritten, ob es diesen Stoff gibt',
            'Kontroverse', 'als Artefakt', 'widerlegt', 'neues Wirkprinzip für',
            'kann man einnehmen', 'Nebennierenschwäche']


async def zum_reiter(pg):
    await pg.click('#groups button[data-g="0"]')
    await pg.wait_for_timeout(250)
    await pg.click('#tabs button:has-text("Botenstoffe")')
    await pg.wait_for_timeout(460)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1600)
        probleme = []

        await zum_reiter(pg)
        chip = pg.locator('.qchip[data-jump="bo-pepcan"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt')
        else:
            await chip.click()
            await pg.wait_for_timeout(680)
            # Auf Stillstand warten statt auf eine feste Dauer. Am 20.11.2026
            # wurde der Container ersetzt und Chromium sprang von 1194 auf 1243;
            # derselbe Sprung braucht dort mehr als doppelt so lang. Gemessener
            # Verlauf der Kartenoberkante: 9522 -> 2333 -> 661 -> 164 -> 137.
            # Eine feste Wartezeit von 680 ms misst mitten in der Bewegung und
            # meldet einen Seitenfehler, den es nicht gibt. Sechs Tests hingen
            # daran. Dieselbe Lehre wie beim fest eingetragenen Chromium-Pfad:
            # kein Wert, der an eine Umgebung gebunden ist.
            _vorher = None
            for _ in range(40):                      # hoechstens 6 Sekunden
                await pg.wait_for_timeout(150)
                _jetzt = await pg.evaluate('Math.round(window.scrollY)')
                if _jetzt == _vorher:
                    break
                _vorher = _jetzt
            lage = await pg.evaluate("""() => {
                const r = document.getElementById('bo-pepcan').getBoundingClientRect();
                return {top: Math.round(r.top), hoch: Math.round(r.height)};
            }""")
            print('  Karte nach Sprung:', lage)
            if abs(lage['top']) > 400 or lage['hoch'] < 400:
                probleme.append('Sprung landet falsch: %s' % lage)

        t = await pg.inner_text('#bo-pepcan')
        print('  Kartentext:', len(t), 'Zeichen')
        for muss in MUSS:
            if muss not in t:
                probleme.append('fehlt: %s' % muss)
        for weg in VERBOTEN:
            if weg in t:
                probleme.append('Formulierung, die die Arbeiten nicht tragen: %s' % weg)

        # Alle vier Stufen, die die Karte braucht: gemessen (m), Lokalisierung im
        # Tier (s), Uebersichtsarbeit (Hypothese) und die Wirkung am Menschen (n).
        for stufe in ['teils belegt', 'schwach belegt', 'Hypothese', 'nicht untersucht']:
            if stufe not in t:
                probleme.append('Belegstufe fehlt: %s' % stufe)
        # Keine Dosis- oder Einnahmeangabe zu einem koerpereigenen Peptid.
        if re.search(r'\d+\s*(mg|µg|mikrogramm|Milligramm)\b', t, re.I):
            probleme.append('Mengenangabe im Text')

        n = await pg.locator('#bo-pepcan button.xlink').count()
        print('  Querverweise:', n)
        if n != 7:
            probleme.append('%d Querverweise, erwartet 7' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#bo-pepcan button.xlink').nth(i)
            beschr = (await kn.inner_text()).strip()
            ziel = await kn.get_attribute('data-card')
            stoff = await kn.get_attribute('data-sub')
            await kn.click()
            await pg.wait_for_timeout(820)
            if ziel:
                da = await pg.evaluate("""(id) => {
                    const c = document.getElementById(id);
                    return c ? c.getBoundingClientRect().height > 0 : 'FEHLT';
                }""", ziel)
                if da is not True:
                    probleme.append('Verweis "%s" -> %s tot (%s)' % (beschr, ziel, da))
                else:
                    print('   ok  "%s" -> %s' % (beschr[:34], ziel))
            elif stoff:
                name = (await pg.inner_text('#subName')).replace('#', '').strip()
                print('   ok  "%s" -> Stoff %s' % (beschr[:34], name))
                if not name:
                    probleme.append('Stoffverweis "%s" waehlt nichts aus' % beschr)

        # Die beiden Rueckverweise: ohne sie steht die Regel ohne ihre Ausnahme.
        await zum_reiter(pg)
        ch = await pg.inner_text('#b-chemie')
        if 'Der Botenstoff, der kein Fett ist' not in ch:
            probleme.append('b-chemie verweist nicht auf bo-pepcan')
        await pg.click('#tabs button:has-text("Rezeptoren")')
        await pg.wait_for_timeout(520)
        al = await pg.inner_text('#r-allo')
        if 'einen körpereigenen' not in al:
            probleme.append('r-allo verweist nicht auf bo-pepcan')
        if 'kein einziger positiver Modulator hat je eine Studie erreicht' not in al:
            probleme.append('r-allo hat seine eigene Aussage verloren')

        for q in ['pepcan', 'hemopressin', 'nebennierenmark']:
            await pg.fill('#findQ', q)
            await pg.wait_for_timeout(520)
            n2 = await pg.eval_on_selector_all('#findRes [role=option]', 'e => e.length')
            print('  Suche "%s": %s Treffer' % (q, n2))
            if not n2:
                probleme.append('Suche findet "%s" nicht' % q)

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
