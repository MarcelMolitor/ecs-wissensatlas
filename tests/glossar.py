# -*- coding: utf-8 -*-
"""Prueft die antippbaren Fachbegriffe (TERMS).

Vier Fragen:
 1. Werden die zehn neuen Begriffe irgendwo auf der Seite wirklich markiert?
    Ein Eintrag, der nie greift, ist toter Ballast.
 2. Oeffnet das Antippen eine Erklaerung mit passendem Titel?
 3. Bleiben die vorher vorhandenen Begriffe markiert? Die Agonisten-Familie
    (Partialagonist, Inverser Agonist, Antagonist) teilt Wortteile mit den
    Neuzugaengen - hier wuerde ein Musterkonflikt auffallen.
 4. Bleibt das Durchblaettern schnell? glossify prueft jedes Wort gegen jeden
    Textknoten, 23 -> 33 Woerter kosten Zeit.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys, time
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'

GRENZE_MS = 30000   # Durchblaettern aller Reiter, grosszuegig gegen Rauschen

NEU = ['TNF', 'Zytokin', 'Mikroglia', 'Prostaglandin', 'Vasopressin',
       'Hypothalamus', 'Dendrit', 'MAP-Kinase', 'JNK', 'Homöostase']
# Gruppen, nicht einzelne Woerter: Ein TERMS-Eintrag hat oft mehrere
# Schreibweisen, und die Seite benutzt davon nur eine. Die erste Fassung dieser
# Pruefung verlangte jede einzeln und meldete deshalb "Partialagonist" und
# "Antagonist" als verloren, obwohl der Text dort "Teilaktivator" und
# "Gegenspieler" schreibt - beides dieselben Eintraege, beide intakt.
ALT = [['Partialagonist', 'Teilaktivator'],
       ['Antagonist', 'Gegenspieler'],
       ['Inverser Agonist', 'inverser Agonist'],
       ['FAAH'], ['MAGL'], ['CB1'], ['CB2'], ['TRPV1'], ['GPR55'],
       ['Toleranz'], ['Placebo'], ['Synapse', 'synaptische']]
# Steht in TERMS, wird aber nirgends im Text getroffen - gemessen, nicht
# vermutet, und schon vor dieser Aenderung so. Die Erklaerung bleibt ueber den
# Glossar-Reiter erreichbar, deshalb hier nur festgehalten, nicht beanstandet.
TOT = ['Phytocannabinoid']


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 900})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE)
        await pg.wait_for_timeout(1800)
        probleme = []

        # --- Alle Reiter und Stoffe durchblaettern, markierte Woerter sammeln
        t0 = time.time()
        markiert = set()
        ng = await pg.evaluate('document.querySelectorAll("#groups button").length')
        reiter = 0
        for g in range(ng):
            await pg.click('#groups button[data-g="%d"]' % g)
            await pg.wait_for_timeout(240)
            for i in range(await pg.evaluate('document.querySelectorAll("#tabs button").length')):
                await pg.locator('#tabs button').nth(i).click()
                await pg.wait_for_timeout(220)
                reiter += 1
                for w in await pg.eval_on_selector_all('#tabpanel .term', 'e => e.map(x => x.textContent)'):
                    markiert.add(w.strip())
        dauer = int((time.time() - t0) * 1000)
        # Seit 08.11.2026 gibt es den Reiter "Herkunft"; die Zahl ist absichtlich
        # eine Untergrenze, damit ein neuer Reiter diesen Test nicht bricht,
        # ein VERLORENER aber schon.
        assert reiter >= 25, 'nur %d Reiter durchblaettert, erwartet 25+' % reiter
        for sid in await pg.eval_on_selector_all('.chip', 'e => e.map(x => x.dataset.id)'):
            await pg.click('.chip[data-id="%s"]' % sid)
            await pg.wait_for_timeout(150)
            for w in await pg.eval_on_selector_all(
                    '#subWhat .term, #status .term, #steps .term', 'e => e.map(x => x.textContent)'):
                markiert.add(w.strip())

        tief = ' '.join(markiert).lower()
        for name in NEU:
            if name.lower()[:7] not in tief:
                probleme.append('NEU, aber nie markiert: %s' % name)
        for gruppe in ALT:
            if not any(n.lower()[:7] in tief for n in gruppe):
                probleme.append('VORHER DA, jetzt kein Wort der Gruppe markiert: %s' % ' / '.join(gruppe))
        for name in TOT:
            if name.lower()[:9] in tief:
                print('  Hinweis: "%s" wird jetzt doch markiert - TOT-Liste anpassen' % name)

        # --- Antippen: oeffnet sich eine Erklaerung mit Titel?
        await pg.click('#groups button[data-g="0"]')
        await pg.wait_for_timeout(260)
        geprueft = 0
        for i in range(await pg.evaluate('document.querySelectorAll("#tabs button").length')):
            await pg.locator('#tabs button').nth(i).click()
            await pg.wait_for_timeout(220)
            n = await pg.locator('#tabpanel .term').count()
            for j in range(min(n, 5)):
                kn = pg.locator('#tabpanel .term').nth(j)
                wort = (await kn.inner_text()).strip()
                await kn.click()
                await pg.wait_for_timeout(120)
                tip = await pg.evaluate("""() => {
                    const box = document.getElementById('tip');
                    return {offen: !box.hidden,
                            titel: document.getElementById('tipT').textContent,
                            text: document.getElementById('tipD').textContent};
                }""")
                if not tip['offen']:
                    probleme.append('Erklaerung zu "%s" oeffnet nicht' % wort)
                elif len(tip['text']) < 25 or not tip['titel']:
                    probleme.append('Erklaerung zu "%s" unvollstaendig: %s' % (wort, tip))
                geprueft += 1
                await pg.keyboard.press('Escape')
                await pg.wait_for_timeout(50)

        print('verschiedene markierte Begriffe:', len(markiert))
        print('angetippt und geprueft:', geprueft)
        print('Durchblaettern aller %d Reiter:' % reiter, dauer, 'ms (Grenze %d)' % GRENZE_MS)
        if dauer > GRENZE_MS:
            probleme.append('zu langsam: %d ms' % dauer)
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler:
            sys.exit(1)


asyncio.run(main())
