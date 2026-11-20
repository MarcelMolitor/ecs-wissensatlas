# -*- coding: utf-8 -*-
"""Prueft die Karte r-kern im Reiter Rezeptoren und die fuenf belegten
PPAR-Stellen bei PEA und OEA.

WARUM ES DIESEN TEST GIBT: Die Behauptung, dass die Hauptwirkung von PEA und
OEA ueber PPAR-alpha laeuft, stand mehrfach auf der Seite und nirgends mit
Beleg - bei den beiden Stoffen der Gruppe "Ergaenzungsmittel", die Menschen
tatsaechlich kaufen. Der Test haelt fest:

 - die Karte selbst mit ihren Pflichtstellen und sechs Querverweisen,
 - dass PEA und OEA ihre PPAR-Belege behalten (sonst faellt die Seite in den
   alten Zustand zurueck, ohne dass es auffaellt),
 - und eine Verbotsliste: kein Wirksamkeitsversprechen, keine Dosis zu zwei
   frei kaeuflichen Mitteln, keine Zeitangabe zum Unterschied zwischen
   Membran- und Kernrezeptor (die steht in keinem der beiden Belege), und
   nicht die gezaehlte Zahl von Andockstellen, die beim ersten Schreiben
   falsch war.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['PPAR-α', 'sitzen in einer Membran', 'welche Proteine die Zelle baut',
        'Mäuse, denen dieser Rezeptor fehlt',
        'an die Cannabinoid-Rezeptoren bindet es nicht',
        'bei Mäusen ohne PPAR-α tut es nichts', 'Schwesterrezeptoren',
        'welche Gene abgelesen werden', 'unerwartete Rolle für einen Kernrezeptor',
        'Bauanleitung für PPAR-α', 'zwei verschiedenen Entzündungsmodellen',
        'vollständig wirkungslos', 'CBG', 'saubere Gegenbeweis',
        'hat niemand gemessen', 'gemischt bis ernüchternd',
        'Ein geklärter Mechanismus ist keine Behandlung']
VERBOTEN = ['sieben Andockstellen', 'Alles andere in diesem Reiter steckt in der Zellhülle',
            'Beides steht in der Literatur', 'Millisekunden', 'innerhalb von Stunden',
            'wirkt beim Menschen', 'hilft bei', 'sollte man einnehmen', 'empfehlenswert',
            'gut belegt', 'Beweis für die Wirksamkeit']


async def zum_reiter(pg):
    await pg.click('#groups button[data-g="0"]')
    await pg.wait_for_timeout(250)
    await pg.click('#tabs button:has-text("Rezeptoren")')
    await pg.wait_for_timeout(500)


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
        chip = pg.locator('.qchip[data-jump="r-kern"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt')
        else:
            await chip.click()
            await pg.wait_for_timeout(680)

        t = await pg.inner_text('#r-kern')
        print('  Kartentext:', len(t), 'Zeichen')
        for muss in MUSS:
            if muss not in t:
                probleme.append('fehlt: %s' % muss)
        for weg in VERBOTEN:
            if weg in t:
                probleme.append('Formulierung, die die Belege nicht tragen: %s' % weg)
        for stufe in ['teils belegt', 'schwach belegt', 'nicht untersucht']:
            if stufe not in t:
                probleme.append('Belegstufe fehlt: %s' % stufe)
        if re.search(r'\d+\s*(mg|g|Kapsel)\b', t):
            probleme.append('Mengenangabe zu einem frei käuflichen Mittel')

        n = await pg.locator('#r-kern button.xlink').count()
        print('  Querverweise:', n)
        if n != 7:
            probleme.append('%d Querverweise, erwartet 7' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#r-kern button.xlink').nth(i)
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

        # Die fuenf Stellen bei PEA und OEA muessen ihre PPAR-Belege behalten.
        # SUBS ist nicht global, deshalb direkt in der Quelldatei geprueft.
        import io as _io
        quelle = _io.open(SEITE.replace('file://', ''), encoding='utf-8').read()
        # 15.11.2026: Drei Anker trugen die WIRKSTUFE mit im Suchtext
        # ("immune:[2,'...", "gut:[3,'..."). Als pea/immune nach der Regel der
        # Legende von 2 auf 1 gesenkt wurde, meldete dieser Test "PPAR-Stelle
        # verschwunden" - obwohl der PPAR-Beleg unveraendert dastand. Der Test
        # soll den BELEG bewachen, nicht die Stufe; die Stufe hat ihren eigenen
        # Test (t/wirkstufe.py). Ziffer aus den Ankern entfernt.
        PFLICHT = [
            ("'Entzündungshemmend, vor allem über PPAR-α", '15465922', 'PEA organs.immune'),
            ('Der angenommene Hauptweg über PPAR-α beruht auf Mäusen', '15465922', 'PEA obasis'),
            ("'Der Entstehungsort und der Angriffspunkt: PPAR-α", '12955147', 'OEA organs.gut'),
            ('An die Cannabinoid-Rezeptoren bindet OEA dabei nicht', '12955147', 'OEA organs.brain'),
            ("'Wie PEA ein PPAR-α-Weg", '15465922', 'OEA organs.immune'),
            ('Der Wirkweg selbst ist an Mäusen geklärt, nicht am Menschen', '12955147', 'OEA obasis'),
        ]
        for anker, pmid, was in PFLICHT:
            i = quelle.find(anker)
            if i < 0:
                probleme.append('PPAR-Stelle verschwunden: %s' % was)
            elif pmid not in quelle[i:i + 420]:
                probleme.append('PPAR-Stelle wieder ohne Beleg: %s' % was)
            else:
                print('   ok  %s traegt [[%s]]' % (was, pmid))

        for q in ['ppar', 'kernrezeptor', 'zellinneren']:
            await pg.fill('#findQ', q)
            await pg.wait_for_timeout(520)
            n3 = await pg.eval_on_selector_all('#findRes [role=option]', 'e => e.length')
            print('  Suche "%s": %s Treffer' % (q, n3))
            if not n3:
                probleme.append('Suche findet "%s" nicht' % q)

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
