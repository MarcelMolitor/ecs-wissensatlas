# -*- coding: utf-8 -*-
"""Dauertest: die CB1-Matrix des Wirkstoff-Labors kennt DREI Zustaende, und der
dritte wird auch als dritter markiert.

WARUM DIESER TEST GEBRAUCHT WIRD: Die Matrix kannte zwei Zustaende - "geprueft"
(ein CB1_RUN-Eintrag) und "nie versucht" (kein Eintrag, Gedankenstrich). Fuer
"begonnen und dann still geworden" hatte sie keinen. Genau dieselbe Luecke wie
bei der Dichteskala der Koerperkarte, die keine Stufe fuer "nicht gemessen"
hatte (siehe t/organstufe.py).

Aufgefallen ist es erst am GERENDERTEN Reiter: In der Zelle peri|gastro stand
ein Kreuz und "HIER WAERE SCHLUSS" ueber einem Text, der ausdruecklich sagt, es
sei weder bestanden noch gescheitert. In der Quelldatei faellt das nicht auf,
weil dort nur eine Zahl steht; erst der Browser macht daraus ein Kreuz.

Der Test haelt vier Dinge fest:
 1. Die Zelle peri|gastro existiert und traegt die Kurzmarke
    "begonnen, kein Ergebnis".
 2. Im Trichter steht dort ein FRAGEZEICHEN, kein Kreuz, und die Ueberschrift
    "Hier wurde es still".
 3. Eine gescheiterte Zelle (peri|niere) traegt weiter das Kreuz und
    "Hier waere Schluss" - die Einfuehrung des dritten Zustands darf die
    beiden alten nicht verschoben haben.
 4. Die gerechneten Zahlen der Einleitung stimmen mit der Tabelle ueberein:
    Spalten x Zeilen = genannte Kombinationen, und die Zahl der stillen Zellen
    wird genannt. Die Seite rechnet diese Zahlen aus den Objekten (CB1_N,
    CB1_NGEP, CB1_NSTILL) - handgeschriebene Zahlen sind hier schon einmal
    veraltet, deshalb wird die Rechnung selbst geprueft.

AUSSERDEM: Kein <b> in den Abbruchkaesten. .stage-fail b wird per CSS zur
Ueberschrift (display:block, uppercase) - ein inline gemeintes Fettwort wird
dort stillschweigend zu einer Abschnittsueberschrift, und der Satz danach
beginnt klein. Genau das ist mir am 12.11.2026 passiert.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'
QUELLE = HIER + '/page.html'   # 15.11.: war die Arbeitsdatei, nicht der Pruefling


async def zum_labor(pg):
    await pg.click('#groups button[data-g="3"]')
    await pg.wait_for_timeout(300)
    await pg.click('#tabs button:has-text("Wirkstoff-Labor")')
    await pg.wait_for_timeout(700)
    # Vorlage Rimonabant schaltet in den CB1-Modus, in dem die Matrix steht.
    await pg.locator('.qchip[data-preset="6"]').click()
    await pg.wait_for_timeout(650)


async def zelle(pg, how, use):
    await pg.locator('.cb1cell[data-how="%s"][data-use="%s"]' % (how, use)).click()
    await pg.wait_for_timeout(700)
    return (await pg.eval_on_selector_all('#labRun .stage-n', 'e => e.map(x => x.textContent)'),
            await pg.eval_on_selector_all('#labRun .stage-fail b', 'e => e.map(x => x.textContent)'),
            await pg.inner_text('#labRun'))


async def main():
    probleme = []
    import io
    S = io.open(QUELLE, encoding='utf-8').read()

    # --- Quelldatei: keine <b> in den Texten, die im Abbruchkasten landen ---
    for name in ('CB1_RUN', 'CB1_DAMIT', 'CB2_DAMIT', 'LAB_DAMIT'):
        m = re.search(r'const %s = \{' % name, S)
        if not m:
            probleme.append('%s nicht gefunden' % name); continue
        j = m.end(); t = 1; k = j
        while t:
            if S[k] == '{': t += 1
            elif S[k] == '}': t -= 1
            k += 1
        if '<b>' in S[j:k - 1]:
            probleme.append('%s enthaelt <b> - wird im Abbruchkasten zur Ueberschrift' % name)
    # --- Quelldatei: eine einzige Definition fuer "still" ---
    if 'const cb1Still = r =>' not in S:
        probleme.append('cb1Still() fehlt - Zahl und Markierung koennten auseinanderlaufen')
    if S.count('/kein Ergebnis/') != 1:
        probleme.append('"kein Ergebnis" wird an %d Stellen geprueft, erwartet genau 1 (cb1Still)'
                        % S.count('/kein Ergebnis/'))

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1000})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1700)
        await zum_labor(pg)

        # 1. Die stille Zelle in der Tabelle
        z = pg.locator('.cb1cell[data-how="peri"][data-use="gastro"]')
        if await z.count() != 1:
            probleme.append('Zelle peri|gastro fehlt')
        else:
            txt = (await z.inner_text()).strip()
            if 'begonnen, kein Ergebnis' not in txt:
                probleme.append('Kurzmarke peri|gastro: "%s"' % txt)
            else:
                print('  ok  Kurzmarke peri|gastro: begonnen, kein Ergebnis')
            # Eine angefasste Zelle hat KEINEN Gedankenstrich - sonst saehe sie leer aus.
            if await z.locator('.cb1dash').count():
                probleme.append('peri|gastro zeigt den Gedankenstrich einer leeren Zelle')

        # 2. Der Trichter: Fragezeichen, nicht Kreuz
        marken, ueber, ganz = await zelle(pg, 'peri', 'gastro')
        print('  peri|gastro Marken:', marken)
        if '?' not in marken:
            probleme.append('peri|gastro ohne Fragezeichen im Trichter: %s' % marken)
        if '✕' in marken:
            probleme.append('peri|gastro traegt ein Kreuz - das heisst gescheitert')
        if not any('still' in u.lower() for u in ueber):
            probleme.append('peri|gastro ohne Ueberschrift "Hier wurde es still": %s' % ueber)
        else:
            print('  ok  Ueberschrift: %s' % ueber[0])
        for muss in ('sechs Teilnehmende', 'nicht veröffentlicht', 'Angefangen, nicht berichtet'):
            if muss not in ganz:
                probleme.append('peri|gastro fehlt: %s' % muss)
        # Kein klein beginnender Satz nach einer Ueberschrift.
        for m in re.finditer(r'\n([a-zäöüß])', ganz):
            probleme.append('Satz beginnt klein: "...%s..."'
                            % ganz[max(0, m.start() - 30):m.start() + 40].replace('\n', '|'))

        # 3. Eine gescheiterte Zelle bleibt gescheitert
        marken2, ueber2, _ = await zelle(pg, 'peri', 'niere')
        print('  peri|niere  Marken:', marken2)
        if '✕' not in marken2:
            probleme.append('peri|niere ohne Kreuz: %s' % marken2)
        if not any('Schluss' in u for u in ueber2):
            probleme.append('peri|niere ohne "Hier waere Schluss": %s' % ueber2)
        else:
            print('  ok  peri|niere weiter: %s' % ueber2[0])

        # 4. Die gerechneten Zahlen gegen die Tabelle
        r = await pg.evaluate("""() => {
            const sp = document.querySelectorAll('.cb1m thead th').length - 1;
            const ze = document.querySelectorAll('.cb1m tbody tr').length;
            const zellen = document.querySelectorAll('.cb1m .cb1cell').length;
            const leer = document.querySelectorAll('.cb1m .cb1dash').length;
            const still = [...document.querySelectorAll('.cb1m .cb1cell')]
                .filter(c => /begonnen, kein Ergebnis/.test(c.textContent)).length;
            return {sp, ze, zellen, leer, still,
                    txt: document.getElementById('tabpanel').innerText};
        }""")
        print('  Tabelle: %d Spalten x %d Zeilen = %d Zellen, %d leer, %d still'
              % (r['sp'], r['ze'], r['zellen'], r['leer'], r['still']))
        if r['sp'] * r['ze'] != r['zellen']:
            probleme.append('Tabelle unvollstaendig: %dx%d != %d Zellen'
                            % (r['sp'], r['ze'], r['zellen']))
        if 'nie an einem Menschen geprüft' not in r['txt']:
            probleme.append('Einleitung nennt die leeren Felder nicht')
        if r['still'] and 'still geworden' not in r['txt']:
            probleme.append('Einleitung nennt den dritten Zustand nicht, obwohl es ihn gibt')
        # Die genannte Gesamtzahl muss die gerechnete sein.
        if str(r['zellen']) not in r['txt']:
            probleme.append('Die Zahl %d steht nicht im Text - Rechnung und Tabelle uneinig'
                            % r['zellen'])
        else:
            print('  ok  genannte Gesamtzahl %d stimmt mit der Tabelle' % r['zellen'])
        # Angefasst = alle Zellen minus die leeren. Muss mit der Zahl im Text zusammenpassen.
        angefasst = r['zellen'] - r['leer']
        if angefasst < 1:
            probleme.append('keine einzige angefasste Zelle - Matrix leer?')
        if r['still'] > angefasst:
            probleme.append('mehr stille (%d) als angefasste (%d) Zellen'
                            % (r['still'], angefasst))
        print('  ok  %d angefasst, davon %d still' % (angefasst, r['still']))

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
