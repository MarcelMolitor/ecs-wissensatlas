
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
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(700)
    bad=await pg.evaluate("""() => {
      const groups=[...document.querySelectorAll('#groups button')];
      const problems=[];
      for (let g=0; g<groups.length; g++){
        groups[g].click();
        for (const t of [...document.querySelectorAll('#tabs button')]){
          t.click();
          const panel=document.getElementById('tabpanel'), tab=t.textContent.trim();
          for (const btn of panel.querySelectorAll('[data-jump]')){
            const el=document.getElementById(btn.dataset.jump);
            if (!el) problems.push([tab,'jump',btn.dataset.jump,'Ziel fehlt']);
            else if (!panel.contains(el)) problems.push([tab,'jump',btn.dataset.jump,'Ziel ausserhalb des Reiters']);
          }
        }
      }
      return problems;
    }""")
    print('Echte Sprungprobleme:', bad if bad else 'keine')
    # Querverweise mit data-card wirklich anklicken
    out=await pg.evaluate("""async () => {
      const sleep=ms=>new Promise(r=>setTimeout(r,ms));
      const groups=[...document.querySelectorAll('#groups button')];
      const refs=[];
      for (let g=0; g<groups.length; g++){
        groups[g].click();
        for (const t of [...document.querySelectorAll('#tabs button')]){
          t.click(); const from=t.textContent.trim();
          for (const b of document.getElementById('tabpanel').querySelectorAll('[data-tab][data-card]'))
            refs.push([from,b.dataset.tab,b.dataset.card]);
        }
      }
      const fail=[];
      for (const [from,tab,card] of refs){
        location.hash='#'+tab+'/'+card; await sleep(220);
        const el=document.getElementById(card);
        const sel=document.querySelector('#tabs [aria-selected=true]');
        if (!el) fail.push([from,tab,card,'Karte nicht gefunden']);
      }
      return {count:refs.length, fail};
    }""")
    print(f"Querverweise mit Kartenziel: {out['count']} geprüft, Fehlschläge:", out['fail'] if out['fail'] else 'keine')

    # Seit 31.10.: Karten koennen auch auf ein Organ oder eine Hirnregion verweisen.
    # Ein data-organ, das kein Organ ist, waere ein toter Knopf - also hier dauerhaft pruefen.
    ziele = await pg.evaluate("""async () => {
      const gefunden=[]; const groups=[...document.querySelectorAll('#groups button')];
      for (let g=0; g<groups.length; g++){
        groups[g].click();
        for (const t of [...document.querySelectorAll('#tabs button')]){
          t.click();
          for (const b of document.getElementById('tabpanel').querySelectorAll('.xlink[data-organ], .xlink[data-region]'))
            gefunden.push([b.dataset.organ ? 'organ' : 'region', b.dataset.organ || b.dataset.region]);
        }
      }
      const tot=[];
      for (const [art,id] of gefunden){
        const ok = art==='organ' ? !!document.querySelector('#or-'+id) : !!document.querySelector('#rg-'+id);
        if (!ok) tot.push([art,id]);
      }
      return {n:gefunden.length, tot};
    }""")
    print(f"Verweise auf Organ/Hirnregion: {ziele['n']} geprüft, tote:", ziele['tot'] if ziele['tot'] else 'keine')
    print('Fehler:', errs)
    await b.close()
asyncio.run(main())
