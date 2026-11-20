# -*- coding: utf-8 -*-
"""Dauertest fuer den Reiter Interleukine.

WARUM DIESER REITER UEBERHAUPT: Gefragt war eine Darstellung aller Verbindungen
zwischen diesem System und dem Interleukin-Netz. Die Formatfrage (eigener
Reiter oder Grafik in der Koerperkarte) wurde GEMESSEN entschieden: Die Befunde
sitzen an ZELLTYPEN - Hautzellen, T-Zellen, Fresszell-Zelllinien -, nicht an
Organen. Auf der Koerperkarte wuerden sie einen Ort behaupten, den die Studien
nie gemessen haben. Ausserdem kennt die Koerperkarte nur eine Dichtestufe 0-3
pro Organ, waehrend eine Interleukin-Verbindung RICHTUNG und SPEZIES hat.

DREI FEHLER BEIM BAU, alle erst beim LESEN DES GERENDERTEN TEXTS gefunden -
und alle drei pruefen wir hier dauerhaft:

 1. GLOSSARBEGRIFFE IM SVG WURDEN GEFRESSEN. glossify haengt fuer jeden Begriff
    einen HTML-<button class="term"> in den Textknoten. Innerhalb eines <svg>
    wird ein HTML-Button nicht gezeichnet - der Begriff verschwand vollstaendig.
    Sichtbar war 'AM404 Pfeil' als bloss 'Pfeil', 'CB2-Stoff' als '-Stoff' und
    die Legende endete bei 'auch unter' statt 'unter Placebo'. Behoben an der
    Ursache: glossify nimmt jetzt 'svg' aus. Der Test prueft BEIDES - dass kein
    Glossarknopf mehr in einem SVG der ganzen Seite steckt, und dass die drei
    Beschriftungen vollstaendig dastehen.

 2. HANDGEZAEHLTE ZAHLEN, zweimal. Die Ueberschrift sagte '16 Befunde', die
    Grafik zeichnete 18. Der Satz darunter sagte, Cannabis-Wirkstoffe kaemen im
    Menschen-Feld 'zweimal' vor - es sind drei, zwei davon Nullbefunde. Beides
    rechnet der Reiter jetzt selbst aus IL_NET. Der Test rechnet unabhaengig
    nach und vergleicht mit dem gerenderten Text.

 3. ZU STARKE FORMULIERUNGEN. 'nicht ueber CB1 und CB2' las sich, als spielten
    die Rezeptoren keine Rolle - die Zellbefunde laufen ja gerade dort. Und
    'alle Verbindungen, die gemessen wurden' ist eine Vollstaendigkeits-
    behauptung ueber die Weltliteratur, die niemand halten kann. Der Test
    verbietet beide Fassungen.

WAS DER REITER INHALTLICH BEHAUPTET und was deshalb dastehen muss: Die
menschlichen Befunde stammen ueberwiegend aus dem Fettsaeureamid-Zweig (PEA,
OEA), dessen Hauptweg laut der Seite PPAR-alpha ist [[15465922]] und nicht
CB1/CB2. Fuer Cannabis findet die groesste Sichtung klinischer Studien keine
Zytokin-Aenderung [[39921765]]. Dazu drei Gegenbefunde, die ausdruecklich
dastehen muessen: IL-10 (die Bremse) sank mit, IL-8 STIEG unter Falcarinol, und
IL-4 sank auch unter Placebo.
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

BELEGE = ['34331010', '38572744', '38311974', '36057884', '36084236', '38068797', '26857391']
# Kernaussagen, ohne die der Reiter sein Ergebnis nicht traegt.
MUSS = [
    'PPAR-α',                       # der im Tierversuch belegte Weg
    'sind Zellbefunde',             # die Einordnung von CB1/CB2
    # Am 12.11.2026 nachtraeglich korrigiert: Der Reiter hatte den PPAR-Weg als
    # Weg AM MENSCHEN behauptet, gestuetzt auf einen Maeuse-Knockout - also
    # genau den Fehler, gegen den er argumentiert. Diese zwei Wendungen halten
    # die Korrektur fest.
    'in keiner dieser Studien gemessen',
    'Im Tierversuch ist der Weg PPAR-α',
    'IL-10 ist der bekannteste',    # Gegenbefund 1: die Bremse ging mit
    'erhöhte in menschlichen Hautzellen',  # Gegenbefund 2: dieselbe Achse hinauf
    'auch in der Placebogruppe',    # Gegenbefund 3: Placebo tat dasselbe
    'Keine dieser Arbeiten zeigt',  # keine Ursache belegt
    'nur von 36 der 108',           # die Blutwerte-Luecke
    'p = 0,05',                     # der Wert auf der Grenze
    'Interleukine wurden dort nicht gemessen',  # Zelle ist nicht Patient
]
# Fassungen, die zurueckgebaut wurden und nicht wiederkommen duerfen.
VERBOTEN = [
    'Sie läuft über den Fettsäureamid-Zweig und PPAR-α, nicht über CB1 und CB2.',
    'Verbindungen zusammen, die zwischen diesem System und einzelnen Interleukinen gemessen wurden',
    '16 Befunde',
    'kommen dort nur zweimal vor',
    'fast ausschließlich von',
    'kein Grund, sie weglassen',
    'PEAs Hauptwirkung läuft über PPAR-α',
    'läuft sie über den Fettsäureamid-Zweig und PPAR-α',
    'hängen überwiegend nicht an den Cannabinoid-Rezeptoren',
]
# Die Beschriftungen, die der Glossar-Fehler zerstoert hatte.
SVG_MUSS = ['AM404', 'CB2-Stoff', 'unter Placebo']


def _bands(zeile):
    """Die drei Baender einer IL-Zeile mit echtem Klammerzaehlen trennen.

    NICHT mit einem Regex: '\\[.*?\\]' bricht beim ERSTEN ']' ab und verliert in
    einem Band mit mehreren Befunden alles ab dem zweiten. Am 12.11.2026 hat
    genau dieser Fehler den Test 16 statt 18 Befunde melden lassen - waehrend
    die Grafik korrekt 18 zeichnete. Haette ich dem Test geglaubt, haette ich
    die richtige Seite auf eine falsche Zahl heruntergezogen. Der Vergleich mit
    der gezeichneten Pillenzahl im DOM hat das verhindert; er bleibt drin.
    """
    out, tiefe, start = [], 0, None
    for k, ch in enumerate(zeile):
        if ch == '[':
            if tiefe == 0:
                start = k
            tiefe += 1
        elif ch == ']':
            tiefe -= 1
            if tiefe == 0:
                out.append(zeile[start:k + 1])
    return out


def zahlen_aus_der_quelle():
    """IL_NET unabhaengig vom Seitencode nachrechnen."""
    S = io.open(QUELLE, encoding='utf-8').read()
    i = S.find('const IL_NET = [')
    assert i > 0, 'IL_NET fehlt'
    j = S.find('\n];', i)
    blk = S[i:j]
    treffer = re.findall(r"\n\s*(\['IL[^\n]*\])", blk)
    assert len(treffer) >= 8, 'nur %d IL-Zeilen gefunden' % len(treffer)
    fund = re.compile(r"\['[^']+','([a-z?]+)','([a-z])'\]")
    ges = mensch = fett = cann = null = 0
    for z in treffer:
        # Die Zeile ist selbst eine Klammergruppe - erst die aeussere abstreifen,
        # dann liegen genau die drei Baender darin (der IL-Name ist unbeklammert).
        bd = _bands(z.strip()[1:-1])
        assert len(bd) == 3, 'Zeile hat %d Baender, erwartet 3: %s' % (len(bd), z[:40])
        for bi, band in enumerate(bd):
            f = fund.findall(band)
            ges += len(f)
            if bi == 0:
                mensch += len(f)
                fett += sum(1 for r, k in f if k == 'f')
                cann += sum(1 for r, k in f if k == 'c')
                null += sum(1 for r, k in f if k == 'c' and r == 'o')
    return len(treffer), ges, mensch, fett, cann, null


async def main():
    probleme = []
    ilz, ges, mensch, fett, cann, null = zahlen_aus_der_quelle()
    print('  nachgerechnet: %d Interleukine, %d Befunde, davon %d am Menschen'
          ' (%d Fettsäureamid, %d Cannabis, %d Nullbefunde)'
          % (ilz, ges, mensch, fett, cann, null))

    S = io.open(QUELLE, encoding='utf-8').read()
    for p in BELEGE:
        if ("['%s'," % p) not in S:
            probleme.append('Beleg %s fehlt im Verzeichnis' % p)
        if ('[[%s]]' % p) not in S:
            probleme.append('Beleg %s wird nirgends benutzt' % p)
    if 'option,.tip,svg' not in S:
        probleme.append('glossify nimmt SVG nicht aus - Begriffe in Grafiken verschwinden')
    else:
        print('  ok  glossify nimmt SVG aus')
    if "'interleukine'" not in S:
        probleme.append('Reiter nicht in GROUPS eingetragen')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1200})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)
        await pg.click('#groups button[data-g="1"]')
        await pg.wait_for_timeout(350)
        kn = pg.locator('#tabs button:has-text("Interleukine")')
        if await kn.count() != 1:
            print('Probleme: Reiter Interleukine nicht in der Gruppe Praxis')
            await b.close(); sys.exit(1)
        await kn.click()
        await pg.wait_for_timeout(900)

        for cid in ('i-was', 'i-karte', 'i-bruch', 'i-gegen', 'i-grenzen', 'i-fazit'):
            if await pg.locator('#' + cid).count() != 1:
                probleme.append('Karte %s fehlt' % cid)
        ganz = await pg.inner_text('#tabpanel')
        if '${' in ganz:
            probleme.append('unaufgeloeste Vorlage im Reiter')
        for m in MUSS:
            if m not in ganz:
                probleme.append('Kernaussage fehlt: %s' % m)
        for v in VERBOTEN:
            if v in ganz:
                probleme.append('zurueckgebaute Fassung ist wieder da: %s' % v)
        print('  ok  sechs Karten, alle Kernaussagen, keine alte Fassung')

        # Die gerechneten Zahlen muessen mit der Nachrechnung uebereinstimmen.
        for soll, wo in ((ges, '%d Befunde' % ges), (ilz, 'acht Interleukinen'),
                         (mensch, 'den %d Befunden am Menschen' % mensch),
                         (fett, '<b>%d von PEA oder OEA</b>' % fett)):
            t = wo.replace('<b>', '').replace('</b>', '')
            if t not in ganz:
                probleme.append('gerechnete Zahl stimmt nicht mit IL_NET: erwartet "%s"' % t)
        if 'dreimal vor' in ganz and cann != 3:
            probleme.append('Text sagt dreimal, IL_NET sagt %d' % cann)
        print('  ok  alle Zahlen im Text stimmen mit IL_NET')

        # Die Grafik: Beschriftungen vollstaendig, nichts ausserhalb, nichts ueberlappend.
        g = await pg.evaluate("""() => {
          const sv = [...document.querySelectorAll('#tabpanel svg')]
            .find(s => (s.getAttribute('aria-label') || '').includes('Interleukinen'));
          if (!sv) return 'SVG FEHLT';
          const vb = sv.getAttribute('viewBox').split(' ').map(Number);
          const raus = [];
          sv.querySelectorAll('rect,text').forEach(e => { const b = e.getBBox();
            if (b.x < -1 || b.x + b.width > vb[2] + 1 || b.y < -1 || b.y + b.height > vb[3] + 1)
              raus.push((e.textContent || e.tagName).slice(0, 28)); });
          const pil = [...sv.querySelectorAll('rect[rx]')].map(e => e.getBBox());
          const ov = [];
          for (let i = 0; i < pil.length; i++) for (let j = i + 1; j < pil.length; j++) {
            const a = pil[i], c = pil[j];
            if (a.x < c.x + c.width && c.x < a.x + a.width &&
                a.y < c.y + c.height && c.y < a.y + a.height) ov.push(i + '/' + j); }
          // NUR der wirklich gezeichnete Text: In einem <text> malt SVG seine
          // eigenen Textknoten. Ein hineingehaengtes HTML-Element - etwa der
          // Glossarknopf - steckt in textContent, wird aber NICHT gezeichnet.
          // Deshalb waere eine Pruefung gegen textContent gruen, obwohl der
          // Leser nichts sieht (am 12.11.2026 genau so passiert).
          let gemalt = '';
          sv.querySelectorAll('text').forEach(t => {
            t.childNodes.forEach(n => { if (n.nodeType === 3) gemalt += n.nodeValue; });
            gemalt += ' '; });
          return {pillen: pil.length, raus, ov, text: gemalt};
        }""")
        if g == 'SVG FEHLT':
            probleme.append('die Netzgrafik fehlt')
        else:
            if g['pillen'] != ges:
                probleme.append('Grafik zeichnet %d Pillen, IL_NET hat %d Befunde'
                                % (g['pillen'], ges))
            if g['raus']:
                probleme.append('Grafik laeuft aus dem Bild: %s' % g['raus'])
            if g['ov']:
                probleme.append('Pillen ueberlappen: %s' % g['ov'])
            for m in SVG_MUSS:
                if m not in g['text']:
                    probleme.append('Beschriftung in der Grafik verstuemmelt, fehlt: %s' % m)
            if not g['raus'] and not g['ov']:
                print('  ok  Grafik: %d Pillen, im Bild, ohne Ueberlappung,'
                      ' Beschriftungen vollstaendig' % g['pillen'])

        # Kein Glossarknopf in IRGENDEINEM SVG der ganzen Seite.
        drin = 0
        for grp in range(4):
            await pg.click('#groups button[data-g="%d"]' % grp)
            await pg.wait_for_timeout(220)
            n = await pg.locator('#tabs button').count()
            for i in range(n):
                await pg.locator('#tabs button').nth(i).click()
                await pg.wait_for_timeout(300)
                drin += await pg.locator('#tabpanel svg button.term').count()
        if drin:
            probleme.append('%d Glossarknoepfe stecken in SVGs - dort verschwindet der Text' % drin)
        else:
            print('  ok  kein Glossarknopf in einem SVG der ganzen Seite')

        # Keine Dosisangabe bei den erhaeltlichen Stoffen dieses Reiters.
        await pg.click('#groups button[data-g="1"]')
        await pg.wait_for_timeout(250)
        await pg.locator('#tabs button:has-text("Interleukine")').click()
        await pg.wait_for_timeout(700)
        t = await pg.inner_text('#tabpanel')
        for d in (' mg', 'Milligramm'):
            if d in t:
                probleme.append('Dosisangabe im Reiter: %s' % d)

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
