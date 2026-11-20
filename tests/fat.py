
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    errs=[]
    pg=await b.new_page(viewport={'width':1280,'height':900})
    pg.on('pageerror',lambda e:errs.append('ERR:'+str(e)))
    # Deep link direkt auf den neuen Reiter
    await pg.goto('file://' + HIER + '/page.html#fatigue'); await pg.wait_for_timeout(900)
    print('aktiver Reiter:', await pg.evaluate('document.querySelector("#tabs [aria-selected=true]")?.textContent'))
    cards=await pg.evaluate('[...document.querySelectorAll("#tabpanel article.card")].map(c=>c.id+"|"+(c.querySelector("h3")?.textContent||"").slice(0,42))')
    print('Karten:'); [print('  ',c) for c in cards]
    print('Zitate:', await pg.evaluate('document.querySelectorAll("#tabpanel a.cite").length'))
    print('Belegstaerke-Marker:', await pg.evaluate('document.querySelectorAll("#tabpanel .ev").length'))
    print('Tabellenzeilen:', await pg.evaluate('document.querySelectorAll("#tabpanel table tbody tr").length'))
    print('Faktoren:', await pg.evaluate('document.querySelectorAll("#tabpanel .factor").length'))
    # Sprungmarken testen
    chips=await pg.evaluate('[...document.querySelectorAll("#tabpanel [data-jump]")].map(b=>b.dataset.jump)')
    miss=[c for c in chips if not await pg.evaluate(f'!!document.getElementById("{c}")')]
    print('Sprungziele:', chips, 'fehlend:', miss)
    # Querverweise auf andere Reiter
    xl=await pg.evaluate('[...document.querySelectorAll("#tabpanel [data-tab]")].map(b=>b.dataset.tab)')
    known=await pg.evaluate('[...document.querySelectorAll("#tabs button")].length')
    print('Querverweise:', sorted(set(xl)))
    # Neue Belege im Studien-Reiter
    await pg.evaluate('location.hash="#studien"'); await pg.wait_for_timeout(900)
    txt=await pg.inner_text('#tabpanel')
    for pm in ['Versace','Abdullah','Smith & Wagner']:
      print(f'  {pm} im Studienreiter:', pm in txt)
    import re
    m=re.search(r'(\d+)\s+Schlüsselstudien|(\d+)\s+Studien', txt)
    print('  Zählung:', m.group(0) if m else 'n/a')
    print('Fehler:', errs)
    await b.close()
asyncio.run(main())
