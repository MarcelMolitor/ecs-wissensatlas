
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    pg=await b.new_page(viewport={'width':1280,'height':900})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(800)
    # Kernaussage oben
    nb=await pg.evaluate("""() => { const n=document.querySelector('.notice'); return n ? {txt:n.innerText.slice(0,90), hasLink:!!n.querySelector('[data-tab=bilanz]')} : null; }""")
    print('Kernaussage oben:', nb)
    # Knopf in der Navigation
    print('Navi-Knopf:', await pg.evaluate("!!document.querySelector('.topnav [data-go=\"tab:bilanz\"]')"))
    # ueber die Kernaussage in den Reiter springen
    await pg.click('.notice [data-tab=bilanz]'); await pg.wait_for_timeout(800)
    print('aktiver Reiter:', await pg.evaluate("document.querySelector('#tabs [aria-selected=true]')?.textContent"))
    cards=await pg.evaluate("[...document.querySelectorAll('#tabpanel article.card')].map(c=>c.id)")
    print('Karten:', cards)
    print('Zitate:', await pg.evaluate("document.querySelectorAll('#tabpanel sup.cite a').length"))
    print('Tabellenzeilen:', await pg.evaluate("document.querySelectorAll('#tabpanel table tbody tr').length"))
    # dynamische Zahlen
    import re
    t=await pg.inner_text('#tabpanel')
    print('Zahlen im Text:', re.findall(r'\d+ (?:Studien|Belege|randomisierte Studien|zusammenfassende Auswertungen)', t)[:6])
    # Sprungmarken
    chips=await pg.evaluate("[...document.querySelectorAll('#tabpanel [data-jump]')].map(b=>b.dataset.jump)")
    miss=[c for c in chips if not await pg.evaluate(f'!!document.getElementById(\"{c}\")')]
    print('Sprungziele fehlend:', miss)
    # Navi-Knopf testen
    await pg.evaluate("location.hash='#botenstoffe'"); await pg.wait_for_timeout(500)
    await pg.click('.topnav [data-go="tab:bilanz"]'); await pg.wait_for_timeout(800)
    print('nach Navi-Klick:', await pg.evaluate("document.querySelector('#tabs [aria-selected=true]')?.textContent"))
    print('Fehler:', errs)
    await b.close()
asyncio.run(main())
