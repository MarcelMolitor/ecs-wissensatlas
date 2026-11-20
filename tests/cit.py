
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re
from playwright.async_api import async_playwright
SRC=open(HIER + '/page.html',encoding='utf8').read()
# alle im neuen Reiter verwendeten PMIDs
start=SRC.index("{id:'fatigue'"); end=SRC.index("{id:'nachbarn'")
used=sorted(set(re.findall(r'\[\[(\d+)\]\]', SRC[start:end])))
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    pg=await b.new_page(viewport={'width':1280,'height':900})
    await pg.goto('file://' + HIER + '/page.html#fatigue'); await pg.wait_for_timeout(900)
    print('Zitatanker:', await pg.evaluate('document.querySelectorAll("#tabpanel sup.cite a").length'))
    ids=await pg.evaluate('[...document.querySelectorAll("#tabpanel sup.cite a")].map(a=>a.dataset.pm)')
    print('verwendete PMIDs im Quelltext:', len(used))
    unresolved=[u for u in used if u not in set(ids)]
    print('nicht aufgelöst (verschwunden):', unresolved)
    # Nummern aufsteigend und korrekt?
    nums=await pg.evaluate('[...document.querySelectorAll("#tabpanel sup.cite a")].map(a=>a.textContent)')
    print('Beispiel-Nummern:', nums[:8], '...', nums[-4:])
    # Klick auf ein Zitat landet im Studienreiter beim richtigen Eintrag
    await pg.evaluate('document.querySelector("#tabpanel sup.cite a[data-pm=\'41513981\']").click()')
    await pg.wait_for_timeout(900)
    print('nach Klick Reiter:', await pg.evaluate('document.querySelector("#tabs [aria-selected=true]")?.textContent'))
    print('Ziel sichtbar:', await pg.evaluate('!!document.getElementById("key-41513981")'))
    await b.close()
asyncio.run(main())
