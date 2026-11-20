# -*- coding: utf-8 -*-
"""Der Doppelhemmer-Zweig des Labors darf nicht auf die alte, ueberholte
Behauptung zurueckfallen.

ANLASS (15.11.2026): Das Labor sagte an zwei Stellen, ein Wirkstoff, der FAAH
und MAGL zugleich hemmt, sei "am Menschen nie geprueft worden" und es gebe
"kein Programm". Eine Registerabfrage zeigte das Gegenteil: BMS-986368 laeuft
in drei Phase-2-Studien mit zusammen 362 Teilnehmenden an 139 Orten. In PubMed
gibt es zu dem Stoff NULL Treffer - "keine veroeffentlichten Ergebnisse" war
also richtig, "nicht geprueft" war falsch.

GENAU DIESE UNTERSCHEIDUNG bewacht der Test. Sie ist das, was die Seite sonst
auszeichnet, und sie stand hier auf dem Kopf.
Faellt gegen vor-dual.html durch."""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io,re,sys
T=io.open(HIER + '/page.html',encoding='utf-8').read(); F=[]
# Die alte Behauptung darf nirgends mehr stehen
for alt in ['MAGL zugleich hemmt, ist am Menschen nie geprüft worden',
            'Dafür gibt es am Menschen kein Programm']:
    if alt in T: F.append('Die ueberholte Behauptung steht wieder da: "%s"'%alt[:50])
# Der Stoff und seine Studien
if 'BMS-986368' not in T: F.append('BMS-986368 fehlt')
for nct in ['NCT06782490','NCT06808984','NCT07704840']:
    if nct not in T: F.append('Studie %s fehlt'%nct)
# Die Unterscheidung muss ausdruecklich dastehen
i=T.find('Bis vor kurzem')
if i<0:
    F.append('Der korrigierte Doppelhemmer-Zweig fehlt')
else:
    Z=T[i:i+2600]
    if 'keine veröffentlichten Ergebnisse' not in Z or 'nicht geprüft' not in Z:
        F.append('Die Unterscheidung "keine Ergebnisse" / "nicht geprueft" fehlt')
    if 'kein Profil' not in Z:
        F.append('Dass der Stoff ohne Veroeffentlichung kein Profil bekommt, steht nicht da')
    # Die Beobachtung zu den Anwendungsgebieten darf keine Unterstellung werden
    if 'Spastik' in Z and 'nicht sagen' not in Z and 'lässt sich von außen' not in Z:
        F.append('Die Beobachtung zu den Anwendungsgebieten ist nicht als unsicher gekennzeichnet')
    for b in ['um dem Problem auszuweichen','bewusst vermieden','offensichtlich deshalb']:
        if b in Z: F.append('Unterstellung: "%s"'%b)
# Es darf KEIN Stoffprofil geben, solange es keine Veroeffentlichung gibt
if "{id:'bms'" in T or "{id:'bms986368'" in T:
    F.append('BMS-986368 hat ein Stoffprofil, obwohl es keine einzige Veroeffentlichung gibt')
print('FEHLER' if F else 'OK','Doppelhemmer: Programm genannt, Unterscheidung gewahrt')
for f in F: print(' -',f)
sys.exit(1 if F else 0)
