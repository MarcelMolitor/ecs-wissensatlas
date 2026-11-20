
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
    pg.on('console',lambda m:errs.append('C:'+m.text) if m.type=='error' else None)
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(800)
    r=await pg.evaluate("""() => {
      const out={marker:[],dupCard:[],noName:[],imgNoAlt:[],ariaBad:[],emptyCite:0,tabs:0};
      const groups=[...document.querySelectorAll('#groups button')];
      const seenCards={};
      for (let g=0; g<groups.length; g++){
        groups[g].click();
        for (const t of [...document.querySelectorAll('#tabs button')]){
          t.click(); out.tabs++;
          const panel=document.getElementById('tabpanel'), name=t.textContent.trim();
          // unaufgeloeste Marker
          const m=panel.innerHTML.match(/\\[\\[\\d+\\]\\]/g);
          if (m) out.marker.push([name,m]);
          // doppelte Karten-IDs
          for (const c of panel.querySelectorAll('[id]')){
            if (seenCards[c.id] && seenCards[c.id]!==name) out.dupCard.push([c.id,seenCards[c.id],name]);
            seenCards[c.id]=name;
          }
          // Knoepfe ohne zugaenglichen Namen
          for (const btn of panel.querySelectorAll('button')){
            const n=(btn.textContent||'').trim() || btn.getAttribute('aria-label') || btn.title;
            if (!n) out.noName.push([name, btn.outerHTML.slice(0,60)]);
          }
          // Bilder ohne Alternativtext
          for (const img of panel.querySelectorAll('img')) if (!img.alt) out.imgNoAlt.push([name,img.src.slice(0,40)]);
          // aria-selected: genau einer aktiv
          const sel=document.querySelectorAll('#tabs [aria-selected=true]').length;
          if (sel!==1) out.ariaBad.push([name,sel]);
        }
      }
      return out;
    }""")
    print('Reiter geprüft:', r['tabs'])
    print('Unaufgelöste Belegmarker:', r['marker'] or 'keine')
    print('IDs in mehreren Reitern:', r['dupCard'][:5] or 'keine')
    print('Knöpfe ohne Namen:', r['noName'][:5] or 'keine')
    print('Bilder ohne Alternativtext:', r['imgNoAlt'][:5] or 'keine')
    print('aria-selected fehlerhaft:', r['ariaBad'][:5] or 'keine')
    print('Fehler/Konsole:', [e for e in errs if 'ERR_' not in e and 'Failed to fetch' not in e][:5] or 'keine')
    await b.close()
asyncio.run(main())
