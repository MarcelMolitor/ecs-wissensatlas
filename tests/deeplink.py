
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
HASHES=['','#labor','#labor/lab-dosis','#lebensphasen','#bilanz','#bilanz/b-tier','#studien','#klinisch','#entzuendung/e-ablauf','#fatigue','#anwendung/m-erg','#gene','#wikipedia','#weg','#geschichte','#mythen','#covid','#nachbarn/n-tnf','#botenstoffe','#glossar','#einfluss','#wechsel','#rezeptoren','#enzyme']
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    bad=[]
    for h in HASHES:
      pg=await b.new_page(viewport={'width':1280,'height':900})
      errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
      await pg.goto('file://' + HIER + '/page.html'+h); await pg.wait_for_timeout(1100)
      r=await pg.evaluate("""() => ({tab:document.querySelector('#tabs [aria-selected=true]')?.textContent,
        len:document.getElementById('tabpanel').innerText.length})""")
      ok = r['len'] > 200 and not errs
      if not ok: bad.append((h, r, errs[:1]))
      print(f"{h or '(ohne)':24s} {r['tab'][:24] if r['tab'] else '?':26s} {r['len']:>6} Zeichen  {'OK' if ok else 'FEHLER ' + str(errs[:1])}")
      await pg.close()
    print('\nProbleme:', bad or 'keine')
    await b.close()
asyncio.run(main())
