
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, re, difflib
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    pg=await b.new_page(viewport={'width':1280,'height':900})
    await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(700)
    texts=await pg.evaluate("""() => {
      const groups=[...document.querySelectorAll('#groups button')], o={};
      for (let g=0; g<groups.length; g++){ groups[g].click();
        for (const t of [...document.querySelectorAll('#tabs button')]){ t.click();
          o[t.textContent.trim()]=document.getElementById('tabpanel').innerText; } }
      return o;
    }""")
    def sents(t):
      return [s.strip() for s in re.split(r'(?<=[.!?])\s+', t) if len(s.strip())>70]
    S={k:sents(v) for k,v in texts.items()}
    new='Post-COVID & Fatigue'
    print('Satzlängen neuer Reiter:', len(S[new]))
    hits=[]
    for other,os_ in S.items():
      if other==new: continue
      for a in S[new]:
        for c in os_:
          r=difflib.SequenceMatcher(None,a,c).ratio()
          if r>0.72: hits.append((round(r,2),other,a[:95],c[:95]))
    hits.sort(reverse=True)
    print('\nÄhnliche Sätze zu anderen Reitern:', len(hits))
    for h in hits[:6]:
      print(f'  {h[0]} ggü. [{h[1]}]')
      print('    neu :', h[2])
      print('    alt :', h[3])
    await b.close()
asyncio.run(main())
