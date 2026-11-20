# -*- coding: utf-8 -*-
"""Die vier Zustaende des CB1-Trichters muessen eindeutig und sichtbar getrennt
bleiben: geprueft/gescheitert, Zulassung zurueckgenommen, still geworden, laeuft
noch. Jede Zelle gehoert zu genau einem, und die Markierung muss zum Text passen.

VORGESCHICHTE. Am 12.11.2026 stand ein KREUZ und "Hier waere Schluss" ueber
einem Text, der sagte, es sei weder bestanden noch gescheitert - ehrliche Prosa
unter unehrlicher Markierung. Daraufhin entstand der dritte Zustand (still).
Am 20.11.2026 passierte derselbe Fehler nochmal: nam|cud bekam ein Kreuz und
"Hier waere Schluss" ueber eine LAUFENDE Phase 3. Daraufhin der vierte Zustand.

Beide Male war der Fehler in der Quelldatei nicht zu sehen - nur am gerenderten
Reiter. Darum prueft dieser Test die Markierung am Browser und nicht im Text.

Dazu zwei Fallen, die beim Einbau zuschlugen:
- CB1_DAMIT ist die Parallelstruktur zu CB1_RUN und muss deckungsgleich sein.
- Der Still-Hinweis zaehlte "der drei Zustaende" auf. Ein vierter Zustand macht
  so einen mitzaehlenden Satz still falsch. Dieser Test haelt die Zahl fest.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None
import asyncio, io, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'
QUELLE = (sys.argv[1].replace('file://', '') if len(sys.argv) > 1
          else HIER + '/page.html')

# Welche Ueberschrift zu welchem Zustand gehoert.
KOPF_STILL = 'Hier wurde es still'
KOPF_LAEUFT = 'Hier steht es gerade'
KOPF_ENDE = 'Hier wäre Schluss'
KOPF_ZURUECK = 'Bis hierher – und zurück'

probleme = []


def quelle_pruefen():
    S = io.open(QUELLE, encoding='utf-8').read()

    # 1) Beide Strukturen deckungsgleich
    def keys(name):
        i = S.find('const ' + name); j = S.find('\n};', i)
        return set(re.findall(r"^ '([a-z]+\|[a-z]+)'", S[i:j], re.M))
    r, d = keys('CB1_RUN'), keys('CB1_DAMIT')
    if r != d:
        probleme.append('CB1_RUN und CB1_DAMIT laufen auseinander: %s' % (r ^ d))
    print('Zellen in CB1_RUN: %d, in CB1_DAMIT: %d' % (len(r), len(d)))

    # 2) Jede Zelle genau ein Zustand
    i = S.find('const CB1_RUN'); j = S.find('\n};', i)
    zustand = {}
    for m in re.finditer(r"^ '([a-z]+\|[a-z]+)':\[(\d+),'[^']*','.*?','([^']*)'\]",
                         S[i:j], re.M | re.S):
        k, stufe, kurz = m.group(1), int(m.group(2)), m.group(3)
        st = 'kein Ergebnis' in kurz
        la = 'läuft' in kurz
        zu = 4 if stufe == 4 else 'still' if st else 'laeuft' if la else 'ende'
        if st and la:
            probleme.append('%s loest still UND laeuft aus: %s' % (k, kurz))
        zustand[k] = (zu, stufe, kurz)
        print('  %-14s %-7s Stufe %d  %s' % (k, zu, stufe, kurz))
    if not zustand:
        probleme.append('keine Zelle gelesen - Muster passt nicht mehr')

    # 3) Die beiden Praedikate muessen existieren und je einmal definiert sein
    for name in ['cb1Still', 'cb1Laeuft']:
        if S.count('const %s =' % name) != 1:
            probleme.append('%s nicht genau einmal definiert' % name)

    # 4) Ein mitzaehlender Satz. Vier Zustaende, also "vier".
    if 'der vier Zustände' not in S:
        probleme.append('Der Still-Hinweis zaehlt nicht vier Zustaende - '
                        'nach einem fuenften Zustand hier nachziehen')
    if 'der drei Zustände' in S:
        probleme.append('Es steht noch "der drei Zustände" auf der Seite')
    return zustand


async def main():
    zustand = quelle_pruefen()
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1300, 'height': 1400})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1200)
        await pg.click('#groups button[data-g="3"]'); await pg.wait_for_timeout(300)
        await pg.click('#tabs button:has-text("Wirkstoff-Labor")')
        await pg.wait_for_timeout(700)
        await pg.locator('.qchip[data-preset="6"]').click()
        await pg.wait_for_timeout(650)

        print()
        for k, (zu, stufe, kurz) in sorted(zustand.items()):
            how, use = k.split('|')
            z = pg.locator('.cb1cell[data-how="%s"][data-use="%s"]' % (how, use))
            if not await z.count():
                probleme.append('%s: Zelle fehlt im Reiter' % k); continue
            await z.click(); await pg.wait_for_timeout(600)
            marken = await pg.eval_on_selector_all('#labRun .stage-n',
                                                   'e => e.map(x => x.textContent)')
            koepfe = await pg.eval_on_selector_all('#labRun .stage-fail b',
                                                   'e => e.map(x => x.textContent)')
            kopf = koepfe[0] if koepfe else ''
            marke = marken[stufe] if stufe < len(marken) else '?'
            soll_kopf = {4: KOPF_ZURUECK, 'still': KOPF_STILL,
                         'laeuft': KOPF_LAEUFT, 'ende': KOPF_ENDE}[zu]
            soll_marke = {4: '✕', 'still': '?', 'laeuft': '→', 'ende': '✕'}[zu]
            ok = (kopf == soll_kopf and marke == soll_marke)
            print('  %-14s %s  Marke %s  "%s"' % (k, 'ok ' if ok else 'FEHLER',
                                                  marke, kopf))
            if kopf != soll_kopf:
                probleme.append('%s: Ueberschrift "%s", erwartet "%s"'
                                % (k, kopf, soll_kopf))
            if marke != soll_marke:
                probleme.append('%s: Marke "%s" auf Stufe %d, erwartet "%s"'
                                % (k, marke, stufe, soll_marke))
            # Der Kern der Sache: ein Kreuz darf nicht ueber einem Text stehen,
            # der sagt, es sei nicht gescheitert.
            txt = await pg.inner_text('#labRun')
            if marke == '✕' and ('läuft' in kurz or 'kein Ergebnis' in kurz):
                probleme.append('%s: KREUZ ueber einem Text, der kein Scheitern '
                                'behauptet - genau der Fehler vom 12.11.' % k)
            if 'nie veröffentlicht worden' in txt and 'läuft' in kurz:
                probleme.append('%s: Hinweis behauptet "nie veroeffentlicht" '
                                'ueber eine laufende Studie' % k)

        ueber = await pg.evaluate(
            'document.documentElement.scrollWidth - document.documentElement.clientWidth')
        if ueber > 0:
            probleme.append('Ueberlauf %d px' % ueber)
        if errs:
            probleme.append('JS-Fehler: %s' % errs)
        print()
        print('Ueberlauf:', ueber)
        print('Fehler:', errs or 'keine')
        await b.close()

    print('Probleme:', probleme or 'keine')
    if probleme:
        sys.exit(1)


asyncio.run(main())
