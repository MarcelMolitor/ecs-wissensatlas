# -*- coding: utf-8 -*-
"""Haelt die Verneinungen fest, die ein ganzes Forschungsprogramm bestreiten.

WARUM ES DIESEN TEST GIBT: Die Seite sagt an vielen Stellen "dazu gibt es
keine Studie". Das ist ihre fragilste Klasse von Aussagen - sie wird falsch,
ohne dass sich auf der Seite etwas aendert. Zweimal ist das binnen einer Woche
passiert:

  cbn.skin sagte "zur Wirkung auf die Haut gibt es keine Studie". Es gab eine
  abgeschlossene Phase 2 (NCT04908215).

  Rimonabant stand als abgeschlossene Geschichte da. Es laufen vier Studien.

Beide wurden von Hand gefunden, beide zufaellig. Am 23.11.2026 sind die drei
Saetze, die ein ganzes Programm bestreiten, nachgesehen und mit Datum versehen
worden. Dieser Test haelt fest, dass sie ihr Datum und ihre Registerbelege
behalten - und dass die Abfragen, mit denen man sie prueft, auf der Seite
stehen.

WAS DIESER TEST NICHT KANN: nachsehen. Die Suite laeuft ohne Netz, und eine
Registerabfrage ergibt nicht bei jedem Lauf dasselbe. Geprueft wird also die
FORM: Steht ein Datum dabei? Ist die Registernummer genannt? Hat der Stoff eine
Abfrage? Das eigentliche Nachsehen bleibt Handarbeit - die Arbeitsliste dafuer
liegt in scratchpad/verneinungen.py und sortiert nach Dringlichkeit.

WER EINE DIESER AUSSAGEN AENDERT, muss das Datum mitaendern. Genau das soll
dieser Test erzwingen: Ein Stempel ist eine Behauptung darueber, wann jemand
geschaut hat.
"""
import io
import os
import re
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
QUELLE = sys.argv[1] if len(sys.argv) > 1 else HIER + '/page.html'
S = io.open(QUELLE, encoding='utf-8').read()

# Das Kopfprotokoll zitiert eigene Fehler und dabei Saetze der Seite.
UMFANG = 200000
I = S[UMFANG:]

pr = []

# --- 1) Die drei Verneinungen: Aussage, Beleg, Datum ----------------------
# Form: (Name, Kernsatz, Dinge die im Umfeld stehen muessen, Umfeldgroesse)
FEST = [
    ('THCP', 'keine einzige Studie am Menschen',
     ['null Einträge', 'ClinicalTrials.gov', 'abgefragt am 23.11.2026'], 400),
    ('CBC', 'Es gibt keine klinischen Studien</b>',
     ['NCT07087938', 'zurückgezogen', 'abgefragt am 23.11.2026',
      'complete blood count'], 1500),
    ('CBN-Abwehr', 'Am Menschen selbst ist zur Abwehr nichts gemessen',
     ['elf Einträge', 'Um die Abwehr geht es in keinem',
      'abgefragt am 23.11.2026'], 700),
]
for name, kern, pflicht, weite in FEST:
    i = I.find(kern)
    if i < 0:
        pr.append('%s: die Aussage selbst ist weg ("%s")' % (name, kern[:40]))
        continue
    umfeld = I[max(0, i - weite):i + weite]
    for p in pflicht:
        if p not in umfeld:
            pr.append('%s: "%s" fehlt im Umfeld der Aussage' % (name, p))

# --- 2) Die Abfragen, mit denen man sie nachprueft ------------------------
# Ohne Abfrage ist eine Verneinung nicht nachpruefbar - genau daran lag es
# bei CBC und THCP, bis zum 23.11.2026.
for stoff, begriff in [('cbc', 'cannabichromene'),
                       ('thcp', 'tetrahydrocannabiphorol'),
                       ('cbn', 'cannabinol')]:
    m = re.search(r"\b%s:\{pm:'((?:[^'\\]|\\.)*)'"
                  r"(?:,\s*ct:\{intervention:'((?:[^'\\]|\\.)*)'\})?\}" % stoff, S)
    if not m:
        pr.append('%s: keine Abfrage auf der Seite' % stoff)
        continue
    if begriff not in (m.group(1) or ''):
        pr.append('%s: die PubMed-Abfrage nennt "%s" nicht' % (stoff, begriff))
    if not m.group(2):
        pr.append('%s: keine Registerabfrage' % stoff)
    elif begriff not in m.group(2):
        pr.append('%s: die Registerabfrage nennt "%s" nicht' % (stoff, begriff))

