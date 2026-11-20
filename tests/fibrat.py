# -*- coding: utf-8 -*-
"""Prueft die Karte r-fibrat im Reiter Rezeptoren.

WORUM ES GEHT: Fenofibrat ist ein zugelassenes, millionenfach verschriebenes
Mittel gegen erhoehte Blutfette, und im Zellversuch bindet es an beide
Cannabinoid-Rezeptoren. Aus so einem Befund laesst sich muehelos eine
Gesundheitsaussage machen, die die Arbeit nicht traegt - in BEIDE Richtungen.
Die Verbotsliste haelt deshalb beides draussen: dass das Mittel deswegen
irgendwie wirkt oder helfen koennte, UND dass man deswegen etwas an seiner
Einnahme aendern sollte. Es ist Zellversuch und isoliertes Gewebe, am Menschen
ist nichts gemessen.

Dazu haelt der Test die drei Praezisierungen fest, die beim Korrekturlesen
noetig waren: keine Behauptung, dass weitere Stoffe mitgeprueft wurden; keine
Behauptung, dass die Arbeit nie wiederholt wurde (ich habe nur keine
Wiederholung GEFUNDEN); und die richtige Unterscheidung der drei
Zwei-Richtungs-Faelle der Seite - bei Anandamid und Fenofibrat entscheidet die
MENGE, bei Pepcan-12 der REZEPTOR.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['umgekehrt auch Medikamente', 'Fenofibrat', 'erhöhte Blutfette',
        'bindet an beide', 'erheblich fester als am CB1',
        'am CB1 ein Teilaktivator', 'glockenförmig', 'dämpfender Modulator',
        'isolierten Darmstück', 'zum dritten Mal ein Stoff, der in zwei Richtungen wirkt',
        'Bei Anandamid im Rückenmark entscheidet die Menge',
        'Bei Pepcan-12 entscheidet der Rezeptor',
        'Beobachtung über diese Seite, keine Aussage über die Literatur',
        'eine unabhängige Wiederholung habe ich nicht gefunden',
        'keine gefunden', 'Für die Anwendung des Mittels folgt daraus nichts',
        'Beispiel für eine „neue Klasse',
        'Wie viele Wirkstoffe es je bis zum Menschen geschafft haben']
VERBOTEN = ['deutlicher als erwartet', 'seither nicht wiederholt',
            'Geprüft wurde unter anderem', 'wirkt beim Menschen', 'hilft gegen',
            'könnte helfen', 'sollte man absetzen', 'sollte man einnehmen',
            'bedenklich', 'Nebenwirkung über CB1', 'gut belegt', 'teils belegt',
            'Alltagsmedikament']


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
        chip = pg.locator('.qchip[data-jump="r-fibrat"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt')
        else:
            await chip.click()
            await pg.wait_for_timeout(680)

        t = await pg.inner_text('#r-fibrat')
        print('  Kartentext:', len(t), 'Zeichen')
        for muss in MUSS:
            if muss not in t:
                probleme.append('fehlt: %s' % muss)
        for weg in VERBOTEN:
            if weg in t:
                probleme.append('Formulierung, die die Arbeit nicht traegt: %s' % weg)
        # Zellversuch und isoliertes Gewebe: hoechstens "schwach belegt",
        # und die Wirkung am Menschen ausdruecklich "nicht untersucht".
        if 'schwach belegt' not in t:
            probleme.append('Belegstufe "schwach belegt" fehlt')
        if 'nicht untersucht' not in t:
            probleme.append('Belegstufe "nicht untersucht" fehlt')
        # Keine Dosisangabe zu einem verschreibungspflichtigen Mittel.
        if re.search(r'\d+\s*(mg|Milligramm|Tablette)\b', t):
            probleme.append('Dosisangabe zu einem Medikament')

        n = await pg.locator('#r-fibrat button.xlink').count()
        print('  Querverweise:', n)
        if n != 7:
            probleme.append('%d Querverweise, erwartet 7' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#r-fibrat button.xlink').nth(i)
            beschr = (await kn.inner_text()).strip()
            ziel = await kn.get_attribute('data-card')
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

        for q in ['fenofibrat', 'blutfette', 'glockenförmig']:
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
