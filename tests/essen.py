# -*- coding: utf-8 -*-
"""Dauertest fuer den Reiter 'Essen und Trinken'.

WARUM ER SO GEBAUT IST: Gefragt war ein Reiter mit Lebensmitteln, die auf das
System wirken. Gezaehlt ergab: Die Seite hat dazu schon sehr viel, aber in FUENF
Reitern und sauber getrennt nach zwei Fragen - Einflussfaktoren (was das eigene
System verschiebt) und Medizin (was als Produkt verkauft wird). Diese Trennung
ist richtig; eine Nacherzaehlung waere Doppelung gewesen. Gefehlt hat der
Einstieg ueber das LEBENSMITTEL. Der Reiter ist deshalb eine Uebersicht mit
Verweisen, kein zweiter Text.

DER BEFUND, den der Reiter ausspricht und der dastehen MUSS: Die Dinge, die das
System messbar verschieben - Kaffee, Alkohol, Ausdauersport, das
Fettsaeureverhaeltnis, ballaststoffreiche Kost -, werden nicht dafuer verkauft.
Und die sieben Produkte, die dafuer verkauft werden, haben keine Messung am
Menschen, die eine Wirkung ueber dieses System zeigt. Bei Hanfsamenoel wurde
gemessen - es war das PLACEBO.

NEUER BELEG: [[25958314]] Ramsden u. a., J Pain 2015. 55 Menschen, gezielte
Ernaehrungsumstellung: Omega-3-Abkoemmlinge +65 % und +99 %, 2-AG -25 %. Damit
wird die schwaechste Zeile der Seite ('Omega-3 zu Omega-6 - vor allem
Tierdaten', Stufe s) zu einer Messung am Menschen (Stufe m). Der Test haelt
fest, dass sie nicht zurueckfaellt.

VIER FEHLER BEIM BAU, alle beim Lesen des gerenderten Texts gefunden:
 1. Der Untertitel sagte 'Verschiebung im BLUT' - bei Ballaststoffen wurde im
    STUHL gemessen und bei Alkohol an den REZEPTOREN im Gehirn. Jetzt 'am
    Menschen'.
 2. Die Alkohol-Zeile war die einzige ohne Beleg. Jetzt mit dem PET-Befund
    [[24553924]].
 3. Die Echinacea-Zeile nannte nur die CB2-Bindung - die Seite traegt aber
    einen GEGENBEFUND: Ein zweiter Zellversuch fand den Effekt NICHT ueber CB2
    [[21092239]]. Eine Zeile, die den Gegenbefund derselben Seite verschweigt,
    ist schlechter als keine.
 4. Der Abschlusssatz widersprach sich in zwei Zeilen: 'In keiner dieser Zeilen
    steht eine Messung am Menschen' - und direkt danach 'Bei Hanfsamenoel ist
    am Menschen gemessen worden'.

KEINE MENGEN- UND DOSISANGABEN: Lebensmittel sind erhaeltlich, und dieser
Reiter beschreibt Messungen, keine Ernaehrungsplaene. Der Test prueft das.
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

# Die Zahlwoerter im Text und die Zeilen, die sie behaupten. An diesem Tag sind
# vier handgezaehlte Zahlen falsch gewesen - deshalb wird hier nachgezaehlt.
SOLL = {'e-gemessen': (5, 'Fünf Dinge'), 'e-verkauft': (7, 'Sieben Produkte')}
MUSS = [
    'Omega-3-Abkömmlinge +65 % und +99 %',
    'keine gezeigte Ursache',          # die Korrelations-Einschraenkung
    'Kopfschmerzpatienten, keine Gesunden',
    'Es diente in einer Studie als Placebo',
    'nicht über CB2',                  # der Echinacea-Gegenbefund
    'Keine Studie am Menschen',
    'Rund 16 % weniger verfügbare CB1-Rezeptoren',
    'Was messbar wirkt, wird nicht dafür verkauft',
]
VERBOTEN = [
    'Verschiebung im Blut belegt',     # stimmte fuer zwei Zeilen nicht
    'In keiner dieser sieben Zeilen steht eine Messung am Menschen, die eine Wirkung über dieses System zeigt. Bei Hanfsamenöl ist',
    'Menschen, gut belegt',            # die unbelegte Alkohol-Zelle
    # Keine Empfehlungen:
    'sollten Sie essen', 'empfehlenswert', 'täglich einnehmen',
]
MENGEN = [' mg', 'Milligramm', 'Esslöffel', 'Teelöffel', 'Portionen täglich']


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    if ("['25958314'," not in S) or ('[[25958314]]' not in S):
        probleme.append('Beleg 25958314 fehlt oder wird nicht benutzt')
    if "'einfluss', 'essen'" not in S:
        probleme.append('Reiter nicht in der Gruppe Praxis hinter Einflussfaktoren')
    if 'Vor allem Tierdaten.' in S and 'Omega-3 zu Omega-6' in S:
        i = S.find('Omega-3 zu Omega-6')
        if 'Vor allem Tierdaten' in S[i:i + 400]:
            probleme.append('die Omega-Zeile ist auf "Vor allem Tierdaten" zurueckgefallen')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1200})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)
        await pg.click('#groups button[data-g="1"]')
        await pg.wait_for_timeout(320)
        kn = pg.locator('#tabs button:has-text("Essen und Trinken")')
        if await kn.count() != 1:
            print('Probleme: Reiter "Essen und Trinken" nicht in der Gruppe Praxis')
            await b.close(); sys.exit(1)
        await kn.click()
        await pg.wait_for_timeout(900)

        ganz = await pg.inner_text('#tabpanel')
        if '${' in ganz:
            probleme.append('unaufgeloeste Vorlage im Reiter')
        for m in MUSS:
            if m not in ganz:
                probleme.append('Kernaussage fehlt: %s' % m)
        for v in VERBOTEN:
            if v in ganz:
                probleme.append('zurueckgebaute oder unerwuenschte Fassung: %s' % v[:60])
        for d in MENGEN:
            if d in ganz:
                probleme.append('Mengen- oder Dosisangabe im Reiter: %s' % d.strip())
        print('  ok  Kernaussagen da, keine alte Fassung, keine Mengenangabe')

        # Die Zahlwoerter gegen die wirklichen Zeilen pruefen.
        for cid, (n, wort) in SOLL.items():
            if await pg.locator('#' + cid).count() != 1:
                probleme.append('Karte %s fehlt' % cid); continue
            zeilen = await pg.locator('#%s tbody tr' % cid).count()
            if zeilen != n:
                probleme.append('%s hat %d Zeilen, der Text sagt %s' % (cid, zeilen, wort))
            t = await pg.inner_text('#' + cid)
            if wort not in t:
                probleme.append('%s: das Zahlwort "%s" steht nicht im Text' % (cid, wort))
        print('  ok  Zahlwoerter stimmen mit den Tabellenzeilen')

        # Jede Zeile der Menschen-Tabelle muss in der Spalte "An wem" Menschen
        # nennen; keine Zeile der Verkaufs-Tabelle darf das tun.
        mensch = await pg.eval_on_selector_all(
            '#e-gemessen tbody tr', "e => e.map(r => r.cells[3].textContent)")
        for z in mensch:
            if not re.search(r'Mensch|Gewohnheitstrinker|\d+\s*Menschen|Studien am Menschen', z):
                probleme.append('Zeile in e-gemessen nennt keine Messung am Menschen: %s' % z[:60])
        verk = await pg.eval_on_selector_all(
            '#e-verkauft tbody tr', "e => e.map(r => r.cells[3].textContent)")
        ohne = [z for z in verk if re.search(r'Zellversuch|Tierstudien|Tierversuche|'
                                             r'Keine Studie am Menschen|Nachweis im Lebensmittel', z)]
        if len(ohne) < 5:
            probleme.append('nur %d der %d Verkaufs-Zeilen weisen sich als Zell-, Tier- oder'
                            ' fehlende Messung aus' % (len(ohne), len(verk)))
        print('  ok  beide Tabellen weisen ihre Beweisart in jeder Zeile aus')

        # Die Verweise muessen funktionieren - sonst ist der Reiter eine
        # Uebersicht, die nirgends hinfuehrt, und genau das ist sein Zweck.
        for ziel, card in [('anwendung', 'm-hanfoel'), ('einfluss', None)]:
            sel = ('.xlink[data-tab="%s"][data-card="%s"]' % (ziel, card)) if card \
                  else ('.xlink[data-tab="%s"]' % ziel)
            if await pg.locator('#tabpanel ' + sel).count() < 1:
                probleme.append('Verweis fehlt: %s' % sel)
        kn2 = pg.locator('#tabpanel .xlink[data-tab="anwendung"][data-card="m-hanfoel"]').first
        await kn2.click()
        await pg.wait_for_timeout(900)
        if not await pg.evaluate(
                "()=>{const c=document.getElementById('m-hanfoel');"
                " return c ? c.getBoundingClientRect().height>0 : false;}"):
            probleme.append('der Verweis auf m-hanfoel fuehrt ins Leere')
        else:
            print('  ok  Verweise fuehren zu den Karten')

        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