# --- 3) Kein Stempel ohne Nachsehen --------------------------------------
# Jeder Stempel vom 23.11.2026 muss zu einer Sache gehoeren, die an diesem Tag
# wirklich nachgesehen wurde. Darum keine nackte Zahl, sondern eine Liste: Wer
# einen Stempel setzt, traegt hier ein, WAS er nachgesehen hat. Sonst schlaegt
# der Test an - und genau das ist am 23.11. passiert, als die vier neuen
# CB2-Einsatzgebiete zwei weitere Stempel brachten.
# 27.11.2026 umgebaut: Vorher hing diese Regel an einem einzigen Datum. Das
# geht nur bis zum naechsten Arbeitstag gut - der 27.11. brachte zwei neue
# Stempel, die unbemerkt durchgelaufen waeren, weil nur der 23.11. gezaehlt
# wurde. Jetzt ein Datum pro Eintrag: Wer irgendwann einen Stempel setzt, muss
# unter SEINEM Datum eintragen, was er nachgesehen hat, und ein Datum, das im
# Text auftaucht aber hier fehlt, schlaegt an.
# NACHGETRAGEN am 27.11.2026, und zwar mit Vorbehalt: Diese drei Tage lagen
# vor dieser Regel. Ihre Eintraege sind aus dem beschrieben, WAS DIE SEITE
# SAGT - ich habe diese Abfragen nicht wiederholt. Sie stehen hier, damit die
# Regel greift, nicht als Bestaetigung. Wer einen davon anfasst, sieht neu
# nach und setzt sein eigenes Datum.
NACHGESEHEN = {
    '15.11.2026': [
        'Nimacimab NCT06577090: Pruefplan - was ein peripher begrenzter '
        'Antikoerper messen wuerde und was nicht',
        'Ein Pruefplan mit sechs Teilnehmenden, der ohne Ergebnis blieb: '
        'belegt ist das Prinzip, nicht die Wirkung',
        'Drei Studien, die sich auf Spastik und Unruhe richten - '
        'Registerstand',
        'Ein weiterer Pruefplan-/Registerstand im Organfeld (NICHT '
        'wiederholt, aus dem Seitentext nachgetragen)',
    ],
    '21.11.2026': [
        'Der dritte Zustand - angefasst, ohne berichtetes Ergebnis: '
        'Registerstand',
        'Nimacimab NCT06577090: Absicht klar, Wirkung nicht - daher '
        'niedrige Belegstufe',
        'NCT03900325: Nebenbeobachtung, ohne Ergebnis, Registerstand seit '
        'Jahren unbekannt',
        'NCT05622994: sollte 11/2023 fertig sein, Eintrag seitdem '
        '"unbekannt", nichts berichtet',
    ],
    '22.11.2026': [
        'US-Patent 6.630.507: am 21.04.2019 abgelaufen (Google Patents)',
        'NCT01385124, NCT01596075, NCT02392780, NCT02478424: alle vier auf '
        '"unbekannt", keine berichtet Ergebnisse',
        'NCT03093402: im Register und als Kongressbeitrag, kein Aufsatz',
    ],
    '23.11.2026': [
        'THCP im Studienregister: null Eintraege',
        'Cannabichromen im Studienregister: ein zurueckgezogener Eintrag',
        'Cannabinol im Studienregister: elf Eintraege, keiner zur Abwehr',
        'S-777469 bei Neurodermitis: zwei Studien, keine Ergebnisse',
        'KHK6188 bei Zoster-Neuralgie: eine Studie, keine Ergebnisse',
        'NCT03625453 (MAGL bei Tourette): kein Ergebnisbericht im Register – '
        'die Veroeffentlichung gibt es aber',
        ('Die vier unberichteten Rimonabant-Programme (Praediabetes NCT00325650, '
         'Essanfaelle NCT00481975, NASH NCT00576667, Alzheimer NCT00380302): '
         'alle has_results = false, keine Arbeit in PubMed. Zitiert an zwei '
         'Stellen: Quellenkarte b-quellen und Labor (CB1_RUN block|prae) – '
         'der Laboreintrag traegt bewusst das Datum der tatsaechlichen '
         'Nachschau vom 23.11., nicht das Datum seines Einbaus am 27.11.', 2),
    ],
    '28.11.2026': [
        # EIN Stempel im Text deckt beide Abfragen, deshalb hier auch ein
        # Eintrag: Die Regel vergleicht Fundstellen mit Eintraegen, und
        # zwei Eintraege auf einen Stempel waeren eine Buchung zu viel.
        'ME/CFS, zwei Abfragen unter einem Stempel. PubMed ("chronic fatigue '
        'syndrome endocannabinoid"): 5 Treffer, zwei davon wirklich auf ME/CFS '
        'zusammen mit diesem System verschlagwortet (24977967 Mangel-These, '
        '33361830 Strahlenschaeden), drei Fehltreffer der Suchlogik. Register '
        '(ME/CFS bzw. chronic fatigue syndrome x Cannabinoide oder PEA): 2 '
        'Eintraege - NCT05311852 (PEA mit Luteolin bei Long Covid, randomisiert, '
        'abgeschlossen) und ein Fehltreffer (Nasenspuelung bei Golfkriegs-'
        'Syndrom). Also nicht null - aber keiner MISST etwas an Menschen mit '
        'ME/CFS, und genau darum bleibt die Schlussfolgerung stehen',
    ],
    '27.11.2026': [
        'NCT02889224 (VISECA, Endocannabinoide beim Cushing-Syndrom, '
        'Bordeaux): abgeschlossen 09/2013, has_results = false, keine Arbeit '
        'in PubMed',
        'CB1-Blocker GEGEN das Cushing-Syndrom: keine einzige Studie im '
        'Register – deshalb kein Einsatzgebiet und kein siebtes '
        'Rimonabant-Programm',
        ('NCT00822744 (FIDELIO, FAAH-Hemmer bei Altersdepression, 527 '
         'Teilnehmende, abgeschlossen 02/2010): kein Ergebnisbericht, keine '
         'Arbeit in PubMed – die groesste FAAH-Pruefung am Menschen. Zitiert '
         'an zwei Stellen: Enzymkarte e-faahmensch und Labor '
         '(LAB_USE.altersdepression)', 2),
        'NCT07282574 (Roche, MAGL-Hemmer bei fortschreitender MS, Phase 2, '
        '360 Teilnehmende, 114 Zentren): laeuft seit 03/2026, Abschluss '
        'geplant 05/2028 – noch keine Ergebnisse zu erwarten',
        # Nachgetragen am 27.11.2026, nachdem genau diese Regel gemeldet
        # hatte, dass zwei Stempel im Text stehen, die hier fehlten. Sie
        # hat also getan, wofuer sie da ist.
        'AEF0117 im Register (Intervention AEF0117): genau 8 Studien – '
        'eine Phase 2b (NCT05322941, 333 Behandlungssuchende, '
        'abgeschlossen, has_results = false), eine Phase 2a (NCT03717272, '
        '29), sechs Phase 1. KEINE Phase 3 – deshalb ist „zwei '
        'Phase-3-Endpunkte“ ersetzt. Dazu die umgekehrte Richtung: '
        'positiv allosterische CB1-Modulatoren (auch ZCZ011, GAT211, '
        'GAT229, ABD1085) ergeben im Register 0 Treffer – die '
        'Verstaerker-Richtung ist am Menschen wirklich nie geprueft',
        'Trockenes Auge und Cannabinoide: im Register 0 Studien zu '
        'trockenem Auge, Keratoconjunctivitis sicca oder Sjoegren; von 30 '
        'augenbezogenen Cannabinoid-Studien misst keine ein Traenenmass. '
        'In PubMed kein Schirmer-Test, keine Traenenfilm-Aufreisszeit und '
        'keine Traenenosmolaritaet am Menschen – wohl aber vier Berichte '
        'ueber trockene Augen und eine OSDI-Messung (42524865), deshalb '
        'steht in der Augentafel jetzt die Dreiteilung statt „nicht '
        'belegt“',
        'NCT06577090 (Nimacimab, CBeyond): eine Woche nach dem genannten '
        'Abschluss des Hauptteils unveraendert – Termin steht, nimmt niemanden '
        'mehr auf, has_results weiter false. Neu gefunden: Verlaengerung seit '
        '05/2025 um 26 Behandlungswochen plus 13 Wochen Nachbeobachtung, '
        'daher Gesamtabschluss erst 02/2027',
        'Irafamdastat (frueher CC-97489/BMS-986368), vier Eintraege '
        'nachgesehen: NCT06782490 (200, 61 Orte), NCT06808984 (120, 77 Orte), '
        'NCT07704840 (42) alle RECRUITING; NCT05099822 (84) ABGEBROCHEN ohne '
        'genannten Grund. Dazu NCT05065541, PET an 32 Gesunden zur '
        'Enzymverfuegbarkeit im Gehirn, abgeschlossen 01/2024, '
        'has_results false, keine Arbeit in PubMed',
    ],
}
# 27.11.2026 nachgeschaerft: Die Regel nahm an, ein Stempel sei eine Nachschau.
# Das stimmt nicht, wenn DIESELBE Nachschau an zwei Stellen zitiert wird - die
# 527er-Studie steht in der Enzymkarte und im Labor. Statt die Liste mit einer
# Dopplung zu verfaelschen, darf ein Eintrag jetzt sagen, an wie vielen Stellen
# er zitiert wird: ('Text', 2). Ohne Zahl gilt 1.
def _soll(liste):
    return sum(e[1] if isinstance(e, tuple) else 1 for e in liste)


