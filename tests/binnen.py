# -*- coding: utf-8 -*-
"""Dauertest fuer die Binnenverteilungs-Marke auf der Hirnkarte.

WAS SIE LEISTET: Die Hirnkarte zeigt EINEN Dichtewert je Region. Die Karte
g-nichtgleich sagt seit dem 12.11.2026, dass das eine Vereinfachung ist - aber
nur als Satz. Die Marke zeigt jetzt auf der Karte selbst, WO diese
Vereinfachung am meisten verdeckt: bei fuenf Regionen, deren Wert nachweislich
ein Mittel ueber stark verschiedene Teile ist. Beim Hirnstamm ist das der
Unterschied zwischen 'spaerlich besetzt' und 'am Vaguskern hohe Dichten'.

Die fuenf sind: Grosshirnrinde, Basalganglien, Thalamus, Kleinhirn, Hirnstamm.

BEWUSST OHNE MARKE: das HOEHLENGRAU. Dort gehen nicht die Werte innerhalb der
Region auseinander, sondern ZWEI ARTEN VON MESSUNG - Dichtekarte gegen
Wirkungsversuch im Rattenhirn. Die Marke wuerde ihre Bedeutung verlieren, wenn
sie beides hiesse. Dieser Test haelt fest, dass das Hoehlengrau KEINE
Marke bekommt, damit das nicht spaeter 'vervollstaendigt' wird.

ZWEI EIGENE FEHLER BEIM BAU, beide festgehalten:
 1. Der erste Pruefblick suchte die Marken in '#bodySvg' und fand NULL - die
    Hirnkarte zeichnet aber in '#brainSvg'. Fast haette ich eine funktionierende
    Aenderung fuer kaputt erklaert. MERKEN: Koerperkarte und Hirnkarte sind
    zwei verschiedene SVG-Elemente.
 2. Ich hatte den Rinden-Befund (Assoziationsfelder hoch, primaere Felder
    niedrig) in das Feld basis geschrieben, weil er dort fehlte - er stand aber
    bereits ausfuehrlicher im Feld fuer die Bedeutung. Ich hatte nur basis
    gelesen und daraus auf ein Fehlen geschlossen. Der Zusatz wurde wieder
    entfernt; dieser Test verbietet ihn, damit er nicht zurueckkommt.
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

MIT_MARKE = ['Großhirnrinde', 'Basalganglien', 'Thalamus', 'Kleinhirn', 'Hirnstamm']
OHNE_MARKE = ['Höhlengrau', 'Hippocampus', 'Amygdala', 'Nucleus accumbens',
              'Entorhinalrinde', 'Hypothalamus', 'Stirnhirn', 'Globus pallidus',
              'Brechzentrum', 'Substantia nigra', 'Tegmentum (VTA)', 'Gyrus cinguli', 'Inselrinde', 'Riechkolben']
# Der Zusatz, der eine Doppelung war und nicht zurueckkommen darf.
VERBOTEN = 'Die eine Stufe für die ganze Rinde ist dabei ein Mittelwert'


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    if S.count("uneven:'") != len(MIT_MARKE):
        probleme.append('%d uneven-Felder, erwartet %d' % (S.count("uneven:'"), len(MIT_MARKE)))
    if VERBOTEN in S:
        probleme.append('die entfernte Doppelung im Rinden-Beleg ist zurueck')
    if '.runeven{' not in S:
        probleme.append('CSS der Marke fehlt - sie waere unsichtbar')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1100})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)
        await pg.click('#viewSeg button[data-v="brain"]')
        await pg.wait_for_timeout(700)

        g = await pg.evaluate("""() => {
          // Die Hirnkarte ist #brainSvg, NICHT #bodySvg. Ein Blick in das
          // falsche Element meldet null Marken, obwohl alles stimmt.
          const sv = document.getElementById('brainSvg');
          if (!sv) return 'brainSvg FEHLT';
          const vb = sv.getAttribute('viewBox').split(' ').map(Number);
          const mk = [...sv.querySelectorAll('.runeven')]
            .map(e => e.parentElement.textContent.replace('±', '').trim());
          const sicht = [...sv.querySelectorAll('.runeven')]
            .filter(e => { const b = e.getBBox(); return b.width > 0 && b.height > 0; }).length;
          const lab = [...sv.querySelectorAll('.rlabel')];
          const raus = lab.filter(e => { const b = e.getBBox();
            return b.x < 0 || b.x + b.width > vb[2] + 1; }).map(e => e.textContent);
          const bb = lab.map(e => e.getBBox()); const ov = [];
          for (let i = 0; i < bb.length; i++) for (let j = i + 1; j < bb.length; j++) {
            const a = bb[i], c = bb[j];
            if (a.x < c.x + c.width && c.x < a.x + a.width &&
                a.y < c.y + c.height && c.y < a.y + a.height)
              ov.push(lab[i].textContent + '/' + lab[j].textContent); }
          const al = [...sv.querySelectorAll('.region')]
            .filter(e => (e.getAttribute('aria-label') || '').includes('Mittelwert')).length;
          return {marken: mk, sichtbar: sicht, raus, ov, mitHinweis: al,
                  legende: (document.getElementById('legUneven') || {}).textContent || ''};
        }""")
        if g == 'brainSvg FEHLT':
            print('Probleme: brainSvg fehlt'); await b.close(); sys.exit(1)

        if sorted(g['marken']) != sorted(MIT_MARKE):
            probleme.append('Marken stehen an %s, erwartet %s' % (sorted(g['marken']), sorted(MIT_MARKE)))
        else:
            print('  ok  Marke an genau den fuenf vorgesehenen Regionen')
        if g['sichtbar'] != len(MIT_MARKE):
            probleme.append('nur %d von %d Marken haben eine Flaeche - unsichtbar?'
                            % (g['sichtbar'], len(MIT_MARKE)))
        if g['mitHinweis'] != len(MIT_MARKE):
            probleme.append('%d Regionen tragen den Hinweis in der Vorlesehilfe, erwartet %d'
                            % (g['mitHinweis'], len(MIT_MARKE)))
        else:
            print('  ok  Vorlesehilfe nennt den Mittelwert-Hinweis')
        if g['raus']:
            probleme.append('Beschriftung laeuft aus dem Bild: %s' % g['raus'])
        if g['ov']:
            probleme.append('Beschriftungen ueberlappen: %s' % g['ov'])
        if not g['raus'] and not g['ov']:
            print('  ok  Beschriftungen im Bild und ohne Ueberlappung')
        if 'Mittelwert' not in g['legende']:
            probleme.append('Legendenzeile zur Marke fehlt - die Marke waere ein Raetsel')
        else:
            print('  ok  Legende erklaert die Marke')

        # Die Tafeln: markierte Region zeigt den Satz, nicht markierte nicht.
        for k, name in [('cortex', 'Großhirnrinde'), ('brainstem', 'Hirnstamm')]:
            await pg.locator('#rg-' + k).evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(420)
            t = await pg.inner_text('#organInfo')
            if 'Mittelwert über ungleich besetzte Teile' not in t:
                probleme.append('Tafel %s erklaert die Marke nicht' % name)
        for k, name in [('pag', 'Höhlengrau'), ('hippocampus', 'Hippocampus')]:
            await pg.locator('#rg-' + k).evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(420)
            t = await pg.inner_text('#organInfo')
            if 'Mittelwert über ungleich besetzte Teile' in t:
                probleme.append('%s traegt den Hinweis, obwohl es ihn nicht bekommen soll'
                                % name)
        print('  ok  Tafeln: markierte erklaeren die Marke, die anderen nicht')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
