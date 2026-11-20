
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, json
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    pg=await b.new_page(viewport={'width':1280,'height':900})
    errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(800)
    res=await pg.evaluate("""() => {
      const out={tabs:[],xrefs:[],jumps:[],cites:0,unresolved:[],dupIds:[],headings:[]};
      const ids=[...document.querySelectorAll('#tabs button')].length;
      const groups=[...document.querySelectorAll('#groups button')];
      const tabIds=[];
      // alle Reiter einmal rendern und einsammeln
      const all={};
      for (let g=0; g<groups.length; g++){
        groups[g].click();
        const tb=[...document.querySelectorAll('#tabs button')];
        for (const t of tb){ t.click(); const id=t.dataset.k||t.id||t.textContent.trim();
          tabIds.push(t.textContent.trim());
          const panel=document.getElementById('tabpanel');
          all[t.textContent.trim()]={
            html:panel.innerHTML,
            xr:[...panel.querySelectorAll('[data-tab]')].map(b=>b.dataset.tab+(b.dataset.card?'/'+b.dataset.card:'')),
            jm:[...panel.querySelectorAll('[data-jump]')].map(b=>b.dataset.jump),
            cardIds:[...panel.querySelectorAll('article.card')].map(c=>c.id),
            cites:panel.querySelectorAll('sup.cite a').length,
            marker:(panel.innerHTML.match(/\\[\\[\\d+\\]\\]/g)||[]),
            hs:[...panel.querySelectorAll('h2,h3,h4')].map(h=>h.tagName)
          };
        }
      }
      out.tabs=tabIds; out.all=all;
      return out;
    }""")
    allt=res['all']
    print('Reiter:', len(res['tabs']))
    # Querverweise auflösen
    knowIds = await pg.evaluate("[...document.querySelectorAll('#groups button')].map((g,i)=>{g.click();return [...document.querySelectorAll('#tabs button')].map(t=>t.dataset.k)}).flat()")
    print('Reiter-IDs:', knowIds)
    badx=[]; badj=[]; marker=[]; cards={}
    for name,d in allt.items():
      cards[name]=d['cardIds']
      if d['marker']: marker.append((name,d['marker']))
      for x in d['xr']:
        tab,_,card=x.partition('/')
        if tab not in knowIds: badx.append((name,x,'Reiter unbekannt'))
      for j in d['jm']:
        if j not in d['cardIds']: badj.append((name,j))
    print('\nUnaufgelöste Belegmarker:', marker if marker else 'keine')
    print('Querverweise auf unbekannte Reiter:', badx if badx else 'keine')
    print('Sprungziele ohne Karte:', badj if badj else 'keine')
    # Karten-Ziele der Querverweise prüfen
    badcard=[]
    for name,d in allt.items():
      for x in d['xr']:
        tab,_,card=x.partition('/')
        if card and tab in knowIds:
          target=[k for k in allt if True]
          # Kartenliste des Zielreiters finden
          for n2,d2 in allt.items():
            pass
    # direkt im Browser prüfen: jeden data-card Verweis anklicken
    print('\nFehler:', errs)
    await b.close()
asyncio.run(main())
