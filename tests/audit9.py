
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
    errs=[]; pg.on('pageerror',lambda e:errs.append('ERR:'+str(e)))
    pg.on('console',lambda m:errs.append('C:'+m.text) if m.type=='error' else None)
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(900)
    # Tour
    tour=await pg.evaluate("!document.getElementById('tour').hidden")
    print('Tour erscheint:', tour)
    if tour:
      for i in range(8):
        if await pg.evaluate("document.getElementById('tour').hidden"): break
        await pg.click('#tourNext'); await pg.wait_for_timeout(260)
      print('Tour durchlaufbar, danach verborgen:', await pg.evaluate("document.getElementById('tour').hidden"))
    # Mein Profil
    await pg.click('#mySeg button[data-g="AA"]'); await pg.wait_for_timeout(300)
    print('Profiltext:', (await pg.inner_text('#myTxt'))[:60])
    fy=await pg.evaluate("!document.getElementById('forYou').hidden")
    print('Für-dich-Kasten sichtbar:', fy, '|', (await pg.inner_text('#forYou'))[:60] if fy else '')
    # Vergleich
    await pg.evaluate("""() => { const b=[...document.querySelectorAll('button')].find(x=>/vergleich/i.test(x.textContent)); if(b) b.click(); }""")
    await pg.wait_for_timeout(600)
    cmp=await pg.evaluate("""() => { const s=document.getElementById('vergleich');
      return {offen:!s.hidden, spalten:s.querySelectorAll('.cmp-col').length,
        canvas:[...s.querySelectorAll('canvas')].map(c=>c.width*c.height),
        fakten:[...s.querySelectorAll('.cmp-facts')].map(f=>f.textContent.length)}; }""")
    print('Vergleich:', cmp)
    if cmp['offen']:
      await pg.evaluate("const s=document.querySelector('#vergleich select'); s.selectedIndex=3; s.dispatchEvent(new Event('change',{bubbles:true}))")
      await pg.wait_for_timeout(500)
      print('Vergleich nach Wechsel:', await pg.evaluate("[...document.querySelectorAll('#vergleich .cmp-facts')].map(f=>f.textContent.length)"))
      await pg.click('#cmpClose'); await pg.wait_for_timeout(300)
    # Studien-Reiter: Filter und Suche
    await pg.evaluate("location.hash='#studien'"); await pg.wait_for_timeout(900)
    st=await pg.evaluate("""() => ({eintraege:document.querySelectorAll('#tabpanel .st-item').length,
      filter:document.querySelectorAll('#tabpanel .qchip, #tabpanel select').length})""")
    print('Studien-Reiter:', st)
    q=await pg.evaluate("!!document.querySelector('#tabpanel .st-q')")
    if q:
      await pg.fill('#tabpanel .st-q','Albträume'); await pg.wait_for_timeout(500)
      print('nach Filter „Albträume":', await pg.evaluate("document.querySelectorAll('#tabpanel .st-item').length"))
      await pg.fill('#tabpanel .st-q',''); await pg.wait_for_timeout(400)
    # Deep Link auf eine Karte
    await pg.evaluate("location.hash='#bilanz/b-tier'"); await pg.wait_for_timeout(800)
    print('Deep Link auf Karte:', await pg.evaluate("""() => { const e=document.getElementById('b-tier');
      return {gefunden:!!e, reiter:document.querySelector('#tabs [aria-selected=true]')?.textContent}; }"""))
    print('Fehler:', [e for e in errs if 'ERR_' not in e and 'Failed to fetch' not in e][:6] or 'keine')
    await b.close()
asyncio.run(main())
