# -*- coding: utf-8 -*-
"""Messung: Welche Fachbegriffe stehen auf der Seite, ohne erklaert zu werden?

Das Glossar (TERMS) erklaert 23 Begriffe durch Antippen. Diese Messung sammelt
den gerenderten Text ALLER Reiter, zaehlt Kandidaten fuer Fachsprache und zeigt,
welche davon kein Glossareintrag abdeckt - sortiert nach Haeufigkeit, damit
sichtbar wird, was Leserinnen wirklich oft begegnet.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys, collections
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

# Woerter, die lang und fremd aussehen, aber Alltagsdeutsch sind
HARMLOS = set("""
Endocannabinoide Endocannabinoid Endocannabinoid-System Cannabinoide Cannabinoid
Wissenschaft Untersuchung Untersuchungen Beobachtung Beobachtungen Veroeffentlichung
Teilnehmer Teilnehmerinnen Teilnehmende Entzuendung Entzuendungen Nebenwirkung
Nebenwirkungen Wechselwirkung Wechselwirkungen Verdauungstrakt Nervenzelle
Nervenzellen Immunzellen Wirkstoff Wirkstoffe Wirkung Wirkungen Behandlung
Zulassung Dosierung Erkrankung Erkrankungen Beschwerden Studie Studien
""".split())

# Grossgeschrieben, aber Alltagssprache: Tabellenkoepfe und Satzanfaenge
GROSSGESCHRIEBEN = set("""
DIE DER DAS UND SICH NICHT WAS WIE WO BEI VON MIT FUER AUF IST EIN EINE
ROLLE ZIELE BILDUNG ABBAU VORKOMMEN WIRKUNG WIRKUNGEN LIGANDEN ENZYME
ORGAN ORGANE STOFF STOFFE BELEG BELEGE STUDIE STUDIEN JAHR JAHRE
""".split())


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)

        # Glossarbegriffe, wie die Seite sie wirklich markiert
        erklaert = set()
        # Die Reiter liegen in drei Gruppen (#groups). Wer nur #tabs durchlaeuft,
        # erwischt acht von 24 - genau dieser Fehler hat den ersten Durchlauf
        # dieser Messung wertlos gemacht.
        texte = []
        ng = await pg.evaluate('document.querySelectorAll("#groups button").length')
        for g in range(ng):
            await pg.click('#groups button[data-g="%d"]' % g)
            await pg.wait_for_timeout(300)
            for i in range(await pg.evaluate('document.querySelectorAll("#tabs button").length')):
                await pg.locator('#tabs button').nth(i).click()
                await pg.wait_for_timeout(280)
                t = await pg.inner_text('#tabpanel')
                assert len(t) > 80, 'Reiter leer - Messung waere wertlos'
                texte.append(t)
                for x in await pg.eval_on_selector_all('#tabpanel .term', 'els => els.map(e => e.textContent)'):
                    erklaert.add(x.lower())
        assert len(texte) >= 25, 'nur %d Reiter eingesammelt, erwartet 25+' % len(texte)
        print('Reiter eingesammelt:', len(texte), '| Zeichen:', sum(len(x) for x in texte))
        # Stofftexte dazu
        for sid in await pg.eval_on_selector_all('.chip', 'els => els.map(e => e.dataset.id)'):
            await pg.click('.chip[data-id="%s"]' % sid)
            await pg.wait_for_timeout(180)
            texte.append(await pg.inner_text('#subWhat') + ' ' + await pg.inner_text('#status'))
            for t in await pg.eval_on_selector_all('#subWhat .term, #status .term', 'els => els.map(e => e.textContent)'):
                erklaert.add(t.lower())
        await b.close()

    ganz = '\n'.join(texte)
    # Kandidaten: Abkuerzungen in Grossbuchstaben, Woerter mit fremden Endungen
    kand = collections.Counter()
    # Ganze Token, Bindestriche eingeschlossen: ein Muster, das mitten im Wort
    # abbricht, erfindet Fachbegriffe wie "FAAH-H" oder "MS-S", die es nicht gibt.
    for w in re.findall(r'[A-Za-zÄÖÜäöüßα-ω][A-Za-zÄÖÜäöüßα-ω0-9]*(?:-[A-Za-zÄÖÜäöüßα-ω0-9]+)*', ganz):
        if w in HARMLOS or len(w) < 3:
            continue
        # Grossgeschriebene Tabellenkoepfe und Satzanfaenge sind keine Fachsprache
        if w.isupper() and (len(w) < 3 or w in GROSSGESCHRIEBEN):
            continue
        abk = bool(re.fullmatch(r'[A-ZÄÖÜ][A-ZÄÖÜ0-9α-ω]{1,}(?:-[A-ZÄÖÜa-zα-ω0-9]+)*', w))
        fach = bool(re.search(r'(ose$|itis$|ämie$|ologie|graphie|grafie|agonist|zeptor|enzym|synthese|'
                              r'lyse$|kinase|transferase|hydrolase|lipase|protein|peptid|metabolit|'
                              r'pathie$|algie$|zytose|phagen|glia|mitochondri)', w.lower()))
        if abk or fach:
            kand[w] += 1

    print('Glossar markiert auf der Seite:', len(erklaert), 'verschiedene Begriffe')
    print('\nFachwort-Kandidaten ohne Glossareintrag (ab 3 Nennungen):')
    n = 0
    for w, c in kand.most_common():
        if c < 3:
            break
        if w.lower() in erklaert:
            continue
        print('  %4d  %s' % (c, w))
        n += 1
    print('\ninsgesamt', n, 'ohne Erklaerung')


asyncio.run(main())
