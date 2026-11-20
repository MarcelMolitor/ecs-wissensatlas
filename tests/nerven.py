# -*- coding: utf-8 -*-
"""Periphere Nerven auf der Koerperkarte (14.11.2026).

WARUM DIESE STELLE BESONDERS IST: An ihr haengt die groesste Hoffnung des
Feldes - Schmerzlinderung ohne Rausch, weil der Wirkstoff nicht ins Gehirn
gelangen muesste. Der Mechanismus ist an Maeusen gezeigt [[17558404]], am
Menschen ist daraus bisher nichts geworden. Genau diese Reihenfolge muss die
Tafel halten: erst der Befund, dann sein Scheitern am Menschen - und nicht die
eine kleine positive Studie als Ergebnis.

DIE FALLE: Von den drei randomisierten Studien ist die EINZIGE positive die
KLEINSTE (29 Teilnehmende). Wer sie ohne diese Einordnung nennt, dreht die
Aussage um. Der Test verlangt den einordnenden Satz ausdruecklich.

DIE DICHTESTUFE ist 0, weil die Seite fuer den menschlichen peripheren Nerv
keinen Messwert traegt - der Mausbefund ist kein Messwert am Menschen.
Die Wirkungsstufen von THC und CBD stehen nach der Regel vom 14.11. auf 1
(siehe t/wirkstufe.py).

MITGEPRUEFT: Die Schilddruese wurde am selben Tag geprueft und BEWUSST
weggelassen (38 Treffer, keiner passend - nur eine Zellkulturarbeit an
Krebszellen und eine Rattenarbeit). Taucht sie ohne neue Belege wieder auf,
ist das ein Rueckfall und der Test meldet es.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, io, re, sys
from playwright.async_api import async_playwright

EXE = _CHROME
SEITE = sys.argv[1] if len(sys.argv) > 1 else 'file://' + HIER + '/page.html'
QUELLE = SEITE.replace('file://', '')

NEU = ['17558404', '39016024', '31793418']
MUSS = [
    'Schmerzlinderung ohne Rausch',
    'nur in den Schmerzfasern ausgeschaltet',
    'nicht aber, wenn man sie direkt ins Rückenmark gab',   # der entscheidende Kontrollarm
    'Am Menschen ist daraus bisher kein Nutzen geworden',
    'keine besser als Placebo',
    'Dagegen steht die kleinste Arbeit',                     # die Einordnung der positiven Studie
    'der die größeren nicht aufhebt',
    'nicht nachgewiesen',                                    # Dichte ohne Messwert am Menschen
]
VERBOTEN = [
    'CBD hilft bei Nervenschmerz',
    'lindert Nervenschmerzen',
    'wirkt gegen Nervenschmerz',
    'Schmerzlinderung ohne Rausch ist belegt',
    ' mg', 'Milligramm',
]
STUFEN = {'thc': 'Schwache Wirkung', 'cbd': 'Schwache Wirkung'}


async def main():
    probleme = []
    S = io.open(QUELLE, encoding='utf-8').read()
    T = S[S.find('<title>'):]
    for p in NEU:
        if ("['%s'," % p) not in T: probleme.append('Beleg %s fehlt im Verzeichnis' % p)
        if ('[[%s]]' % p) not in T: probleme.append('Beleg %s wird nicht benutzt' % p)
    # Schilddruese: bewusst weggelassen, darf nicht ohne neue Belege zurueckkommen
    if re.search(r"\n  \w+:\{name:'Schilddrüse'", T):
        probleme.append('Die Schilddruese ist wieder auf der Karte - am 14.11.2026 '
                        'bewusst weggelassen, weil es dazu keine passenden Belege gibt')

    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width': 1280, 'height': 1050})
        fehler = []
        pg.on('pageerror', lambda e: fehler.append('PAGEERROR ' + str(e)))
        await pg.goto(SEITE); await pg.wait_for_timeout(1800)

        if not await pg.locator('#or-nerv').count():
            print('Probleme: die Stelle "Periphere Nerven" fehlt'); await b.close(); sys.exit(1)
        n = await pg.locator('#bodySvg .organ').count()
        if n != 23: probleme.append('%d Organe statt 23' % n)

        # Der Marker muss AUF dem Koerper liegen - am 14.11. lag 288|306 schon
        # ausserhalb, die Arme reichen nur bis x=298.
        drin = await pg.evaluate("""()=>{const sv=document.getElementById('bodySvg');
          const f=[...sv.querySelectorAll('path,ellipse,rect')].filter(e=>!e.closest('.organ'));
          const m=document.querySelector('#or-nerv circle, #or-nerv ellipse');
          const bb=m.getBBox(); const pt=sv.createSVGPoint();
          pt.x=bb.x+bb.width/2; pt.y=bb.y+bb.height/2;
          return f.some(q=>{try{return q.isPointInFill(pt)}catch(e){return false}})}""")
        if not drin: probleme.append('der Marker der Nerven liegt nicht auf dem Koerper')

        # Beschriftung darf nicht aus dem Bild laufen (passierte mit dem langen Namen)
        raus = await pg.evaluate("""()=>{const sv=document.getElementById('bodySvg').getBoundingClientRect();
          return [...document.querySelectorAll('#bodySvg .olabel')].filter(t=>{const r=t.getBoundingClientRect();
            return r.left<sv.left-1||r.right>sv.right+1}).map(t=>t.textContent)}""")
        if raus: probleme.append('Beschriftung laeuft aus dem Bild: %s' % raus)

        for sid, soll in STUFEN.items():
            await pg.locator('button.chip[data-id="%s"]' % sid).first.evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(300)
            await pg.locator('#or-nerv').evaluate(
                "e=>e.dispatchEvent(new MouseEvent('click',{bubbles:true}))")
            await pg.wait_for_timeout(300)
            t = await pg.inner_text('#organInfo')
            if '${' in t or '[[' in t: probleme.append('%s: Vorlagenrest in der Nerventafel' % sid)
            m = re.search(r'\n(Nicht untersucht|Schwache Wirkung|Deutliche Wirkung|Starke Wirkung)\.', t)
            if not m or m.group(1) != soll:
                probleme.append('%s/nerv steht auf "%s", erwartet "%s"'
                                % (sid, m.group(1) if m else '??', soll))
            if sid == 'thc':
                for s in MUSS:
                    if s not in t: probleme.append('Kernaussage fehlt: %s' % s)
                for v in VERBOTEN:
                    if v in t: probleme.append('unerwuenscht: %s' % v.strip())
                marken = await pg.locator('#organInfo sup.cite').count()
                if marken < 5: probleme.append('nur %d Belegmarken, erwartet mindestens 5' % marken)
                else: print('  ok  Nerventafel: alle Kernaussagen, %d Belegmarken' % marken)
        print('Probleme:', probleme or 'keine')
        print('Fehler:', fehler or 'keine')
        await b.close()
        if probleme or fehler: sys.exit(1)

asyncio.run(main())
