
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio
from playwright.async_api import async_playwright
JS = r"""
() => {
  const parse = s => {
    if (!s) return null;
    let m = s.match(/rgba?\(([^)]+)\)/);
    if (m){ const p=m[1].split(/[\s,\/]+/).filter(Boolean).map(Number); return [p[0],p[1],p[2], p.length>3?p[3]:1]; }
    m = s.match(/color\(srgb\s+([^)]+)\)/);
    if (m){ const p=m[1].split(/[\s\/]+/).filter(Boolean).map(Number);
            return [p[0]*255,p[1]*255,p[2]*255, p.length>3?p[3]:1]; }
    return null;
  };
  const lin = c => { c/=255; return c<=0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); };
  const L = ([r,g,b]) => 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b);
  const ratio = (a,b) => { const l1=L(a), l2=L(b); return (Math.max(l1,l2)+0.05)/(Math.min(l1,l2)+0.05); };
  const bgOf = el => {
    let n = el;
    while (n && n !== document.documentElement){
      const c = parse(getComputedStyle(n).backgroundColor);
      if (c && c[3] > 0.95) return c;
      n = n.parentElement;
    }
    return parse(getComputedStyle(document.body).backgroundColor) || [255,255,255,1];
  };
  const out = [];
  const panel = document.getElementById('tabpanel');
  for (const el of panel.querySelectorAll('*')){
    const txt = [...el.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.trim()).join('');
    if (!txt) continue;
    const cs = getComputedStyle(el);
    if (cs.visibility==='hidden' || cs.display==='none') continue;
    const fg = parse(cs.color); if (!fg) continue;
    const bg = bgOf(el);
    const px = parseFloat(cs.fontSize), bold = parseInt(cs.fontWeight||'400',10) >= 700;
    const large = px >= 24 || (px >= 18.66 && bold);
    const need = large ? 3 : 4.5;
    const r = ratio(fg,bg);
    if (r < need) out.push({sel: el.tagName.toLowerCase()+'.'+(el.className||'').toString().split(' ').filter(Boolean).join('.'),
                            ratio: +r.toFixed(2), need, px, txt: txt.slice(0,48)});
  }
  return out;
}
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(executable_path=_CHROME)
    for theme in ['light','dark']:
      pg=await b.new_page(viewport={'width':1280,'height':900},color_scheme=theme)
      await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(700)
      groups=await pg.evaluate("document.querySelectorAll('#groups button').length")
      allbad=[]
      for g in range(groups):
        await pg.click(f'#groups button[data-g="{g}"]'); await pg.wait_for_timeout(200)
        n=await pg.evaluate("document.querySelectorAll('#tabs button').length")
        for i in range(n):
          t=pg.locator('#tabs button').nth(i); lbl=await t.inner_text(); await t.click(); await pg.wait_for_timeout(260)
          bad=await pg.evaluate(JS)
          for x in bad: x['tab']=lbl
          allbad += bad
      # deduplizieren
      seen=set(); uniq=[]
      for x in allbad:
        k=(x['sel'],x['ratio'])
        if k not in seen: seen.add(k); uniq.append(x)
      print(f'--- {theme}: {len(uniq)} Kontrastprobleme')
      for x in sorted(uniq,key=lambda y:y['ratio'])[:12]:
        print(f"   {x['ratio']:>5} (nötig {x['need']}) {x['sel'][:46]:46s} [{x['tab'][:18]}] {x['txt'][:34]}")
      await pg.close()
    await b.close()
asyncio.run(main())
