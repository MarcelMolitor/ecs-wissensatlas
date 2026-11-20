# -*- coding: utf-8 -*-
"""Dauertest: die belegten Organtexte der beiden koerpereigenen Botenstoffe
bleiben belegt, und die Zahl der unbelegten steigt nicht wieder.

WARUM DIESER TEST GEBRAUCHT WIRD: Die Organtexte sind nie im Ganzen geprueft
worden, und die Messung am 09.11.2026 ergab 56 von 161 ohne jeden Beleg - 35
Prozent. Das Muster zeigte nach innen: nicht die Randstoffe standen schlecht
da, sondern die zentralen (Anandamid 7 von 9 unbelegt, 2-AG 7 von 8,
Rimonabant 6 von 6). belege.py findet das nicht, weil es nur Elemente mit
einer ev()-Belegstufe ansieht; Organtexte tragen eine Dichtestufe 1-3, keine
Belegstufe. Das war die sechste Luecke derselben Art.

Dieser Test haelt zwei Dinge fest:
 1. Die sechs in dieser Runde belegten Felder tragen weiter ihren Beleg, und
    zwar namentlich den richtigen. Faellt einer heraus - etwa weil eine
    spaetere Runde den Text neu schreibt -, schlaegt der Test an.
 2. Eine OBERGRENZE fuer die Gesamtzahl unbelegter Organtexte. Sie steht auf
    dem erreichten Stand (50). Damit kann die Zahl weiter sinken, ohne den
    Test zu brechen, aber nicht wieder steigen.

Geprueft wird an der QUELLDATEI, nicht im Browser: SUBS liegt in einer IIFE
und ist von aussen nicht erreichbar - das war schon bei t/kern.py die Lehre.
"""
import os as _os
HIER = _os.path.dirname(_os.path.abspath(__file__))
_c = _os.environ.get('CHROME_PATH') or '/opt/pw-browsers/chromium-1194/chrome-linux/chrome'
_CHROME = _c if _os.path.exists(_c) else None  # None => Playwright nimmt sein eigenes Chromium
import io, re, sys

QUELLE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'