# Gross-/Kleinschreibung: Ein Stempel am Satzanfang ("(Abgefragt am
# 28.11.2026.)") ist derselbe Stempel wie einer mitten im Satz. Ohne
# IGNORECASE zaehlte diese Regel ihn nicht und meldete "0 im Text".
gefunden = sorted(set(re.findall(r'abgefragt am (\d{1,2}\.\d{1,2}\.20\d\d)',
                                 I, re.I)))
for tag in gefunden:
    if tag not in NACHGESEHEN:
        pr.append('Stempel vom %s im Text, aber kein Eintrag in NACHGESEHEN – '
                  'was wurde an dem Tag nachgesehen?' % tag)
for tag, liste in NACHGESEHEN.items():
    # Wie oben: ein Stempel am Satzanfang ("(Abgefragt am ...") ist
    # derselbe Stempel. I.count() unterscheidet Gross- und
    # Kleinschreibung, deshalb hier kleingeschrieben zaehlen.
    n = I.lower().count(('abgefragt am ' + tag).lower())
    if n != _soll(liste):
        pr.append('Stempel vom %s: %d im Text, aber %d Fundstellen als '
                  'nachgesehen eingetragen – wurde wirklich nachgesehen?'
                  % (tag, n, _soll(liste)))
heute = sum(I.lower().count(('abgefragt am ' + t).lower()) for t in NACHGESEHEN)

