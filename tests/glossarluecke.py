# -*- coding: utf-8 -*-
"""Wie oft begegnet man einem Glossarwort DORT, wo es nicht erklaert wird?

Die Seite hat zwei Verzeichnisse: TERMS (antippbar im Text) und den
Glossar-Reiter (eine Liste, die man aufsuchen muss). Diese Messung zaehlt fuer
jedes Wort des Glossar-Reiters, wie oft es im Text der ANDEREN 23 Reiter und in
den Stofftexten vorkommt. Nur wo diese Zahl gross ist, lohnt ein Eintrag in
TERMS - ein antippbares Wort, dem man nie begegnet, aendert nichts.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

# Wort -> Suchmuster (Mehrzahl mitgedacht)
WORT = [
    ('Agonist',               r'Agonist(?:en)?'),
    ('Homöostase',            r'Homöostase'),
    ('Negative Rückkopplung', r'[Nn]egative[nr]? Rückkopplung'),
    ('Endocannabinoid-Tonus', r'Endocannabinoid-Tonus'),
    ('Herunterregulierung',   r'[Hh]erunterregul\w+'),
    ('TNF',                   r'TNF'),
    ('Zytokin',               r'Zytokin(?:e|en)?'),
    ('Mikroglia',             r'Mikroglia'),
    ('Prostaglandin',         r'Prostaglandin(?:e|en)?'),
    ('Vasopressin',           r'Vasopressin'),
    ('Hypothalamus',          r'Hypothalamus'),
    ('Dendrit',               r'Dendrit(?:en)?'),
    ('MAP-Kinase',            r'MAP-Kinase(?:n)?'),
    ('JNK',                   r'JNK'),
    ('Apoptose',              r'Apoptose'),
]


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)
        texte, glossar = [], ''
        ng = await pg.evaluate('document.querySelectorAll("#groups button").length')
        for g in range(ng):
            await pg.click('#groups button[data-g="%d"]' % g)
            await pg.wait_for_timeout(300)
            for i in range(await pg.evaluate('document.querySelectorAll("#tabs button").length')):
                t = pg.locator('#tabs button').nth(i)
                lbl = await t.inner_text()
                await t.click()
                await pg.wait_for_timeout(280)
                txt = await pg.inner_text('#tabpanel')
                assert len(txt) > 80, 'Reiter %s leer' % lbl
                if lbl.strip() == 'Glossar':
                    glossar = txt
                else:
                    texte.append(txt)
        # UNTERE GRENZE, keine feste Zahl: Die Seite bekommt Reiter dazu (zuletzt
        # "Herkunft"), und dieser Test hat deswegen monatelang rot gestanden.
        assert len(texte) >= 24 and glossar, 'Erwartet mindestens 24 Reiter + Glossar, habe %d / %s' % (len(texte), bool(glossar))
        for sid in await pg.eval_on_selector_all('.chip', 'els => els.map(e => e.dataset.id)'):
            await pg.click('.chip[data-id="%s"]' % sid)
            await pg.wait_for_timeout(170)
            texte.append(await pg.inner_text('#subWhat') + ' ' + await pg.inner_text('#status')
                         + ' ' + await pg.inner_text('#steps'))
        await b.close()

    ganz = '\n'.join(texte)
    print('Text ohne Glossar-Reiter:', len(ganz), 'Zeichen\n')
    print('%-24s %s' % ('Wort', 'Nennungen ausserhalb des Glossars'))
    for name, pat in sorted(WORT, key=lambda x: -len(re.findall(x[1], ganz))):
        print('  %-22s %4d' % (name, len(re.findall(pat, ganz))))


asyncio.run(main())
