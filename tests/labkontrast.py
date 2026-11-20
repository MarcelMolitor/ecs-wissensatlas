# -*- coding: utf-8 -*-
"""Kontrast der Einschaetzungs-Ueberschrift im Wirkstoff-Labor, ueber ALLE Modi und
   Einsatzgebiete. audit4 prueft nur den Startzustand; die Farbe haengt hier aber an
   der Belegstufe des gewaehlten Gebiets. Chromium liefert color(srgb 0..1), nicht rgb(0..255)."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright
JS = """() => {
  const el = document.querySelector('#labVerdict .fy-h'); if (!el) return null;
  const parse = c => {
    const n = (c.match(/-?\\d*\\.?\\d+/g) || []).slice(0,3).map(Number);
    return c.startsWith('color(') ? n : n.map(v => v/255);
  };
  const lum = c => { const [r,g,b] = parse(c).map(v => v<=.03928 ? v/12.92 : Math.pow((v+.055)/1.055,2.4));
    return .2126*r + .7152*g + .0722*b; };
  let bg = null, n = el.parentElement;
  while (n && !bg){ const c = getComputedStyle(n).backgroundColor; if (c && c !== 'rgba(0, 0, 0, 0)') bg = c; n = n.parentElement; }
  const l1 = lum(getComputedStyle(el).color), l2 = lum(bg || 'rgb(255,255,255)');
  return Math.round(((Math.max(l1,l2)+.05)/(Math.min(l1,l2)+.05))*100)/100;
}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=_CHROME)
        schlecht, geprueft = [], 0
        for schema in ('light', 'dark'):
            pg = await b.new_page(viewport={'width':1400,'height':1500}, color_scheme=schema)
            await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(1800)
            ok = False
            for gi in range(await pg.locator('#groups button').count()):
                await pg.locator('#groups button').nth(gi).click(); await pg.wait_for_timeout(220)
                for ti in range(await pg.locator('#tabs .tab').count()):
                    if (await pg.locator('#tabs .tab').nth(ti).inner_text()).strip() == 'Wirkstoff-Labor':
                        await pg.locator('#tabs .tab').nth(ti).click(); await pg.wait_for_timeout(800); ok = True; break
                if ok: break
            for mode in ('faah', 'cb2', 'cb1'):
                await pg.click('.seg[data-lab="mode"] button[data-v="%s"]' % mode); await pg.wait_for_timeout(700)
                for o in await pg.eval_on_selector_all('#labUse option', 'e=>e.map(x=>x.value)'):
                    await pg.select_option('#labUse', o); await pg.wait_for_timeout(260)
                    k = await pg.evaluate(JS); geprueft += 1
                    if k is None or k < 4.5: schlecht.append((schema, mode, o, k))
            await pg.close()
        print('geprüfte Einstellungen:', geprueft)
        print('unter 4,5:1:', schlecht if schlecht else 'keine')
        await b.close()
asyncio.run(main())