# --- 3b) Die zwei Programme, die geprueft und nie berichtet wurden --------
# Diese Klasse ist das Gegenstueck zur Verneinung: Nicht "niemand hat
# geprueft", sondern "jemand hat geprueft, und niemand erfaehrt es". Sie darf
# nicht stillschweigend zu einem "gescheitert" werden.
# Geprueft wird der EINTRAG, nicht ein Zeichenfenster: Beim ersten Versuch
# nahm ich 1200 Zeichen um die Registernummer und erwischte damit das Wort
# "gescheitert" aus dem NACHBAREINTRAG (Reizdarm, der wirklich gescheitert
# ist). Ein gruener Test waere das nicht gewesen, aber ein falscher Alarm, und
# die kosten dasselbe Vertrauen.
def cb2_eintrag(key):
    m = re.search(r"\bCB2_USE\s*=", S[UMFANG:])
    if not m:
        return None
    a = UMFANG + m.start()
    j = S.find('{', a)
    tief, k = 0, j
    while k < len(S):
        if S[k] == '{':
            tief += 1
        elif S[k] == '}':
            tief -= 1
        if tief == 0:
            break
        k += 1
    for t in re.split(r"\n (?=\w+:)", S[j:k + 1]):
        if re.match(r"\{?\s*%s:" % key, t):
            return t
    return None

