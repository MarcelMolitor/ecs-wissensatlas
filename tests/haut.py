# -*- coding: utf-8 -*-
"""Haut-Tafel und Hautfelder (14.11.2026).

DER BEFUND DIESER RUNDE: CB1 daempft das Schwitzen - an Maeusen gemessen, mit
Gegenprobe an Tieren ohne CB1 und ohne CB2 [[42287607]]. THC senkte die
Schweissabgabe, CBD nicht. Die Rezeptoren sitzen NICHT auf den Druesenzellen,
sondern auf den Nervenfasern darum herum - dieselbe Bauweise wie an der
Speicheldruese. Beides muss in der Tafel stehen, weil beides die Aussage traegt.

DIE FALLE: Es ist naheliegend, daraus "THC laesst dich weniger schwitzen" zu
machen. Gemessen ist das an Maeusen, nicht am Menschen. Der Test verlangt den
einschraenkenden Satz und verbietet die Kurzform.

ZWEI VORBEHALTE beim CBG-Feld muessen beide stehen: Die klinische Pruefung ist
ein REIZMODELL (keine Hautkrankheit) und stammt aus den FORSCHUNGSABTEILUNGEN
DER HERSTELLER. Faellt einer weg, liest sich eine Firmenstudie an 20 Personen
wie ein Wirksamkeitsnachweis.

CBN: Das Feld behauptete frueher Zellstudien, die sich nicht belegen liessen.
Es steht jetzt auf 0 mit der Uebersicht, die die Belege minimal nennt. Taucht
die Behauptung ohne Beleg wieder auf, meldet der Test das.
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

NEU = ['42287607', '36769042', '35056807']
TAFEL_MUSS = [
    'An Mäusen senkt ein CB1-Aktivator die Schweißabgabe',
    'CBD nicht',
    'nicht auf den Drüsenzellen, sondern auf den Nervenfasern',
    'Am Menschen ist das Schwitzen unter Cannabis nicht gemessen',
    'eine Dichtezahl für die menschliche Haut trägt diese Seite nicht',
]
TAFEL_VERBOTEN = [
    'THC lässt dich weniger schwitzen',
    'THC senkt das Schwitzen beim Menschen',
    'hilft gegen übermäßiges Schwitzen',
]
STUFEN = {'thc': 'Schwache Wirkung', 'aea': 'Schwache Wirkung',
          'cbg': 'Schwache Wirkung', 'cbn': 'Nicht untersucht'}
FELD_MUSS = {
    'thc': ['bei Tieren ohne CB1 bleibt der Effekt aus', 'Am Menschen ist das nicht gemessen'],
    'aea': ['örtlicher Kreis aus CB1 und Anandamid', 'ist damit nicht gemessen'],
    'cbg': ['20 Personen mit künstlich gereizter Haut', 'Reizmodell statt einer Hautkrankheit',
            'Forschungsabteilungen der Hersteller'],
    'cbn': ['keine Studie', 'minimal'],
}


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    T = S[S.find('<title>'):]
    for p in NEU:
        if ("['%s'," % p) not in T: probleme.append('Beleg %s fehlt im Verzeichnis' % p)
        if ('[[%s]]' % p) not in T: probleme.append('Beleg %s wird nicht benutzt' % p)

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1050})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1800)

        for sid, soll in STUFEN.items():
            kn = pg.locator('button.chip[data-id="%s"]' % sid)
            if not await kn.count(): probleme.append('kein Auswahlknopf fuer %s' % sid); continue
            await kn.first.evaluate("e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(260)
            await pg.locator('#or-skin').evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(280)
            t = await pg.inner_text('#organInfo')
            if '${' in t or '[[' in t: probleme.append('%s: Vorlagenrest in der Hauttafel' % sid)
            m = re.search(r'\n(Nicht untersucht|Schwache Wirkung|Deutliche Wirkung|Starke Wirkung)\.', t)
            if not m or m.group(1) != soll:
                probleme.append('%s/skin steht auf "%s", erwartet "%s"'
                                % (sid, m.group(1) if m else '??', soll))
            for s in FELD_MUSS[sid]:
                if s not in t: probleme.append('%s/skin: fehlt »%s«' % (sid, s))
            if sid == 'thc':
                for s in TAFEL_MUSS:
                    if s not in t: probleme.append('Hauttafel: fehlt »%s«' % s)
                for v in TAFEL_VERBOTEN:
                    if v in t: probleme.append('Hauttafel: unerwuenscht »%s«' % v)
                for d in (' mg', 'Milligramm'):
                    if d in t: probleme.append('Hauttafel: Dosisangabe')
                kn2 = pg.locator('#organInfo .xlink[data-organ="mund"]')
                if await kn2.count() != 1:
                    probleme.append('Verweis auf die Speicheldruese fehlt')
                else:
                    await kn2.first.click(); await pg.wait_for_timeout(700)
                    titel = (await pg.inner_text('#organInfo')).split('\n')[0]
                    if 'Mund' not in titel:
                        probleme.append('Verweis auf die Speicheldruese fuehrt zu: %s' % titel)
                    await pg.locator('#or-skin').evaluate(
                        "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
                    await pg.wait_for_timeout(250)
        print('  ok  vier Hautfelder und die Tafel geprueft')
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler: sys.exit(1)

asyncio.run(main())
