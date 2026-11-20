# -*- coding: utf-8 -*-
"""Findet Aussagen, die eine Belegstufe tragen, aber keinen Beleg.
Dieser Fehlertyp kam am 25.10. dreimal vor (COX-2-Zeile, Uebelkeit-Zeile, Beta-Caryophyllen).
Geprueft wird die gerenderte Seite, nicht der Quelltext - so faellt auch auf,
wenn ein cite() fehlt und der Marker gar nicht erst zu einer Nummer wird.
Stufen, die ausdruecklich das Fehlen von Belegen bedeuten, werden nicht beanstandet."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, json
from playwright.async_api import async_playwright

VERLANGT_BELEG = ['gut belegt', 'teils belegt', 'schwach belegt', 'am Menschen gescheitert']

JS = """
(verlangt) => {
  const out = [];
  document.querySelectorAll('.ev').forEach(e => {
    const stufe = e.textContent.trim();
    if (!verlangt.includes(stufe)) return;
    // Block = naechste Zeile/Karte/Definition, in der die Stufe steht
    // Die Uebersichtstabelle traegt bewusst keine Nummern - die stehen beim Stoff selbst.
    if (e.closest('#ovBody')) return;
    // Karten, die ausdruecklich eine belegte Kette zusammenfassen, statt etwas Neues zu behaupten.
    if (e.closest('[data-summary]')) return;
    const block = e.closest('tr, .factor, .stage, .st-item') || e.closest('article, dl, li') || e.parentElement;
    if (!block) return;
    if (block.querySelector('sup.cite a')) return;
    // Schlussfolgerungs-Absaetze erben die Belege ihrer Karte
    const karte = block.closest('article, .factor, .stage');
    if (karte && karte.querySelector('sup.cite a')) return;
    const txt = (block.innerText || '').replace(/\\s+/g, ' ').trim();
    out.push({stufe, text: txt.slice(0, 150)});
  });
  return out;
}
"""

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        pg = await b.new_page(viewport={'width': 1400, 'height': 1200})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(1800)

        befunde = []
        # 1) Alle Wissens-Reiter durchgehen
        gn = await pg.locator('#groups button').count()
        for gi in range(gn):
            await pg.locator('#groups button').nth(gi).click(); await pg.wait_for_timeout(250)
            tn = await pg.locator('#tabs .tab').count()
            for ti in range(tn):
                name = await pg.locator('#tabs .tab').nth(ti).inner_text()
                await pg.locator('#tabs .tab').nth(ti).click(); await pg.wait_for_timeout(320)
                for f in await pg.evaluate(JS, VERLANGT_BELEG):
                    befunde.append(('Reiter ' + name, f['stufe'], f['text']))

        # 2) Jeden Stoff mit jedem seiner Organe
        ids = await pg.evaluate("[...document.querySelectorAll('#picker .chip')].map(c => c.dataset.id || c.textContent.trim())")
        for sid in ids:
            await pg.goto('file://' + HIER + '/page.html#stoff/' + sid); await pg.wait_for_timeout(700)
            name = (await pg.inner_text('#subName')).replace('#', '').strip()
            organe = await pg.evaluate("[...document.querySelectorAll('#bodySvg g.organ')].map(g => g.dataset.k)")
            for k in organe:
                await pg.eval_on_selector('#or-' + k, "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
                await pg.wait_for_timeout(90)
                for f in await pg.evaluate(JS, VERLANGT_BELEG):
                    befunde.append(('Stoff ' + name + ' / Organ ' + k, f['stufe'], f['text']))

        # Doppelte zusammenfassen
        gesehen = {}
        for ort, stufe, txt in befunde:
            gesehen.setdefault((stufe, txt), []).append(ort)
        print('Aussagen mit Belegstufe, aber ohne Beleg:', len(gesehen))
        for (stufe, txt), orte in sorted(gesehen.items()):
            print('  [%s] %s' % (stufe, txt))
            print('        gefunden in: %s%s' % (', '.join(orte[:3]), ' …' if len(orte) > 3 else ''))
        print('Fehler:', errs)
        await b.close()

asyncio.run(main())
