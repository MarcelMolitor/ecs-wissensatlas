# -*- coding: utf-8 -*-
"""Prueft die Karte r-waisen im Reiter Rezeptoren.

WORUM ES GEHT: GPR3, GPR6 und GPR12 sind die naechsten Verwandten von CB1 und
CB2, und zu ihnen ist am wenigsten bekannt. Aus so einer Lage laesst sich
muehelos mehr machen, als die Arbeiten tragen - in zwei Richtungen:
 (1) CBD hilft deswegen gegen Alzheimer/Parkinson/Krebs. Tut es nicht; das
     sind VORSCHLAEGE der Autoren. Die Verbotsliste haelt das draussen.
 (2) Der Preprint beweist, dass Anandamid das Gedaechtnis verbessert. Tut er
     nicht; er ist nicht begutachtet und nicht wiederholt. Der Test verlangt
     deshalb, dass das Wort "Preprint" UND der Hinweis "nicht begutachtet" in
     der Karte stehen - faellt eines heraus, zitiert die Seite stillschweigend
     eine unbegutachtete Arbeit, und das waere der schwerste Fehler hier.

Dazu haelt der Test die Praezisierungen vom Korrekturlesen fest: keine
Rangfolge gegen den gesamten Reiter (die Uebersicht sagt nur "am naechsten"),
kein Superlativ ueber die eigene Seite, WIN55,212-2 beim Namen genannt, und
die Belegstufe "nicht untersucht" am Ende ihres Absatzes statt mitten darin.

AUSSERDEM: Die Karte muss alle sechs Belegstufen der Seite in der richtigen
Staffelung tragen - g fuer den Stammbaum, s fuer die Zellversuche und die
Hautmessung, h fuer den Preprint, n fuer den Menschen. Genau das ist ihr
Inhalt: wie duenn Wissen sein kann, ohne dass man es merkt.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['Waisenrezeptoren', 'GPR3, GPR6 und GPR12', 'am nächsten',
        'von sich aus an', 'ohne Ligand', 'herunter', 'inverser Agonist',
        'kein Aktivator, aber auch kein Blocker',
        'an GPR6 stärker', 'Cannabidivarin', 'WIN55,212-2',
        'die beiden Blocker', 'Rimonabant', 'das dieses Feld um Jahre zurückgeworfen hat',
        'gemessen ist eine Zelle', 'trifft womöglich mehr als einen',
        'Am Menschen gibt es genau eine Messung', 'Schuppenflechte',
        'Ablesung von Genen, keine Messung einer Wirkung',
        'Anandamid aktiviert den Rezeptor kräftig',
        'Arbeitsgedächtnis', 'laut der Arbeit auch bei Primaten',
        'Diese Arbeit ist ein Preprint', 'nicht begutachtet',
        'niemand hat sie wiederholt', 'erste Preprint auf dieser Seite',
        'ein Hinweis, kein Wissen',
        'aus einem einzigen Labor', 'sagen nichts über CBD',
        'am Menschen nichts gemessen',
        'Vorschläge der Autoren für künftige Forschung',
        'am wenigsten verstanden von allen']
VERBOTEN = [
    # Wirksamkeit, die keine Arbeit hergibt
    'hilft gegen', 'wirkt gegen Alzheimer', 'behandelt', 'Therapie mit CBD',
    'könnte heilen', 'verbessert das Gedächtnis beim Menschen',
    # unbelegte Rangfolgen und Superlative (7. erfundene Rangangabe)
    'näher als jede andere Andockstelle', 'näher als alles andere in diesem Reiter',
    'der am saubersten gegengeprüfte Befund', 'der beste Beleg der Seite',
    # Preprint verschwiegen oder aufgewertet. "gut belegt" steht hier NICHT auf
    # der Verbotsliste: die Karte traegt diese Stufe zu Recht fuer den
    # Stammbaum (Uebersichtsarbeit), und MUSS verlangt sie ausdruecklich.
    'belegt erstmals', 'beweist',
    # Dosis
    'Milligramm', 'Tagesdosis',
]


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
        chip = pg.locator('.qchip[data-jump="r-waisen"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt')
        else:
            await chip.click()
            await pg.wait_for_timeout(680)

        t = await pg.inner_text('#r-waisen')
        print('  Kartentext:', len(t), 'Zeichen')
        for muss in MUSS:
            if muss not in t:
                probleme.append('fehlt: %s' % muss)
        for weg in VERBOTEN:
            if weg in t:
                probleme.append('Formulierung, die die Arbeit nicht traegt: %s' % weg)

        # Staffelung der Belegstufen: g einmal (Stammbaum), s dreimal
        # (zwei Zellversuche, Hautmessung), h fuer den Preprint, n fuer den Menschen.
        for stufe, mind in [('gut belegt', 1), ('schwach belegt', 3),
                            ('Hypothese', 1), ('nicht untersucht', 1)]:
            if t.count(stufe) < mind:
                probleme.append('Belegstufe "%s" nur %dx, erwartet %d+'
                                % (stufe, t.count(stufe), mind))
        # Keine Dosisangabe zu einem frei kaeuflichen Mittel.
        if re.search(r'\d+\s*(mg|Milligramm|Tablette|Tropfen)\b', t):
            probleme.append('Dosisangabe')

        # Die Belegstufe "nicht untersucht" muss ihren Absatz BEENDEN.
        schluss = await pg.evaluate("""() => {
            const ps = [...document.querySelectorAll('#r-waisen p')];
            const p = ps.find(x => x.innerText.includes('nicht untersucht'));
            return p ? p.innerText.trim().slice(-16) : 'KEIN ABSATZ';
        }""")
        print('  Absatzende mit n-Stufe:', repr(schluss))
        if 'nicht untersucht' not in schluss:
            probleme.append('Belegstufe n steht mitten im Absatz: %r' % schluss)

        n = await pg.locator('#r-waisen button.xlink').count()
        print('  Querverweise:', n)
        if n != 7:
            probleme.append('%d Querverweise, erwartet 7' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#r-waisen button.xlink').nth(i)
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
            else:
                print('   ok  "%s" -> Stoff %s' % (beschr[:34], await kn.get_attribute('data-sub')))

        for q in ['waisenrezeptor', 'gpr12', 'preprint']:
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
