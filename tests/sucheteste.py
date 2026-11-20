# -*- coding: utf-8 -*-
"""Breiter Suchtest: welche naheliegenden Begriffe finden nichts?"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import asyncio, sys
from playwright.async_api import async_playwright
EXE = _CHROME
W = """mikrobiom darmflora darmbakterien probiotika ballaststoffe
sport ausdauersport laufen runnershigh stress schlafstörung insomnie schlaflosigkeit
angststörung panikattacke depression burnout psychose schizophrenie sucht abhängigkeit entzug toleranz
epilepsie anfall krampfanfall dravet lennox migräne kopfschmerz cluster
reizdarm morbus crohn colitis übelkeit erbrechen hyperemesis appetitlosigkeit kachexie
arthrose arthritis rheuma gelenkschmerz rückenschmerz nervenschmerz neuropathie fibromyalgie
multiple sklerose spastik parkinson alzheimer demenz als tourette tics
krebs tumor chemotherapie palliativ hospiz
glaukom augeninnendruck juckreiz neurodermitis schuppenflechte akne psoriasis
übergewicht adipositas diabetes insulin fettleber leberschaden
schwangerschaft stillen muttermilch kinder jugendliche pubertät alter senioren
herzinfarkt blutdruck herzrhythmus schlaganfall
immunsystem entzündung autoimmun allergie infekt corona longcovid fatigue
knochen osteoporose muskelkater regeneration
genetik variante faah-gen vererbung geschlecht frauen männer
wechselwirkung blutverdünner antidepressiva statine leberenzym abbau
autofahren arbeitsplatz drogentest urintest haaranalyse
dosierung nebenwirkung überdosis vergiftung notaufnahme""".split()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=EXE, args=['--no-sandbox'])
        pg = await b.new_page(viewport={'width':1280,'height':900})
        await pg.goto('file://' + HIER + '/page.html'); await pg.wait_for_timeout(2000)
        leer, duenn = [], []
        for w in W:
            await pg.fill('#findQ',''); await pg.wait_for_timeout(120)
            await pg.fill('#findQ', w); await pg.wait_for_timeout(330)
            n = await pg.evaluate("() => document.querySelectorAll('#findRes [role=option]').length")
            if n == 0: leer.append(w)
            elif n <= 2: duenn.append((w, n))
        print('Begriffe geprueft:', len(W))
        print('\nOHNE TREFFER (%d):\n  %s' % (len(leer), ' '.join(leer)))
        print('\nNUR 1-2 TREFFER (%d):\n  %s' % (len(duenn), ' '.join('%s(%d)'%d for d in duenn)))
        await b.close()
asyncio.run(main())
