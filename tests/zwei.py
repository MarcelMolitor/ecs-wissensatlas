# -*- coding: utf-8 -*-
"""Brust & Milch und Speiseroehre (14.11.2026).

BRUST & MILCH ist die heikelste Tafel der Koerperkarte, weil sie stillende
Menschen betrifft. Drei Dinge muessen darin stehen und bleiben:
  1. WAS gemessen ist: Uebertritt, Anreicherung, Nachweis ueber Tage, der
     geschaetzte Anteil beim Kind.
  2. WAS NICHT gemessen ist: die Folgen fuer das Kind. Faellt dieser Satz weg,
     liest sich die Tafel wie eine Gefahrenmeldung oder wie eine Entwarnung -
     beides waere erfunden.
  3. WESSEN Rat das ist: Die Vorsichtsempfehlung stammt von den Autoren der
     Verlaufsmessung, nicht von dieser Seite. Der Test verlangt die
     Zuschreibung.
KEINE ng/ml-Werte - die bleiben draussen. Die Anteile (63 Prozent, 2,5 Prozent,
sechs Tage) sind das Ergebnis und keine Dosierung.

SPEISEROEHRE ist ein Musterfall der Seite: Der Mechanismus ist getroffen
(weniger voruebergehende Erschlaffungen des Schliessmuskels), die Anwendung
scheitert trotzdem - in der hoeheren Menge bekam die HAELFTE der Teilnehmenden
Uebelkeit und Erbrechen. Wer nur die erste Haelfte nennt, macht aus der Studie
eine Empfehlung gegen Sodbrennen.

AUSSERDEM GEPRUEFT: dass der Verweis auf die Karte "Die ersten Tage" traegt -
sie behandelt das Saugverhalten (Maeuse) und ist die andere Haelfte des Themas.
Beim Bauen war dieser Verweis zuerst kaputt: Die Vorlage stand als Text statt
als eingesetzter Knopf in der Seite - gueltiges JavaScript, das node --check
durchlaesst, aber zur Laufzeit die ganze Organliste zerstoert hat. Deshalb
prueft dieser Test den Knopf im gerenderten Zustand.
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

NEU = ['30150212', '33469174', '29630019', '42512209', '19068079', '20425477']
BRUST_MUSS = [
    'was im Blut der Mutter ist, kann in sie übergehen',
    '63 Prozent nachweisbar',
    'rund sechs Tage nach dem letzten Konsum',
    'etwa 2,5 Prozent der mütterlichen Menge',
    'mehr als bei Müttern, die nur verdampften',
    'Was das für das Kind bedeutet, ist in keiner dieser Arbeiten gemessen',
    'die Autoren der Verlaufsmessung raten zur Vorsicht',   # Zuschreibung, nicht eigener Rat
]
BRUST_VERBOTEN = [
    'Stillen Sie nicht',
    'sollten nicht stillen',
    'ist unbedenklich',
    'schadet dem Kind',
    'ng/ml', 'ng/mL', ' mg',
]
ESO_MUSS = [
    'genau diese Erschlaffungen trifft THC',
    'Der Mechanismus ist getroffen, die Anwendung scheitert trotzdem',
    'bekam die Hälfte der Teilnehmenden Übelkeit und Erbrechen',
    'sank nicht statistisch sicher',
]
ESO_VERBOTEN = ['hilft gegen Sodbrennen', 'wirkt gegen Reflux', 'Behandlung von Sodbrennen']


async def main():
    probleme = []
    T = io.open(QUELLE, encoding='utf-8').read()
    T = T[T.find('<title>'):]
    for p in NEU:
        if ("['%s'," % p) not in T: probleme.append('Beleg %s fehlt im Verzeichnis' % p)
        if ('[[%s]]' % p) not in T: probleme.append('Beleg %s wird nicht benutzt' % p)
    # Unersetzte Vorlage: gueltiges JS, aber zur Laufzeit toedlich
    if 'X%(' in T: probleme.append('unersetzte Vorlage X%( im Seitentext')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1080})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1800)

        n = await pg.locator('#bodySvg .organ').count()
        if n != 23: probleme.append('%d Organe statt 23' % n)
        for k in ('brust', 'eso'):
            if not await pg.locator('#or-' + k).count():
                probleme.append('Stelle fehlt: %s' % k)
        if probleme and any('fehlt: ' in x for x in probleme):
            print('Probleme:', probleme); await b.close(); sys.exit(1)

        # Marker auf dem Koerper, Beschriftungen im Bild
        drin = await pg.evaluate("""()=>{const sv=document.getElementById('bodySvg');
          const f=[...sv.querySelectorAll('path,ellipse,rect')].filter(e=>!e.closest('.organ'));
          const pt=sv.createSVGPoint();
          return ['brust','eso'].map(k=>{const m=document.querySelector('#or-'+k+' circle, #or-'+k+' ellipse');
            const bb=m.getBBox(); pt.x=bb.x+bb.width/2; pt.y=bb.y+bb.height/2;
            return [k, f.some(q=>{try{return q.isPointInFill(pt)}catch(e){return false}})]})}""")
        for k, ok in drin:
            if not ok: probleme.append('der Marker von %s liegt nicht auf dem Koerper' % k)
        raus = await pg.evaluate("""()=>{const sv=document.getElementById('bodySvg').getBoundingClientRect();
          return [...document.querySelectorAll('#bodySvg .olabel')].filter(t=>{const r=t.getBoundingClientRect();
            return r.left<sv.left-1||r.right>sv.right+1}).map(t=>t.textContent)}""")
        if raus: probleme.append('Beschriftung laeuft aus dem Bild: %s' % raus)

        await pg.locator('button.chip[data-id="thc"]').first.evaluate(
            "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(280)
        for k, muss, verboten in (('brust', BRUST_MUSS, BRUST_VERBOTEN),
                                  ('eso', ESO_MUSS, ESO_VERBOTEN)):
            await pg.locator('#or-' + k).evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(300)
            t = await pg.inner_text('#organInfo')
            if '${' in t or '[[' in t: probleme.append('%s: Vorlagenrest' % k)
            for s in muss:
                if s not in t: probleme.append('%s: fehlt »%s«' % (k, s))
            for v in verboten:
                if v in t: probleme.append('%s: unerwuenscht »%s«' % (k, v.strip()))
            if k == 'brust':
                kn = pg.locator('#organInfo .xlink[data-card="l-still"]')
                if await kn.count() != 1:
                    probleme.append('Verweis auf "Die ersten Tage" fehlt')
                else:
                    await kn.first.click(); await pg.wait_for_timeout(900)
                    if not await pg.evaluate("()=>{const c=document.getElementById('l-still');"
                                             " return c ? c.getBoundingClientRect().height>0 : false;}"):
                        probleme.append('der Verweis auf "Die ersten Tage" fuehrt ins Leere')
                    await pg.locator('button.chip[data-id="thc"]').first.evaluate(
                        "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
                    await pg.wait_for_timeout(280)
        print('  ok  beide Tafeln, Marker, Beschriftungen und der Verweis geprueft')
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler: sys.exit(1)

asyncio.run(main())
