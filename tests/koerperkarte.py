# -*- coding: utf-8 -*-
"""Dauertest fuer die Koerperkarte: Vollstaendigkeit, Belege und Geometrie.

WARUM: Am 12.11.2026 gemessen - alle 17 Organtafeln trugen Belege im Feld
"woher man das weiss", da war nichts offen. Die Luecke lag woanders: Die
mengenmaessige Uebersicht menschlicher Gewebe [[7556170]], auf die sich diese
Karte stuetzt, listet CB1 in Nebenniere, Herz, Lunge, Prostata, Gebaermutter,
Eierstock, Hoden, Knochenmark, Thymus und Mandeln. Alle standen auf der Karte -
bis auf die NEBENNIERE. Und die ist kein Nebenschauplatz: In den hormonbildenden
Zellen des Nebennierenmarks steckt die hoechste gemessene Menge jener
koerpereigenen Peptide, die an den Cannabinoid-Rezeptoren mitregeln
[[25839900]], und entfernt man die Nebennieren, sinkt der staendig im Blut
vorhandene Anteil [[28842619]]. Drei Belege, die alle schon auf der Seite
standen - nur nicht auf der Karte.

DIE GEOMETRIE WIRD MITGEPRUEFT, weil sie sich beim Zufuegen eines Organs
leicht verzieht und das Augenmass hier taeuscht (siehe t/hirnkarte.py, wo
isPointInFill mein Augenmass widerlegt hat). Geprueft werden drei Dinge, die
alle beim Einbau der Nebenniere aufgetreten sind:
 1. Keine zwei Marken duerfen sich ueberdecken.
 2. Keine zwei Beschriftungen duerfen sich ueberlappen oder aus dem Bild
    laufen.
 3. KEINE FUEHRUNGSLINIE DARF EINE ANDERE KREUZEN. Die Nebenniere kreuzte
    zuerst die Linie des Immunsystems, weil ihre Beschriftung ueber der des
    Immunsystems stand, ihre Marke aber darunter. Beim Nachrechnen fiel dann
    eine ZWEITE Kreuzung auf, die es schon lange gab: Haut und Pankreas. Auch
    behoben.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, io, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'
QUELLE = HIER + '/page.html'   # 15.11.: war die Arbeitsdatei, nicht der Pruefling

# Die Gewebe, die [[7556170]] als CB1-tragend nennt, muessen auf der Karte
# auffindbar sein - entweder als eigenes Organ oder im Text eines Organs.
AUS_DER_QUELLE = ['Nebenniere', 'Herz', 'Lunge', 'Prostata', 'Gebärmutter',
                  'Eierstock', 'Hoden', 'Knochenmark', 'Thymus', 'Mandeln']
MIND_ORGANE = 18


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    m = re.search(r'const ORGANS\s*=\s*\{', S)
    j = m.end(); t = 1; k = j
    while t:
        if S[k] == '{': t += 1
        elif S[k] == '}': t -= 1
        k += 1
    blk = S[j:k - 1]
    namen = re.findall(r"\n  \w+:\{name:'([^']*)'", blk)
    print('  Organe:', len(namen))
    if len(namen) < MIND_ORGANE:
        probleme.append('nur %d Organe, erwartet mindestens %d' % (len(namen), MIND_ORGANE))
    if 'Nebenniere' not in namen:
        probleme.append('Nebenniere fehlt - sie steht in [[7556170]] unter den CB1-Geweben')
    # Jede Tafel braucht einen Beleg im Feld basis.
    for e in re.finditer(r"\n  (\w+):\{name:'([^']*)'.*?basis:'((?:[^'\\]|\\.)*)'", blk, re.S):
        if '[[' not in e.group(3):
            probleme.append('Organtafel %s ohne Beleg' % e.group(2))
    # Die Gewebe der Quelle muessen irgendwo auf der Seite vorkommen.
    for g in AUS_DER_QUELLE:
        if g not in S:
            probleme.append('Gewebe aus [[7556170]] kommt nirgends vor: %s' % g)
    print('  ok  alle Organtafeln belegt, alle Gewebe der Quelle vorhanden')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1200})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)

        r = await pg.evaluate("""() => {
          const sv = document.getElementById('bodySvg');
          const vb = sv.getAttribute('viewBox').split(' ').map(Number);
          const org = [...document.querySelectorAll('#bodySvg .organ')].map(g => {
            const c = g.querySelector('circle, .ring-base');
            return [g.dataset.k, +c.getAttribute('cx'), +c.getAttribute('cy')];});
          const nah = [];
          for (let i = 0; i < org.length; i++) for (let j = i + 1; j < org.length; j++) {
            const d = Math.hypot(org[i][1] - org[j][1], org[i][2] - org[j][2]);
            if (d < 16) nah.push(org[i][0] + '/' + org[j][0] + '=' + d.toFixed(1)); }
          const L = [...document.querySelectorAll('#bodySvg line')].map(l => ({k: l.id,
            x1: +l.getAttribute('x1'), y1: +l.getAttribute('y1'),
            x2: +l.getAttribute('x2'), y2: +l.getAttribute('y2')}));
          const cc = (a, b, c) => (c.y - a.y) * (b.x - a.x) > (b.y - a.y) * (c.x - a.x);
          const kr = (p, q) => { const A = {x: p.x1, y: p.y1}, B = {x: p.x2, y: p.y2},
                                       C = {x: q.x1, y: q.y1}, D = {x: q.x2, y: q.y2};
            return cc(A, C, D) !== cc(B, C, D) && cc(A, B, C) !== cc(A, B, D); };
          const x = [];
          for (let i = 0; i < L.length; i++) for (let j = i + 1; j < L.length; j++)
            if (kr(L[i], L[j])) x.push(L[i].k + ' x ' + L[j].k);
          const tx = [...document.querySelectorAll('#bodySvg .olabel')];
          const ov = [];
          for (let i = 0; i < tx.length; i++) for (let j = i + 1; j < tx.length; j++) {
            const a = tx[i].getBBox(), c = tx[j].getBBox();
            if (a.x < c.x + c.width && c.x < a.x + a.width &&
                a.y < c.y + c.height && c.y < a.y + a.height)
              ov.push(tx[i].textContent + '/' + tx[j].textContent); }
          const raus = tx.filter(e => { const bb = e.getBBox();
            return bb.x < 0 || bb.x + bb.width > vb[2]; }).map(e => e.textContent);
          return {n: org.length, nah, kreuz: x, ov, raus};
        }""")
        print('  gezeichnete Organe:', r['n'])
        if r['n'] < MIND_ORGANE:
            probleme.append('nur %d Organe gezeichnet' % r['n'])
        if r['nah']:
            probleme.append('Marken ueberdecken sich: %s' % r['nah'])
        else:
            print('  ok  keine Marke ueberdeckt eine andere')
        if r['kreuz']:
            probleme.append('Fuehrungslinien kreuzen sich: %s' % r['kreuz'])
        else:
            print('  ok  keine Fuehrungslinie kreuzt eine andere')
        if r['ov']:
            probleme.append('Beschriftungen ueberlappen: %s' % r['ov'])
        if r['raus']:
            probleme.append('Beschriftungen laufen aus dem Bild: %s' % r['raus'])
        if not r['ov'] and not r['raus']:
            print('  ok  Beschriftungen frei und im Bild')

        # Die Nebenniere-Tafel inhaltlich
        o = pg.locator('#or-nebenniere')
        if await o.count() != 1:
            probleme.append('Marke der Nebenniere fehlt')
        else:
            await o.evaluate("e => e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(500)
            txt = await pg.inner_text('#organInfo')
            for muss in ('Nebenniere', 'Quelle', 'ausgespült', 'Entfernt man die Nebennieren',
                         'am lebenden Menschen ist diese Rolle nicht gemessen'):
                if muss not in txt:
                    probleme.append('Nebenniere-Tafel fehlt: %s' % muss)
            # Keine Steigerung ueber das Gemessene hinaus.
            for weg in ('große Wirkung auf das Ganze', 'steuert den ganzen Körper'):
                if weg in txt:
                    probleme.append('Formulierung ueber das Gemessene hinaus: %s' % weg)
            if 'Nebenniere' in txt:
                print('  ok  Nebenniere-Tafel vollstaendig, mit Vorbehalt')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