for name, key, nct, pflicht in [
        ('S-777469 / Neurodermitis', 'neuro', 'NCT00703573',
         ['keine Ergebnisse hinterlegt', '209']),
        ('KHK6188 / Zoster-Neuralgie', 'zoster', 'NCT01544296',
         ['null Treffer', '42 Menschen'])]:
    t = cb2_eintrag(key)
    if not t:
        pr.append('%s: das Einsatzgebiet "%s" gibt es nicht mehr' % (name, key))
        continue
    if nct not in t:
        pr.append('%s: %s ist nicht mehr genannt' % (name, nct))
    for p in pflicht:
        if p not in t:
            pr.append('%s: "%s" fehlt' % (name, p))
    if 'gescheitert' in t:
        pr.append('%s: wird als "gescheitert" dargestellt, obwohl kein '
                  'Ergebnis berichtet wurde' % name)

# --- 4) Die Verneinungen, die schon einmal versagt haben -----------------
# DIE FEHLERART: Die Seite sagt, es gebe keine Studie am Menschen - und es
# gibt eine. Das ist der teuerste Fehler, den diese Seite machen kann, denn er
# klingt nach Sorgfalt. Bisher viermal gefunden, jedes Mal von Hand:
#
#   cbn.skin    "keine Studie" neben einer abgeschlossenen Phase 2
#   Rimonabant  "abgeschlossene Geschichte" neben vier laufenden Studien
#   CB2 entz    "nie geprueft" neben drei gescheiterten Geschwistern (27.11.)
#   Echinacea   "keine Studie am Menschen" neben einer randomisierten (27.11.)
#
# Darum eine TABELLE statt einer Regel je Fund: Wer den fuenften findet,
# haengt eine Zeile an, statt einen Block zu schreiben. Je Zeile: der Beleg,
# der dort stehen muss, das Fenster um ihn herum, und die Saetze, die darin
# nicht mehr vorkommen duerfen.
#
# ANKER IST DIE ZITATSTELLE, nicht die Nummer. Beim ersten Versuch stand hier
# '28610718'; die Nummer steht aber auch in der Quellenliste, 315 581 Zeichen
# vor der Karte. Das Fenster lag damit an der voellig falschen Stelle, und die
# Regel war zahnlos - aufgefallen ist das erst, als ich die Verneinung
# versuchsweise wieder einbaute und nichts anschlug.
VERSAGT = [
    ('NCT04908215', 'cbn.skin', 900, 300,
     ['keine Studie', 'nie geprüft', 'nicht geprüft']),
    # 27.11.2026: Hier stand "Es gibt keine Studie am Menschen, die einen
    # Nutzen von Echinacea über das Endocannabinoid-System zeigt." Laut PubMed
    # gibt es sie: 28610718, randomisiert und doppelblind, Hautscore bedeutsam
    # gesenkt, auch gegenüber dem Vergleichspräparat.
    ('[[28610718]]', 'Echinacea', 1200, 900,
     ['keine Studie am Menschen', 'gibt keine Studie', 'nie am Menschen geprüft']),
    # 27.11.2026: Hier stand "28 Jahre nach der Zellmessung [...] keine Studie,
    # die den Anspruch am Menschen geprueft haette. Nicht eine." Es gibt eine
    # (39025264, randomisiert, oxidativer Schaden an der Haut gemessen). Die
    # Stelle war die zugespitzteste Verneinung der ganzen Seite.
    ('[[39025264]]', 'Antioxidans-Anspruch', 1400, 1100,
     ['Nicht eine, die ihn widerlegt', 'keine Studie, die den Anspruch',
      'hat niemand geprüft']),
    # 27.11.2026: Hier stand "Dass PEA oder OEA beim Menschen ueber PPAR-alpha
    # wirken, hat niemand gemessen" mit der Stufe "nicht untersucht". Gemessen
    # ist am Menschen eine Wirkung (31054246); nur der Weg nicht.
    ('[[31054246]]', 'PPAR-α', 1300, 1000,
     ['hat niemand gemessen', 'in Mäusen geklärt, nicht in Menschen']),
    # 28.11.2026: Hier stand, von den FAAH-Pruefungen am Menschen habe "keine
    # einzige" ihren Hauptzielwert erreicht - waehrend die Seite zwei Klicks
    # weiter dieselbe Studie "das beste Ergebnis, das dieser Weg hat" nennt.
    # Laut PubMed hat sie alle drei Hauptzielwerte erreicht. Der erste Fall, in
    # dem die Seite nicht die Literatur falsch darstellte, sondern sich selbst.
    ('sie braucht eine Ausnahme', 'FAAH-Bilanz', 900, 1700,
     ['hat <b>keine einzige</b> ihren Hauptzielwert',
      'keine einzige ihren Hauptzielwert erreicht']),
    # 28.11.2026: Hier stand "ergibt keinen einzigen Treffer" und "keine
    # einzige Studie eingetragen". Beides als Suchergebnis falsch; die
    # Schlussfolgerung stimmte trotzdem.
    ('Bis zum 28.11.2026 stand hier als Begründung', 'ME/CFS', 400, 2400,
     ['ergibt keinen einzigen Treffer', 'ist keine einzige Studie eingetragen']),
]
for beleg, wer, vor_, nach_, boese in VERSAGT:
    n = I.count(beleg)
    if n == 0:
        pr.append('%s: der Beleg %s ist nicht mehr genannt' % (wer, beleg))
        continue
    if n > 1:
        # Nicht stillschweigend die erste Fundstelle nehmen: dann prueft die
        # Regel eine Stelle, die niemand gemeint hat.
        pr.append('%s: der Anker "%s" kommt %dx vor – das Fenster liegt dann '
                  'irgendwo. Anker eindeutig machen.' % (wer, beleg, n))
        continue
    i = I.find(beleg)
    umfeld = I[max(0, i - vor_):i + nach_]
    for schlecht in boese:
        if schlecht in umfeld:
            pr.append('%s: "%s" steht wieder neben einer Studie, die es gibt'
                      % (wer, schlecht))

