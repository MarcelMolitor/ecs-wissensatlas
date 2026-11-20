# -*- coding: utf-8 -*-
"""Prueft die Karte s-mech im Reiter Schmerz & Krebs.

WARUM ES DIESEN TEST GIBT: Die Karte trug den Satz "Das System greift an drei
Ebenen in die Schmerzleitung ein" mit der Stufe "gut belegt" und OHNE EINEN
EINZIGEN BELEG; der eine Beleg der Karte deckte genau eine der drei Ebenen ab,
und zur Ebene Rueckenmark stand auf der ganzen Seite nichts. t/belege.py hat
das nicht gefunden, weil es prueft, ob eine Aussage MIT Stufe einen Beleg hat -
und der Beleg stand im Absatz davor. Dieser Test haelt den behobenen Zustand
fest:

 - jede der drei Ebenen hat eine eigene Belegstufe,
 - "gut belegt" kommt in dieser Karte NICHT mehr vor,
 - und die Verbotsliste haelt die beiden Ueberclaims draussen, die beim
   Schreiben naheliegen: dass die Doppelwirkung des Anandamids das Scheitern
   der FAAH-Hemmer ERKLAERT (sie ist an Rattenrueckenmark gemessen, die Studie
   war am Menschen, niemand hat beides verbunden), und dass die drei Ebenen am
   Menschen gezeigt seien.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

MUSS = ['Drei Ebenen', 'Dieselbe Gruppe hat anschließend gezeigt',
        'periaquäduktale Grau', 'jede mit ihrem eigenen Befund',
        'oberflächlichen Hinterhorn', 'Kappt man die eingehenden Fasern',
        'Schaltzellen des Rückenmarks', 'Reflexschwelle um über 50 Prozent',
        'spiegelbildliche, unwirksame Molekül', 'Injektionen daneben wirken nicht',
        'Glycin-Rezeptor', 'Spinalganglienzellen', 'TRPV1',
        'Niedrige Anandamid-Konzentrationen', 'Hohe Konzentrationen tun das Gegenteil',
        'Die Verbindung zwischen beidem hat niemand geprüft',
        'naheliegender Verdacht und kein Ergebnis',
        'Jeder Befund dieser Karte ist an Nagern erhoben']
VERBOTEN = ['gut belegt', 'Die am besten geprüfte der drei',
            'erklärt damit, warum', 'erklärt das Scheitern', 'damit ist geklärt',
            'am Menschen gezeigt', 'Alle vier Befunde', 'drei Ebenen am Menschen',
            'also kann man', 'für die Grundfunktion, erhoben im Tier']


async def zum_reiter(pg):
    await pg.click('#groups button[data-g="1"]')
    await pg.wait_for_timeout(250)
    await pg.click('#tabs button:has-text("Schmerz & Krebs")')
    await pg.wait_for_timeout(500)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1600)
        probleme = []

        await zum_reiter(pg)
        chip = pg.locator('.qchip[data-jump="s-mech"]')
        if await chip.count() != 1:
            probleme.append('Sprungknopf fehlt')
        else:
            await chip.click()
            await pg.wait_for_timeout(680)

        t = await pg.inner_text('#s-mech')
        print('  Kartentext:', len(t), 'Zeichen')
        for muss in MUSS:
            if muss not in t:
                probleme.append('fehlt: %s' % muss)
        for weg in VERBOTEN:
            if weg in t:
                probleme.append('Formulierung, die die Belege nicht tragen: %s' % weg)
        # Die drei Ueberschriften der Ebenen stehen in Grossbuchstaben (CSS),
        # deshalb hier ohne Ruecksicht auf Gross- und Kleinschreibung.
        tl = t.lower()
        for dt in ['an den nervenenden im gewebe', 'im rückenmark',
                   'im hirnstamm, über die absteigenden bahnen']:
            if dt not in tl:
                probleme.append('Ebenen-Ueberschrift fehlt: %s' % dt)

        # Drei Ebenen, drei eigene Stufen: jede <dd> der Liste muss eine tragen.
        stufen = await pg.evaluate("""() => {
            const dl = document.querySelector('#s-mech dl.kv');
            if (!dl) return 'KEINE LISTE';
            return [...dl.querySelectorAll('dd')].map(d => {
                const e = d.querySelector('.ev, [class*=ev]');
                return (d.textContent.match(/teils belegt|schwach belegt|Hypothese|nicht untersucht|am Menschen gescheitert/) || ['OHNE STUFE'])[0];
            });
        }""")
        print('  Stufen je Ebene:', stufen)
        if stufen == 'KEINE LISTE' or len(stufen) != 3:
            probleme.append('Ebenen-Liste hat nicht drei Eintraege: %s' % (stufen,))
        elif 'OHNE STUFE' in stufen:
            probleme.append('Eine Ebene ohne eigene Belegstufe: %s' % (stufen,))

        # Keine Dosisangabe ausserhalb des Wirkstoff-Labors.
        if re.search(r'\d+\s*mg\b', t):
            probleme.append('Dosisangabe in dieser Karte')

        n = await pg.locator('#s-mech button.xlink').count()
        print('  Querverweise:', n)
        if n != 4:
            probleme.append('%d Querverweise, erwartet 4' % n)
        for i in range(n):
            await zum_reiter(pg)
            kn = pg.locator('#s-mech button.xlink').nth(i)
            beschr = (await kn.inner_text()).strip()
            ziel = await kn.get_attribute('data-card')
            await kn.click()
            await pg.wait_for_timeout(820)
            if ziel:
                da = await pg.evaluate("""(id) => {
                    const c = document.getElementById(id);
                    return c ? c.getBoundingClientRect().height > 0 : 'FEHLT';
                }""", ziel)
                if da is not True:
                    probleme.append('Verweis "%s" -> %s tot (%s)' % (beschr, ziel, da))
                else:
                    print('   ok  "%s" -> %s' % (beschr[:34], ziel))

        for q in ['hinterhorn', 'absteigende', 'spinalganglien']:
            await pg.fill('#findQ', q)
            await pg.wait_for_timeout(520)
            n2 = await pg.eval_on_selector_all('#findRes [role=option]', 'e => e.length')
            print('  Suche "%s": %s Treffer' % (q, n2))
            if not n2:
                probleme.append('Suche findet "%s" nicht' % q)

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
