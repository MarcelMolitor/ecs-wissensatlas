# -*- coding: utf-8 -*-
"""Dauertest: die Hirnansicht bleibt vollstaendig, ihre Formen bleiben im Kopf,
und die Befunde ihrer eigenen Quelle bleiben drin.

WARUM DIESER TEST GEBRAUCHT WIRD: Auf die Frage "fehlen nicht noch mehr
Hirnteile?" wurde am 12.11.2026 nicht gegen mein Gedaechtnis gemessen, sondern
gegen die zwei Arbeiten, auf denen die Karte selbst beruht - Herkenham 1990
[[2308954]] und Glass 1997 [[9472392]]. Ergebnis: Die ENTORHINALRINDE, der
Glass "high concentrations" zuschreibt, kam auf der ganzen Seite null Mal vor.
Dazu drei Befunde derselben Arbeit, die nie erzaehlt wurden (Dichtegefaelle zu
den Assoziationsfeldern, Schichtung in der Tiefe, und die durchgehend hoehere
Dichte in der linken, sprachdominanten Halbkugel).

BEINAHE-FEHLER, der den Test mitbegruendet: Ich wollte aus dem Gedaechtnis das
PERIAQUAEDUKTALE GRAU ergaenzen - bei einer Seite mit Schmerz-Reiter sehr
naheliegend. Glass sagt aber ausdruecklich "very low levels of labelling in
all other midbrain areas". Die Region waere falsch gewesen. Der Test verbietet
sie deshalb, bis jemand eine Quelle dafuer hat.

UND: Die geometrische Pruefung unten hat mein Augenmass korrigiert. Im
Bildschirmfoto sah die neue Form aus, als rage sie unten aus dem Gehirn
heraus; isPointInFill zeigte, dass alle Randpunkte drinliegen. Umgekehrt kann
eine verschobene Form im Kleinen unsichtbar danebenliegen. Deshalb wird das
gerechnet und nicht angesehen.
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

# Regionen, die die Karte fuehren MUSS. Die vier zuletzt genannten nennt Glass
# als hoch oder sehr hoch besetzt; faellt eine heraus, fehlt wieder ein Hirnteil.
PFLICHT = ['Großhirnrinde', 'Gyrus cinguli', 'Stirnhirn', 'Basalganglien', 'Globus pallidus',
           'Nucleus accumbens', 'Thalamus', 'Inselrinde', 'Hypothalamus', 'Amygdala',
           'Riechkolben', 'Entorhinalrinde', 'Hippocampus', 'Kleinhirn', 'Höhlengrau',
           'Tegmentum (VTA)', 'Substantia nigra',
           # 21.11.2026: Das Mittelhirn war verkehrt herum eingetragen - die
           # Substantia nigra oben, das Hoehlengrau unten in der Bruecke.
           # Richtig ist dorsoventral: Hoehlengrau, Tegmentum, Substantia nigra.
           # Mit den Formen wandert ly mit, sonst kreuzten sich die drei
           # Beschriftungslinien. Darum steht hier jetzt die neue Folge.
           'Brechzentrum', 'Hirnstamm']
# Von oben nach unten GELESEN, nicht in der Reihenfolge des Quelltexts: Das
# Hoehlengrau steht im BRAIN-Objekt bewusst zuletzt, weil die Regionen in
# Deklarationsreihenfolge gezeichnet werden und es sonst vom Hirnstamm
# UEBERMALT wird - erst die Vergroesserung hat das gezeigt, im Gesamtbild war
# an der Stelle schlicht nichts zu sehen. Die Beschriftungen stehen trotzdem in
# anatomischer Ordnung, weil ihre Hoehe (ly) getrennt vergeben wird.
# Befunde der eigenen Quelle, die im Text stehen muessen.
BEFUNDE = ['sprachdominanten', 'Assoziationsfeldern', 'Gyrus dentatus', 'Subiculum',
           'Ammonshorn',
           # Kleinhirn: Die Tafel trug bis 12.11.2026 EINEN Satz, und das Feld 'woher man
           # das weiss' endete mit einer Behauptung ohne Beleg. Beides faellt sonst leicht
           # wieder heraus, weil es die dichteste Region mit der kuerzesten Tafel war.
           'Molekularschicht', 'Purkinje-Zellen', 'vierfach abgesichert',
           'Größe der Veränderung',
           # Hippocampus und Nucleus accumbens trugen am 12.11.2026 die zwei
           # KUERZESTEN Tafeln der Karte - der Hippocampus bei HOECHSTER Dichtestufe,
           # dieselbe Unwucht wie zuvor beim Kleinhirn. Und die Region, in der die
           # Rueckwaerts-Bremse entdeckt wurde, sagte das selbst nicht.
           'rückwärts an ihre eigenen Eingänge', 'DAGL-α fällt sie hier aus',
           # Accumbens: die Herkunftsangabe war unbelegt ('kleine Studien am Menschen
           # und Tierversuche') und die Haelfte eines Befundes fehlte, dessen andere
           # Haelfte in der Amygdala-Tafel steht.
           '82 gesunden Erwachsenen', 'entgegengesetzte Richtungen']
# Wird eine dieser Regionen je in die KARTE aufgenommen, dann nicht als dicht
# besetzt. GENAU GELESEN, weil dieser Test sich hier zuerst selbst geirrt hat:
# Er verbot "periaquaeduktal" auf der GANZEN Seite - und schlug sofort an, denn
# die Seite fuehrt das periaquaeduktale Grau laengst, im Schmerz-Reiter, mit
# gezielten Mikroinjektionsstudien [[16129456]]. Das ist voellig richtig und
# etwas anderes als eine Dichteangabe: Glass misst BINDUNGSSTELLEN im
# menschlichen Gewebe und nennt das Mittelhirn ausserhalb der Substantia nigra
# gering besetzt; Suplita misst WIRKUNG am Rattenhirn. Wenige Rezeptoren heissen
# nicht keine Wirkung - derselbe Punkt, den die Karte beim Thalamus schon macht.
# Die Pruefung gilt deshalb nur noch fuer das BRAIN-Objekt, nicht fuer die Seite.
NUR_MIT_VORBEHALT = ['periaquäduktal', 'Periaquäduktal', 'Höhlengrau']


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    m = re.search(r'const BRAIN = \{', S)
    if not m:
        probleme.append('BRAIN-Objekt nicht gefunden')
    else:
        j = m.end(); t = 1; k = j
        while t:
            if S[k] == '{': t += 1
            elif S[k] == '}': t -= 1
            k += 1
        karte = S[j:k - 1]
        for w in NUR_MIT_VORBEHALT:
            if w in karte and 'gering' not in karte[max(0, karte.find(w) - 400):
                                                   karte.find(w) + 600]:
                probleme.append('"%s" steht in der Hirnkarte ohne den Hinweis auf die geringe'
                                ' Bindungsdichte im Mittelhirn' % w)

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1100})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1700)
        await pg.click('#viewSeg button[data-v="brain"]')
        await pg.wait_for_timeout(800)

        # 1. Vollstaendigkeit und Reihenfolge der Beschriftungen
        lab = await pg.eval_on_selector_all(
            '#brainSvg .rlabel',
            "e => e.map(x => [x.textContent, Math.round(x.getBBox().y),"
            " Math.round(x.getBBox().x + x.getBBox().width)])")
        # Die Marke fuer die ungleiche Binnenverteilung (Plusminus) haengt seit
        # dem 12.11.2026 als eigener tspan an fuenf Beschriftungen. Sie gehoert
        # NICHT zum Namen, also wird sie hier abgestreift - dieser Test fragt
        # nach Vollstaendigkeit und anatomischer Reihenfolge, nicht nach der
        # Verzierung. t/binnen.py prueft die Marke selbst.
        namen = [l[0].replace('\u00b1', '').strip() for l in sorted(lab, key=lambda t: t[1])]
        print('  Regionen:', len(namen))
        for n in PFLICHT:
            if n not in namen:
                probleme.append('Region fehlt: %s' % n)
        if namen != PFLICHT:
            probleme.append('Reihenfolge der Beschriftungen weicht ab:\n    ist  %s\n    soll %s'
                            % (namen, PFLICHT))
        else:
            print('  ok  alle %d Regionen, in anatomischer Reihenfolge' % len(namen))

        vb = await pg.get_attribute('#brainSvg', 'viewBox')
        breit = float(vb.split()[2])
        for name, y, x1 in lab:
            if x1 > breit:
                probleme.append('Beschriftung "%s" laeuft rechts aus dem Bild (%d > %d)'
                                % (name, x1, breit))
        ys = sorted(l[1] for l in lab)
        abst = {ys[i + 1] - ys[i] for i in range(len(ys) - 1)}
        if len(abst) != 1:
            probleme.append('Beschriftungen ungleich verteilt, Abstaende: %s' % sorted(abst))
        else:
            print('  ok  Beschriftungen gleichmaessig, Abstand %d, keine laeuft raus' % abst.pop())

        # 2. Jede Form liegt INNERHALB der Hirnkontur. Das Augenmass taeuscht hier.
        raus = await pg.evaluate("""() => {
          const sv = document.getElementById('brainSvg');
          const cortex = document.querySelector('#rg-cortex .rshape');
          const pt = sv.createSVGPoint(), schlecht = [];
          document.querySelectorAll('#regions .region').forEach(g => {
            if (g.id === 'rg-cortex') return;
            const s = g.querySelector('.rshape');
            const bb = s.getBBox(), m = s.getCTM ? null : null;
            let drausen = 0, n = 0;
            if (s.tagName === 'path'){
              // Eine frei gezeichnete Form (Stirnhirn, seit 13.11.2026) ist keine
              // Ellipse: Die Ellipse ihres Rahmens ragt ueber sie hinaus und
              // meldete 7 von 24 Punkten draussen, obwohl die Form drinnen lag.
              // Deshalb hier Punkte auf dem UMRISS selbst, 6 % zur Mitte gerueckt.
              const L = s.getTotalLength(), cx = bb.x + bb.width/2, cy = bb.y + bb.height/2;
              for (let i = 0; i < 24; i++){
                const q = s.getPointAtLength(L * i / 24);
                pt.x = q.x + (cx - q.x) * 0.06; pt.y = q.y + (cy - q.y) * 0.06;
                n++;
                if (!cortex.isPointInFill(pt)) drausen++;
              }
            } else
            for (let a = 0; a < 360; a += 15){
              const t = a * Math.PI/180;
              pt.x = bb.x + bb.width/2  + (bb.width/2)  * Math.cos(t) * 0.98;
              pt.y = bb.y + bb.height/2 + (bb.height/2) * Math.sin(t) * 0.98;
              n++;
              if (!cortex.isPointInFill(pt)) drausen++;
            }
            if (drausen) schlecht.push([g.dataset.k, drausen, n]);
          });
          return schlecht;
        }""")
        # Kleinhirn, Hirnstamm und das im Hirnstamm liegende Hoehlengrau liegen
        # bauartbedingt ausserhalb der Grosshirnkontur.
        AUSNAHME = {'cerebellum', 'brainstem', 'pag', 'brech', 'nigra', 'vta', 'olf'}
        for k, d, n in raus:
            if k in AUSNAHME:
                continue
            probleme.append('Form von %s liegt zu %d/%d ausserhalb der Hirnkontur' % (k, d, n))
        drin = [k for k, _, _ in raus if k not in AUSNAHME]
        print('  ok  Formen innerhalb der Kontur (ausser %s, bauartbedingt)'
              % ', '.join(sorted(AUSNAHME)) if not drin else '  PROBLEM: %s' % drin)

        # 2b. Das Hoehlengrau liegt IM Hirnstamm. Es muss nach ihm gezeichnet werden
        #     und eine andere Fuellung tragen, sonst ist es schlicht unsichtbar -
        #     im Gesamtbild war an der Stelle zuerst gar nichts zu sehen.
        sicht = await pg.evaluate("""() => {
          const alle = [...document.querySelectorAll('#regions .region')].map(g => g.dataset.k);
          const p = document.querySelector('#rg-pag .rshape');
          const b = document.querySelector('#rg-brainstem .rshape');
          return {reihenfolge: alle.indexOf('pag') > alle.indexOf('brainstem'),
                  pagFill: p.getAttribute('fill'), bsFill: b.getAttribute('fill')};
        }""")
        if not sicht['reihenfolge']:
            probleme.append('Hoehlengrau wird VOR dem Hirnstamm gezeichnet und daher uebermalt')
        elif sicht['pagFill'] == sicht['bsFill']:
            probleme.append('Hoehlengrau hat dieselbe Fuellung wie der Hirnstamm - unsichtbar')
        else:
            print('  ok  Hoehlengrau liegt sichtbar im Hirnstamm')

        # 3. Die Befunde der eigenen Quelle stehen im Text
        ganz = ''
        for k in ('entorhinal', 'cortex', 'hippocampus', 'cerebellum', 'accumbens'):
            await pg.locator('#rg-' + k).evaluate(
                "e => e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(420)
            ganz += await pg.inner_text('#organInfo')
        for muss in BEFUNDE:
            if muss not in ganz:
                probleme.append('Befund der eigenen Quelle fehlt im Text: %s' % muss)
        if not [m for m in BEFUNDE if m not in ganz]:
            print('  ok  alle %d Befunde der Quelle im Text' % len(BEFUNDE))

        # 4. Die Entorhinalrinde darf nicht als gemessene Funktion auftreten.
        await pg.locator('#rg-entorhinal').evaluate(
            "e => e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
        await pg.wait_for_timeout(420)
        ent = await pg.inner_text('#organInfo')
        if 'Anatomie und keine Messung' not in ent:
            probleme.append('Entorhinalrinde ohne den Vorbehalt, dass die Funktion'
                            ' Anatomie und keine Messung dieser Arbeit ist')
        else:
            print('  ok  Entorhinalrinde traegt ihren Vorbehalt')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
