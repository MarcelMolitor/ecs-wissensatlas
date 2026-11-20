# -*- coding: utf-8 -*-
"""Prueft den Reiter "Herkunft" (Gruppe Grundlagen) mit den Karten h-alt,
h-pflanze und h-folgen.

WORUM ES GEHT: Dieser Reiter beantwortet, warum eine Pflanze einen Stoff
herstellt, der in unsere Rezeptoren passt. Das ist die Frage, bei der im Netz
am meisten Unsinn steht, und zwar in zwei entgegengesetzte Richtungen:
 (1) "Der Koerper hat Rezeptoren dafuer, also ist die Pflanze fuer uns
     gedacht." Genau dieses Argument raeumt die Karte h-folgen ab. Der Test
     verlangt deshalb, dass der Satz von der umgekehrten Reihenfolge und das
     Wort "Zufall" drinstehen.
 (2) Umgekehrt duerfen die Pflanzenbefunde nicht zu einer Aussage ueber
     Menschen werden - gemessen sind Raupen und Blattlaeuse.

HARTE ZAHLEN, die der Test festhaelt, weil sie belegt sind: 222 gegen 13
Blattlaeuse nach 14 Tagen, und 13 Genome. Nicht festgehalten, sondern
VERBOTEN sind Jahresangaben zum Alter des Systems: in keiner der drei
Stammbaum-Zusammenfassungen steht eine Zahl, und erfundene Zahlen sind auf
dieser Seite mein haeufigster Fehler.

EBENFALLS VERBOTEN ist jede Zahl von Pflanzen ("drei weitere Pflanzen" war
beim Korrekturlesen falsch - die Seite fuehrt mehr und sagt selbst, dass es im
ganzen Pflanzenreich solche gibt).

NACHGEZOGEN AM 09.11.2026: Der taegliche Pruefer der Parallel-Sitzung hat vier
Formulierungen dieses Reiters verscharft, und zwar zu Recht - dieser Test
verlangt jetzt die GENAUEREN Fassungen, nicht die alten:
 - "Die Pflanze stellt diese Stoffe gegen Tiere her" -> "schuetzen die Pflanze
   offenbar UNTER ANDEREM vor Tieren ... die anderen vorgeschlagenen Aufgaben
   sind damit nicht ausgeschlossen". Geprueft war eine von drei Hypothesen.
 - "wozu er entstanden ist" -> "wozu er der Pflanze nuetzt". Heutiger Nutzen
   ist nicht die Entstehungsgeschichte.
 - "Insekten haben keinen Cannabinoid-Rezeptor" -> "fehlt Insekten -
   untersucht ist die Taufliege - ein Rezeptor vom Typ CB1". Elphick hat
   Taufliege und Fadenwurm angesehen, nicht "die Insekten".
 - "kann also nicht dieses System sein" -> "laeuft also sehr wahrscheinlich
   nicht ueber dieses System".

UND: Die Pointe des Reiters ist eine Beobachtung ueber ZWEI Literaturen
(Insekten haben keinen Cannabinoid-Rezeptor, trotzdem schadet ihnen der
Stoff). Der Test verlangt, dass sie als solche gekennzeichnet bleibt - faellt
der Satz heraus, steht da eine Schlussfolgerung, die in keiner Arbeit steht.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

KARTEN = ('h-alt', 'h-pflanze', 'h-folgen')

MUSS = {
 'h-alt': ['Fähigkeit, diese Moleküle herzustellen', 'einzelligen gemeinsamen Vorfahren',
           'im Modus der Möglichkeit', 'unabhängig entstanden sein', 'Lebermoose',
           'einem Fisch, einer Amphibie und einem Vogel', 'Taufliege und Fadenwurm fehlt er',
           'Seescheide', '13 Genome', 'Prostaglandine',
           'Bausteine sind alt und weit verbreitet'],
 'h-pflanze': ['Jahrzehntelang hat die Forschung gefragt', 'über ihren Nutzen für die Pflanze sei wenig',
               'UV-Strahlung', 'drei Stufen', 'Im Feld war der Fraßschaden umso geringer',
               'abgetrennten Blättern', 'Bau der Drüsenhaare', 'künstliche Insektennahrung',
               'Cannabidivarin-Säure', 'rund 222 Läuse', 'rund 13',
               'hatte zugleich deutlich mehr Drüsenhaare', 'schützen die Pflanze offenbar unter anderem vor Tieren',
               'nicht ausgeschlossen'],
 'h-folgen': ['fehlt Insekten', 'sehr wahrscheinlich nicht über dieses System',
              'steht kein Mechanismus', 'Beobachtung über zwei getrennte Literaturen',
              'in einer der Arbeiten dieses Reiters steht', 'Die Reihenfolge ist umgekehrt',
              'nie eine Hanfpflanze gesehen haben', 'keine Absicht, sondern ein Zufall',
              'über das ganze Pflanzenreich hinweg', 'Gleicher Rezeptor heißt nicht gleiches Tier',
              'nicht „für uns gemacht“'],
}
# Verbotenes, in BEIDE Richtungen.
VERBOTEN = [
    # erfundene Altersangaben
    'Millionen Jahre', 'Jahrmillionen', 'Mio. Jahre', 'vor 600', 'seit 500',
    # erfundene Pflanzenzahlen
    'drei weitere, voneinander unabhängige Pflanzen', 'vier Pflanzen', 'der fünf Arbeiten',
    # aus Pflanzenbefunden eine Menschenaussage machen
    'wirkt beim Menschen', 'schützt den Menschen', 'deshalb hilft',
    # Schoepfungs- bzw. Absichtssprache, die der Reiter gerade widerlegt
    'dafür gemacht', 'dafür bestimmt', 'von der Natur vorgesehen',
    # Insektenmittel als Empfehlung
    'sollte man spritzen', 'als Insektizid einsetzen',
    # falsches Deutsch, beim Korrekturlesen gefunden
    'einem Amphib ',
]


async def zum_reiter(pg):
    await pg.click('#groups button[data-g="0"]')
    await pg.wait_for_timeout(250)
    await pg.click('#tabs button:has-text("Herkunft")')
    await pg.wait_for_timeout(550)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1700)
        probleme = []

        # Der Reiter muss in der Gruppe Grundlagen stehen und dort auftauchen.
        await pg.click('#groups button[data-g="0"]')
        await pg.wait_for_timeout(300)
        namen = await pg.eval_on_selector_all('#tabs button', 'e => e.map(x => x.textContent)')
        print('  Grundlagen:', namen)
        if 'Herkunft' not in namen:
            probleme.append('Reiter Herkunft fehlt in der Gruppe Grundlagen')

        await zum_reiter(pg)
        for cid in KARTEN:
            chip = pg.locator('.qchip[data-jump="%s"]' % cid)
            if await chip.count() != 1:
                probleme.append('Sprungknopf %s fehlt' % cid)
            if await pg.locator('#' + cid).count() != 1:
                probleme.append('Karte %s fehlt' % cid)
                continue
            t = await pg.inner_text('#' + cid)
            print('  %-10s %d Zeichen' % (cid, len(t)))
            for muss in MUSS[cid]:
                if muss not in t:
                    probleme.append('%s fehlt: %s' % (cid, muss))

        ganz = await pg.inner_text('#tabpanel')
        for weg in VERBOTEN:
            if weg in ganz:
                probleme.append('Formulierung, die die Arbeiten nicht tragen: %s' % weg)
        # Keine Dosisangabe, nirgends.
        if re.search(r'\d+\s*(mg|Milligramm|Tablette|Tropfen)\b', ganz):
            probleme.append('Dosisangabe')
        # Belegstufen: drei m, ein s, ein n.
        for stufe, mind in [('teils belegt', 3), ('schwach belegt', 1), ('nicht untersucht', 1)]:
            if ganz.count(stufe) < mind:
                probleme.append('Belegstufe "%s" nur %dx, erwartet %d+'
                                % (stufe, ganz.count(stufe), mind))

        n = await pg.locator('#tabpanel button.xlink').count()
        print('  Querverweise:', n)
        if n < 7:
            probleme.append('nur %d Querverweise, erwartet 7+' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#tabpanel button.xlink').nth(i)
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
                    print('   ok  "%s" -> %s' % (beschr[:36], ziel))
            else:
                print('   ok  "%s" -> Stoff %s' % (beschr[:36], await kn.get_attribute('data-sub')))

        for q in ['seescheide', 'blattlaus', 'herkunft']:
            await pg.fill('#findQ', q)
            await pg.wait_for_timeout(520)
            n2 = await pg.eval_on_selector_all('#findRes [role=option]', 'e => e.length')
            print('  Suche "%s": %s Treffer' % (q, n2))

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
