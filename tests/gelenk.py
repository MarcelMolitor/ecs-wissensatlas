
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
EXE = _CHROME
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width':1280,'height':1000})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('C:'+m.text) if m.type=='error' else None)
        await pg.goto('file://' + HIER + '/page.html#organ/gelenk')
        await pg.wait_for_timeout(2600)
        print('Fehler:', [e for e in errs if 'TUNNEL' not in e])
        info = await pg.evaluate("""() => {
          const g = document.querySelector('[data-organ-id="gelenk"], #org-gelenk, g.organ[data-id="gelenk"]');
          const svg = document.querySelector('#koerper svg') || document.querySelector('#koerper');
          const labels = [...document.querySelectorAll('#koerper text')].map(t => ({
            txt: t.textContent.trim(), x: +t.getAttribute('x'), y: +t.getAttribute('y')}));
          return {gefunden: !!g, anzahlText: labels.length,
                  gelenkLabel: labels.filter(l => /Gelenk/.test(l.txt)),
                  nachbarnRechts: labels.filter(l => l.x >= 295 && l.x <= 305).sort((a,b)=>a.y-b.y)};
        }""")
        print(info)
        await pg.screenshot(path=HIER + '/gelenk.png', full_page=False)
        # Ring fuer FAAH-Hemmer?
        await pg.goto('file://' + HIER + '/page.html')
        await pg.wait_for_timeout(1800)
        r = await pg.evaluate("""() => {
          const btn = document.querySelector('[data-pick="inh"], #picker [data-id="inh"], button[data-id="inh"]');
          if (btn) btn.click();
          return !!btn;
        }""")
        await pg.wait_for_timeout(900)
        ring = await pg.evaluate("""() => {
          const els = [...document.querySelectorAll('#koerper circle, #koerper [data-id]')];
          return els.filter(e => (e.getAttribute('data-id')||'') === 'gelenk').map(e => ({
            tag: e.tagName, r: e.getAttribute('r'), cls: e.getAttribute('class')||''}));
        }""")
        print('Stoff-Knopf inh geklickt:', r, '| Gelenk-Elemente:', ring)
        await b.close()
asyncio.run(main())
