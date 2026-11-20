#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tippfehler-Suche ohne Woerterbuch.

Ein Tippfehler kommt fast immer genau EINMAL vor und hat auf derselben
Seite einen richtigen Zwilling, der oft vorkommt: 'grueszte' neben
'groeszte'. Das Skript sammelt den sichtbaren Text aller Reiter und
Stoffprofile und meldet jedes einmalige Wort, das sich von einem
haeufigen Wort um genau einen Buchstaben unterscheidet.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, collections, sys
from playwright.async_api import async_playwright

URL = 'file://' + HIER + '/page.html'
WORT = re.compile(r'[A-Za-zÄÖÜäöüß]{4,}')


def abstand_eins(a, b):
    """True, wenn a und b sich um genau eine Ersetzung, Einfuegung oder Loeschung unterscheiden."""
    la, lb = len(a), len(b)
    if abs(la - lb) > 1:
        return False
    if la == lb:
        unterschiede = sum(1 for x, y in zip(a, b) if x != y)
        return unterschiede == 1
    kurz, lang = (a, b) if la < lb else (b, a)
    i = j = 0
    uebersprungen = False
    while i < len(kurz) and j < len(lang):
        if kurz[i] == lang[j]:
            i += 1; j += 1
        elif uebersprungen:
            return False
        else:
            uebersprungen = True; j += 1
    return True


async def sammle(pg):
    text = []
    gruppen = await pg.locator('#groups button').count()
    gesehen = set()
    for g in range(gruppen):
        await pg.locator('#groups button').nth(g).click()
        await pg.wait_for_timeout(250)
        n = await pg.locator('#tabs .tab').count()
        for i in range(n):
            name = (await pg.locator('#tabs .tab').nth(i).inner_text()).strip()
            if name in gesehen:
                continue
            gesehen.add(name)
            await pg.locator('#tabs .tab').nth(i).click()
            await pg.wait_for_timeout(260)
            text.append(await pg.inner_text('#tabpanel'))
    return text, gesehen


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page(viewport={'width': 1400, 'height': 1200})
        await pg.goto(URL)
        await pg.wait_for_timeout(1200)
        teile, reiter = await sammle(pg)
        # Stoffprofile dazu
        ids = await pg.evaluate("[...document.querySelectorAll('#picker .chip')].map(c => c.dataset.id || c.textContent.trim())")
        for sid in ids:
            await pg.goto(URL + '#stoff/' + sid)
            await pg.wait_for_timeout(260)
            teile.append(await pg.inner_text('body'))
        print('Reiter gelesen:', len(reiter), '| Stoffprofile:', len(ids))
        await b.close()

    worte = collections.Counter()
    for t in teile:
        worte.update(WORT.findall(t))
    einmal = [w for w, n in worte.items() if n == 1]
    haeufig = [w for w, n in worte.items() if n >= 4]
    print('Wortformen:', len(worte), '| einmalig:', len(einmal), '| haeufig (>=4):', len(haeufig))

    nach_laenge = collections.defaultdict(list)
    for h in haeufig:
        for L in (len(h) - 1, len(h), len(h) + 1):
            nach_laenge[L].append(h)

    def mitten_drin(a, b):
        """Liegt der Unterschied VOR den letzten zwei Buchstaben?
        Deutsche Beugung aendert das Wortende - echte Tippfehler sitzen meist weiter vorn."""
        i = 0
        while i < min(len(a), len(b)) and a[i] == b[i]:
            i += 1
        return i < min(len(a), len(b)) - 2

    treffer = []
    for w in einmal:
        wl = w.lower()
        for h in nach_laenge.get(len(w), ()):
            hl = h.lower()
            if hl == wl:
                continue
            if (len(w) >= 7 and w[0] == h[0] and not w.isupper() and not h.isupper()
                    and abstand_eins(wl, hl) and mitten_drin(wl, hl)):
                treffer.append((w, h, worte[h]))
                break
    print('\nVerdaechtige Paare:', len(treffer))
    for w, h, n in sorted(treffer):
        print('   %-26s  vs  %-26s (%dx)' % (w, h, n))

    # zusaetzlich: unmoegliche Buchstabenfolgen
    muster = re.compile(r'(.)\1\1|ßß|üü|öö|ää|[A-ZÄÖÜ]{2,}[a-zäöü]|qu?[^aeiouäöü]')
    odd = sorted({w for w in worte if muster.search(w) and worte[w] <= 2})
    print('\nAuffaellige Buchstabenfolgen:', odd or 'keine')
    sys.exit(0)

asyncio.run(main())