# Und die Echinacea-Karte muss den Unterschied weiter machen, um den es geht:
# ein Nutzen ist gezeigt, der Weg nicht. Faellt der zweite Teil weg, behauptet
# die Seite ploetzlich mehr als ihre Quelle - der umgekehrte Fehler, aber
# derselbe Schaden.
# Anker ist die ZITATSTELLE [[...]], nicht die bloße Nummer: die steht auch
# in der Quellenliste, und dort steht der Kartentext naturgemäß nicht. Beim
# ersten Versuch meldete die Regel vier Fehler, die es nicht gab.
# --- Kernpruefungen: was eine Korrektur nicht verlieren darf ---------------
#
# WARUM ES DIESE FUNKTION GIBT: Die Pruefungen standen vorher als
#     i = I.find(<anker>)
#     if i >= 0: ...
# da - und damit hing jede Pruefung an genau dem Satz, den sie pruefen soll.
# Beim Sabotieren blieb die ME/CFS-Regel stumm, weil ich den Anker selbst
# entfernt hatte: kein Anker, kein Fenster, keine Pruefung. Eine Regel, die
# sich durch Entfernen ihres Ankers abschalten laesst, ist keine Regel.
# Jetzt ist ein fehlender Anker selbst ein Problem - und ein mehrfacher auch,
# denn dann liegt das Fenster irgendwo.
def kern(anker, wer, vor_, nach_, muss, flach=False):
    n = I.count(anker)
    if n == 0:
        pr.append('%s: die Stelle ist weg – Anker "%s" nicht gefunden'
                  % (wer, anker[:50]))
        return
    if n > 1:
        pr.append('%s: der Anker "%s" kommt %dx vor – Fenster beliebig'
                  % (wer, anker[:50], n))
        return
    i = I.find(anker)
    u = I[max(0, i - vor_):i + nach_]
    if flach:
        u = u.replace('<b>', '').replace('</b>', '').replace('<i>', '').replace('</i>', '')
    for muster, warum in muss:
        if muster not in u:
            pr.append('%s: %s fehlt' % (wer, warum))

