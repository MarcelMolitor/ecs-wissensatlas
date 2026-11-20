# -*- coding: utf-8 -*-
"""Messung: Gibt es Glossareintraege, die auf der Seite NIE anspringen?

WARUM DIESE MESSUNG: Das Glossar markiert Fachwoerter im Text und zeigt beim
Antippen eine Erklaerung. Jeder Eintrag ist ein eigener regulaerer Ausdruck,
der so umschlossen wird:

    (?<![\\p{L}\\d-]) (?: MUSTER ) (?![\\p{L}\\d])

Hinten darf also KEIN Buchstabe folgen. Steht ein Begriff auf der Seite nur in
der Mehrzahl oder gebeugt ("Allele", "Synapsen", "Antagonisten"), springt sein
Eintrag nicht an - die Erklaerung ist vorhanden, aber unerreichbar. Ein Teil
der Eintraege fasst seine Beugungen selbst ab ("Zytokin(?:e|en)?"), ein Teil
nicht. Genau diese Luecke zaehlt dieses Skript.

Gemessen wird gegen den GERENDERTEN Text aller Reiter, nicht gegen die
Quelldatei - denn nur was im Text steht, kann markiert werden. Zusaetzlich
wird gezaehlt, wie viele .term-Knoepfe die Seite tatsaechlich erzeugt.

Das Skript ist eine MESSUNG, kein Dauertest: Es endet immer mit 0 und gibt
eine Liste aus, die entscheidet, was zu tun ist.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, io, json, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
QUELLE = HIER + '/page.html'   # 15.11.: war die Arbeitsdatei, nicht der Pruefling
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'


def terms_aus_quelle():
    S = io.open(QUELLE, encoding='utf-8').read()
    m = re.search(r'TERMS\s*=\s*\[', S)
    i = m.end()
    j = S.find('].map(([re, t, d])', i)
    blk = S[i:j]
    return [{'re': a, 't': b} for a, b in
            re.findall(r"\[\s*'((?:[^'\\]|\\.)*)'\s*,\s*'((?:[^'\\]|\\.)*)'", blk)]


async def main():
    terms = terms_aus_quelle()
    print('Glossareintraege in der Quelle:', len(terms))
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append(str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1700)

        # Alle Reiter durchblaettern, Text und erzeugte Knoepfe einsammeln.
        texte, knoepfe = [], 0
        gruppen = await pg.locator('#groups button').count()
        for g in range(gruppen):
            await pg.locator('#groups button').nth(g).click()
            await pg.wait_for_timeout(220)
            n = await pg.locator('#tabs button').count()
            for k in range(n):
                await pg.locator('#tabs button').nth(k).click()
                await pg.wait_for_timeout(230)
                texte.append(await pg.inner_text('#tabpanel'))
                knoepfe += await pg.locator('#tabpanel button.term').count()
        print('Reiter eingesammelt: %d | .term-Knoepfe insgesamt: %d' % (len(texte), knoepfe))

        # Im Browser pruefen, weil nur dort \p{L} und Lookbehind gleich wirken.
        ergebnis = await pg.evaluate("""([terms, texte]) => {
            const ganz = texte.join('\\n');
            const out = [];
            for (const T of terms){
                const streng = new RegExp('(?<![\\\\p{L}\\\\d-])(?:' + T.re + ')(?![\\\\p{L}\\\\d])', 'gu');
                const treffer = (ganz.match(streng) || []).length;
                // Ohne den Lookahead: faengt auch gebeugte und zusammengesetzte
                // Formen. ACHTUNG, hier lag ein Messfehler: Der lose Ausdruck
                // findet "Agonisten" auch dann, wenn das Muster es bereits
                // abdeckt - er verfolgt dann einfach zurueck auf "Agonist" und
                // nimmt "en" als Anhang. Gemeldet wird deshalb nur, was das
                // STRENGE Muster an derselben Stelle wirklich NICHT faengt.
                const lose = new RegExp('(?<![\\\\p{L}\\\\d-])(?:' + T.re + ')(\\\\p{L}{1,6})', 'gu');
                const anker = new RegExp('^(?:' + T.re + ')(?![\\\\p{L}\\\\d])', 'u');
                const formen = {};
                let m;
                while ((m = lose.exec(ganz)) !== null){
                    if (anker.test(ganz.slice(m.index))) continue;   // schon abgedeckt
                    const wort = m[0];
                    formen[wort] = (formen[wort] || 0) + 1;
                }
                out.push({t: T.t, re: T.re, treffer, formen});
            }
            return out;
        }""", [terms, texte])

        tot = [e for e in ergebnis if e['treffer'] == 0]
        verpasst = [e for e in ergebnis if e['formen']]

        print('\n=== TOTE EINTRAEGE (springen nirgends an) ===')
        if not tot:
            print('  keine')
        for e in tot:
            extra = ', '.join('%s x%d' % (k, v) for k, v in
                              sorted(e['formen'].items(), key=lambda x: -x[1])[:6])
            print('  %-24s Muster %-34s | im Text nur als: %s'
                  % (e['t'], e['re'], extra or 'gar nicht vorhanden'))

        print('\n=== EINTRAEGE MIT UNERREICHBAREN FORMEN ===')
        gesamt_verpasst = 0
        for e in sorted(verpasst, key=lambda x: -sum(x['formen'].values())):
            s = sum(e['formen'].values())
            gesamt_verpasst += s
            extra = ', '.join('%s x%d' % (k, v) for k, v in
                              sorted(e['formen'].items(), key=lambda x: -x[1])[:6])
            print('  %-24s %3d Treffer markierbar, %3d weitere Formen: %s'
                  % (e['t'], e['treffer'], s, extra))
        print('\nSUMME unerreichbarer Formen: %d' % gesamt_verpasst)
        print('Fehler:', fehler or 'keine')
        await b.close()


asyncio.run(main())