# Feld -> PMID, die dort stehen MUSS.
PFLICHT = {
    ('aea', 'brain'):  '22776900',   # FAAH-Knockout + geschluckter Hemmer
    ('aea', 'spinal'): '11698030',   # niedrig CB1 / hoch TRPV1
    ('aea', 'gut'):    '11704633',   # Zwischenhirn, CB1-Blocker verhindert
    ('aea', 'heart'):  '9931142',    # Gefaessbett, 2-AG und THC als Gegenprobe
    ('aea', 'repro'):  '27568210',   # menschliche Gebaermutterzellen
    ('2ag', 'brain'):  '20159446',   # DAGL-alpha-Knockout
    # Runde 2 (11.11.2026): die beiden schlechtesten Stoffe der Seite.
    ('rim', 'brain'):    '18022033',  # Meta-Analyse, Abbruch wegen Stimmung/Angst
    ('rim', 'fat'):      '19112166',  # ADAGIO-Lipids, CT: Bauch- gegen Unterhautfett
    ('rim', 'liver'):    '19112166',  # dieselbe Untergruppe, Leberfett
    ('rim', 'gut'):      '18227491',  # RIO gepoolt, Gewicht/Bauchumfang/Uebelkeit
    ('rim', 'pankreas'): '18227491',  # HOMA-IR, HbA1c, 45-57 % nicht gewichtserklaert
    ('rim', 'muskel'):   '18716045',  # Ratten-Clamp, peripher gegen zentral
    ('2ag', 'immune'):   '12711605',  # Monozyten-Wanderung, CB2, Anandamid als Gegenprobe
    ('2ag', 'spinal'):   '22924700',  # MAGL-Hemmer am Rueckenmark, 2-AG stieg NICHT
    ('2ag', 'gut'):      '12055133',  # Kleinhirn als Kontrollregion
    ('2ag', 'bone'):     '16407142',  # CB2-Knockout, Rezeptor belegt, nicht der Ligand
    ('2ag', 'pankreas'): '18092149',  # menschliche Inselzellen, CB1 hoch / CB2 runter
    ('mon', 'fat'):      '41038215',  # Phase 2a: Gewicht gemessen, Fettdepot nicht
    ('mon', 'liver'):    '18716045',  # fuer Monlunabant nicht gemessen -> Stufe 0
    ('mon', 'muskel'):   '18716045',  # dito
    ('mon', 'pankreas'): '41038215',  # Ziel, kein Ergebnis -> Stufe 0
    # Runde 3 (12.11.2026): THC, der schlechteste Stoff der Seite (4 von 10 offen).
    # Drei der vier Felder behaupteten mehr, als gemessen ist - siehe die
    # Docstrings in scratchpad/p_thc.py.
    ('thc', 'lung'):   '31298945',  # Reizung kommt vom Rauch, nicht vom Rezeptor
    ('thc', 'fat'):    '19681888',  # Rueckgabe aus dem Fett: RATTE, nicht Mensch
    ('thc', 'immune'): '39921765',  # 40 klinische Studien: am Menschen KEINE Aenderung
    ('thc', 'repro'):  '15562018',  # CB1 auf Spermien, Laborversuch - nicht "steuert"
    # Runde 5 (13.11.2026): sieben Felder. Der Fund: 2ag.muskel und die
    # Muskel-Tafel sagten flach 'CB1 daempft die Zuckeraufnahme' (eine
    # Rattenarbeit), waehrend die Seite laengst eine Messung am Menschen in
    # die GEGENRICHTUNG trug.
    ('thc', 'mund'):   '35986066',  # Maus-Mechanismus; Mensch nur Befragung
    ('thc', 'ohr'):    '33364406',  # KEIN Nutzen gegen Tinnitus belegt
    ('2ag', 'muskel'): '41869774',  # Clamp an 21 Maennern - Gegenrichtung zur Ratte
    ('nab', 'gut'):    '26103030',  # Meta-Analyse, niedrige Qualitaet, Gruppe statt Nabilon allein
    ('thcv', 'fat'):   '27573936',  # Pilot-RCT; Hauptzielwert HDL NICHT erreicht
    ('bcp', 'gut'):    '21356367',  # Maus-Kolitis, CB2-Blocker hebt auf
    ('prop', 'liver'): '42810868',  # Zusammenhang in Klinikdaten
    ('nbx', 'liver'):  '42942824',  # CYP2C9 / CYP2C19
    ('mtz', 'spinal'): '25557763',  # Maus, CB1- und TRPV1-Blockade
}
# Die drei Felder, die ausdruecklich KEINE Wirkstaerke behaupten duerfen, weil
# fuer Monlunabant an diesem Organ nichts gemessen ist. Siehe t/organstufe.py
# fuer die gerenderte Wendung; hier nur die Zahl in der Quelle.
PFLICHT_STUFE0 = [('mon', 'liver'), ('mon', 'muskel'), ('mon', 'pankreas')]
# Stand nach der Runde vom 13.11.2026 (vorher 56, 50, 35, 31, 23). Darf sinken, nicht steigen.
OBERGRENZE_UNBELEGT = 4    # 14.11.: 11 -> 10 (nab/heart belegt)
#                          # 20.11.: 10 -> 4 (sechs Felder belegt: bcp/bone,
#                          # cbd/spinal, cbg/gut, inh/gut, mtz/liver, thcv/gut)
#                          # NUR SENKEN, NIE ANHEBEN. Reisst ein neuer Stoff die
#                          # Grenze, fehlen Belege - nicht Spielraum.
#                          # Offen bleiben mit Grund: bcp/skin, cbda/liver,
#                          # syn/gut, syn/lung. Fuer die synthetischen
#                          # Cannabinoide fand sich nur ein Einzelfall mit
#                          # LSD-Komedikation und eine Kohorte von 17 Faellen,
#                          # die Unruhe und Rhythmusstoerungen berichtet - nicht
#                          # Uebelkeit - bei einem Intervall von 1,0 bis 108.
# THC darf KEIN unbelegtes Organfeld mehr haben - der Stoff war der schlechteste
# der Seite und ist der, den Leser am haeufigsten nachschlagen.
LUECKENLOS = ['thc']
# Keine Dosisangaben bei erhaeltlichen Stoffen. [[39921765]] nennt Tagesmengen
# aus den eingeschlossenen Studien; die duerfen nicht in die Felder wandern.
KEINE_DOSIS = ['thc', 'cbd', 'dro', 'nbx', 'pea', 'oea', 'nab', 'thcv', 'bcp']


def organfelder(S):
    i = S.find('const SUBS = [')
    blk = S[i:S.find('\nconst KNOW', i)]
    marken = [(m.start(), m.group(1)) for m in
              re.finditer(r"\{id:'([a-z0-9]+)',group:'[^']*',name:'[^']*'", blk)]
    marken.append((len(blk), None))
    raus = {}
    for n in range(len(marken) - 1):
        seg = blk[marken[n][0]:marken[n + 1][0]]
        m = re.search(r'organs:\{', seg)
        if not m:
            continue
        j = m.end(); tiefe = 1; k = j
        while k < len(seg) and tiefe:
            if seg[k] == '{':
                tiefe += 1
            elif seg[k] == '}':
                tiefe -= 1
            k += 1
        for f in re.finditer(r"(\w+):\[(\d),'((?:[^'\\]|\\.)*)'\]", seg[j:k - 1]):
            raus[(marken[n][1], f.group(1))] = (f.group(3), f.group(2))
    return raus