# Die Antioxidans-Stelle darf ihr Argument nicht verlieren: Geprueft ist die
# HAUT, nicht das Geschluckte. Faellt dieser Halbsatz weg, liest die Stelle
# wie ein Beleg fuer den Satz auf der Flasche - das waere schlimmer als die
# alte zu strenge Verneinung.
# Die FAAH-Bilanz muss die Ausnahme weiter nennen UND einordnen - sonst wird
# aus der Korrektur ein Erfolgsversprechen.
kern('sie braucht eine Ausnahme', 'FAAH-Bilanz', 400, 2000, [
    ('nur Männer', 'dass nur Männer geprüft wurden'),
    ('unveröffentlicht', 'dass die größere Wiederholung unveröffentlicht ist'),
    ('schärfer', 'die Einordnung, dass das Muster dadurch härter wird'),
    ('[[30528676]]', 'der Beleg der Ausnahme')])

# Und die ME/CFS-Stelle muss die Maus als Maus benennen.
kern('Bis zum 28.11.2026 stand hier als Begründung', 'ME/CFS', 400, 2600, [
    ('Mausmodell des Golfkriegs-Syndroms', 'dass es ein Mausmodell ist'),
    ('kein Grund, sie für den Menschen zu glauben', 'die Grenze zum Menschen'),
    ('nicht die Aussage, sondern ihr Beleg', 'die Offenlegung des Fehlertyps'),
    ('[[39241906]]', 'der Beleg des Tierbefunds')])

kern('[[39025264]]', 'Antioxidans-Anspruch', 1600, 1600, [
    ('nicht das Geschluckte', 'der Hinweis, dass die Haut geprüft wurde'),
    ('weiter ungeprüft', 'dass der Anspruch für das Produkt offen bleibt'),
    ('Vorstudie', 'dass es eine Vorstudie ist')], flach=True)

# Und die PPAR-alpha-Stelle muss weiter Wirkung von Weg trennen.
# Nicht 'menschlichen Zelllinie': die Seite schreibt 'Darmzelllinie'. Geprueft
# wird deshalb die Aussage selbst - dass die Mechanismusarbeit aus menschlichen
# Zellen stammt und nicht aus Maeusen. Das war der dritte Teil der alten,
# falschen Behauptung.
kern('[[31054246]]', 'PPAR-α', 1200, 1200, [
    ('eine Wirkung, nicht der Weg', 'die Trennung von Wirkung und Weg'),
    ('sondern aus menschlichen Zellen',
     'dass der Weg in menschlichen Zellen gezeigt ist, nicht in Mäusen')],
     flach=True)

kern('[[28610718]]', 'Echinacea', 1500, 1500, [
    ('nicht der Weg', 'der Unterschied zwischen Nutzen und Weg'),
    ('nicht der Rezeptor', 'der Hinweis, dass Haut gemessen wurde'),
    ('Herstellerfirma', 'der Interessenkonflikt der Autoren'),
    ('21092239', 'der Zellversuch, in dem der Effekt nicht über CB2 lief')])

# --- 5) Ein Einzelbefund darf nicht ohne seine Gegenprobe stehen ---------
# Am 23.11.2026 stand auf der Seite: eine Einzeldosis senkte Tics, und die
# groessere Studie sei "weder veroeffentlicht noch berichtet". Die
# Veroeffentlichung gab es seit 2021 - mit umgekehrtem Ergebnis, zugunsten von
# Placebo. Der Leser nahm mit: vielversprechend, niemand hat nachgesehen. In
# Wahrheit hatte jemand zwoelf Wochen lang nachgesehen.
#
# Das ist die Schwester der veralteten Verneinung: ein frueher Befund, dessen
# Widerlegung fehlt. Darum die Regel: Wo der Einzeldosis-Befund zitiert wird,
# muss die zwoelfwoechige Studie im selben Atemzug stehen - und mit ihrer
# RICHTUNG, nicht nur mit ihrer Nummer.
EINZEL, GROSS = '34847610', '34117788'
stellen = [m.start() for m in re.finditer(r'\[\[%s\]\]' % EINZEL, I)]
if not stellen:
    pr.append('Der Tourette-Einzeldosis-Befund (%s) ist nicht mehr zitiert' % EINZEL)