def main():
    S = io.open(QUELLE, encoding='utf-8').read()
    felder = organfelder(S)
    print('Organtexte gefunden:', len(felder))
    probleme = []
    if len(felder) < 150:
        probleme.append('nur %d Organtexte gefunden - Muster veraltet?' % len(felder))

    for (sub, organ), pmid in sorted(PFLICHT.items()):
        eintrag = felder.get((sub, organ))
        if eintrag is None:
            probleme.append('%s.%s fehlt ganz' % (sub, organ))
            continue
        txt, stufe = eintrag
        if '[[%s]]' % pmid not in txt:
            probleme.append('%s.%s ohne den Beleg %s (steht dort: %s)'
                            % (sub, organ, pmid, re.findall(r'\[\[(\d+)\]\]', txt) or 'kein Beleg'))
        else:
            print('  ok  %-4s %-8s Stufe %s -> %s' % (sub, organ, stufe, pmid))

    for sub, organ in PFLICHT_STUFE0:
        eintrag = felder.get((sub, organ))
        if eintrag is None:
            probleme.append('%s.%s fehlt ganz, sollte Stufe 0 tragen' % (sub, organ))
        elif eintrag[1] != '0':
            probleme.append('%s.%s traegt Stufe %s - behauptet eine Wirkstaerke, obwohl an'
                            ' diesem Organ nichts gemessen ist' % (sub, organ, eintrag[1]))
        else:
            print('  ok  %-4s %-8s Stufe 0 (nicht untersucht)' % (sub, organ))

    for s in LUECKENLOS:
        luecken = sorted(o for (sub, o), v in felder.items()
                         if sub == s and '[[' not in v[0])
        if luecken:
            probleme.append('%s muss lueckenlos belegt sein, offen: %s' % (s, luecken))
        else:
            print('  ok  %s lueckenlos belegt' % s)
    for (sub, organ), v in felder.items():
        if sub in KEINE_DOSIS:
            for d in (' mg', 'Milligramm', ' mg/'):
                if d in v[0]:
                    probleme.append('Dosisangabe bei erhaeltlichem Stoff %s.%s: %s'
                                    % (sub, organ, d.strip()))

    # Die Muskel-Tafel der Koerperkarte: Tierbefund nicht mehr als Tatsache.
    if 'CB1 dämpft diese Aufnahme.' in S:
        probleme.append("Muskel-Tafel sagt wieder flach 'CB1 dämpft diese Aufnahme.'")
    elif 'beim Menschen ist die Richtung offen' not in S:
        probleme.append('Muskel-Tafel nennt die offene Richtung am Menschen nicht')
    else:
        print('  ok  Muskel-Tafel: Tierversuch benannt, Richtung am Menschen offen')
    t2 = felder.get(('2ag', 'muskel'), ('', ''))[0]
    if 'Gegenrichtung' not in t2 or 'ganzen Körpers' not in t2:
        probleme.append('2ag.muskel: Gegenbefund am Menschen oder die Einschraenkung '
                        "'des ganzen Koerpers' fehlt")
    tv = felder.get(('thcv', 'fat'), ('', ''))[0]
    if 'Hauptzielwert' not in tv:
        probleme.append('thcv.fat verschweigt, dass der Hauptzielwert nicht erreicht wurde')

    # 15.11.2026: Ein Feld gilt als belegt bei einem PMID ODER einer NCT-Nummer.
    # Anlass: Die Nimacimab-Karte ruht bei brain und gut auf Registereintraegen -
    # zu diesem Stoff existiert genau EINE Veroeffentlichung. Ein Registereintrag
    # ist eine nachpruefbare Quelle, sie hat nur keinen PMID; die Seite nennt
    # NCT-Nummern ohnehin im Lesertext. WICHTIG: Nur die konkrete NUMMER zaehlt,
    # nicht die Floskel "ClinicalTrials.gov" - sonst waere das eine Hintertuer,
    # mit der sich jede Luecke zuschreiben liesse. Obergrenze jetzt 4.
    belegt = lambda t: ('[[' in t) or re.search(r'NCT\d{8}', t)
    ohne = [k for k, v in felder.items() if not belegt(v[0])]
    # Gegenprobe: Die Floskel allein darf ein Feld NICHT belegt machen.
    assert not belegt('nur Prüfplan auf ClinicalTrials.gov ohne Nummer'), \
        'Die Floskel allein wuerde als Beleg zaehlen - Hintertuer offen'
    print('Organtexte ohne Beleg: %d (Obergrenze %d)' % (len(ohne), OBERGRENZE_UNBELEGT))
    if len(ohne) > OBERGRENZE_UNBELEGT:
        neu = sorted('%s.%s' % k for k in ohne)
        probleme.append('%d unbelegte Organtexte, erlaubt sind %d. Liste: %s'
                        % (len(ohne), OBERGRENZE_UNBELEGT, ', '.join(neu)))
    elif len(ohne) < OBERGRENZE_UNBELEGT:
        print('  (%d weniger als die Obergrenze - die Obergrenze darf nachgezogen werden)'
              % (OBERGRENZE_UNBELEGT - len(ohne)))

    print('Probleme:', probleme or 'keine')
    if probleme:
        sys.exit(1)


main()