for i in stellen:
    if GROSS not in I[max(0, i - 200):i + 700]:
        pr.append('Einzeldosis-Befund ohne die zwölfwöchige Studie: …%s…'
                  % re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', I[max(0, i - 110):i + 150])))
for i in [m.start() for m in re.finditer(r'\[\[%s\]\]' % GROSS, I)]:
    umfeld = I[max(0, i - 700):i + 120]
    if 'zugunsten von Placebo' not in umfeld and 'negativ' not in umfeld:
        pr.append('Die zwölfwöchige Studie wird ohne ihre Richtung zitiert')
# ... und die Seite darf sie nirgends wieder als unveroeffentlicht fuehren
j = I.find('NCT03625453')
if j < 0:
    pr.append('NCT03625453 ist nicht mehr genannt')
else:
    umfeld = I[max(0, j - 1200):j + 600]
    for schlecht in ['unveröffentlicht', 'nie veröffentlicht', 'keine Veröffentlichung',
                     'weder eine Veröffentlichung']:
        if schlecht in umfeld:
            pr.append('NCT03625453 gilt wieder als unveröffentlicht ("%s") – '
                      'die Arbeit ist 2021 erschienen' % schlecht)

# --- 6) Das unberichtete Programm: Summe und Einordnung ------------------
# Am 23.11.2026 dazugekommen. Zwei Dinge koennen hier verrotten, ohne dass
# jemand die Seite anfasst:
#   a) Die handgeschriebene Summe. Steht einmal eine Zahl mehr oder weniger in
#      der Liste, stimmt sie nicht mehr. Darum wird sie nachgerechnet und nicht
#      nur gesucht - dieselbe Lehre wie bei den vier veralteten Zahlen im
#      Aenderungsprotokoll.
#   b) Die Einordnung. Diese vier Studien sind NICHT gescheitert, sie sind nie
#      berichtet. Wer das zu "gescheitert" verkuerzt, macht aus Schweigen einen
#      Befund - genau der Fehler, den die Seite an anderer Stelle anprangert.
j = I.find('Ein ganzes Programm')
if j < 0:
    pr.append('Der Abschnitt über das unberichtete Rimonabant-Programm ist weg')
else:
    block = I[j:j + 6000]
    for nct in ['NCT00325650', 'NCT00481975', 'NCT00576667', 'NCT00380302']:
        if block.count(nct) != 1:
            pr.append('%s steht %dx im Abschnitt (erwartet 1x)'
                      % (nct, block.count(nct)))
    # Die Summe nachrechnen: die Teilnehmerzahlen stehen in den <dt>-Zeilen
    teil = [int(x) for x in re.findall(r'·\s*(\d{2,5}) Menschen</dt>', block)]
    summe = re.search(r'Das sind ([\d  ]+) Menschen', block)
    if len(teil) != 4:
        pr.append('%d Teilnehmerzahlen im Abschnitt gefunden (erwartet 4): %s'
                  % (len(teil), teil))
    elif not summe:
        pr.append('die Summe steht nicht mehr im Abschnitt')
    else:
        gesagt = int(re.sub(r'\D', '', summe.group(1)))
        if gesagt != sum(teil):
            pr.append('Summe stimmt nicht: Seite sagt %d, die vier Zahlen '
                      'ergeben %d (%s)' % (gesagt, sum(teil), teil))
    # Schweigen darf nicht zu einem Befund werden
    for schlecht in ['vier gescheiterten', 'sind gescheitert',
                     'es gibt keine Studie', 'wurde nie untersucht']:
        if schlecht in block:
            pr.append('das unberichtete Programm wird als Befund dargestellt: '
                      '"%s"' % schlecht)
    # Und die beiden Einschraenkungen muessen stehenbleiben
    for muss in ['nennt das Register nicht', 'PubMed']:
        if muss not in block:
            pr.append('Einschränkung fehlt im Abschnitt: ' + muss)

print('Verneinungen mit Beleg und Datum geprüft: %d' % len(FEST))
print('Einmal versagte Verneinungen, die bewacht werden: %d' % len(VERSAGT))
print('Einzelbefunde mit Pflicht-Gegenprobe: 1 (Tourette, %d Fundstellen)'
      % len(stellen))
for tag in sorted(NACHGESEHEN):
    print('Am %s nachgesehen: %d Dinge' % (tag, len(NACHGESEHEN[tag])))
print('Abfragen geprüft: 3 | Stempel im Text: %d (Tage: %s)'
      % (heute, ', '.join(gefunden)))
print('Probleme:', pr or 'keine')
if pr:
    sys.exit(1)
