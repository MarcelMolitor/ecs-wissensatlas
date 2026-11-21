# Pruefsuite des ECS-Wissensatlas

111 Tests, die `index.html` zusammenhalten. Sie sind der Grund, warum die Seite
631 Quellen tragen kann, ohne dass sich Angaben widersprechen.

## Laufen lassen

```bash
bash tests/run-all.sh
```

Das kopiert `index.html` nach `tests/page.html` und laeuft alle 111 Tests dagegen.
Rueckgabewert 0 heisst: keiner hat etwas gemeldet. Dauer: etwa 20 bis 30 Minuten.

Eine andere Datei pruefen:

```bash
bash tests/run-all.sh /pfad/zur/fassung.html
```

Einen einzelnen Test:

```bash
cp index.html tests/page.html
python3 tests/wirkstufe.py
```

### Chromium

88 der Tests steuern einen Browser. Sie nehmen in dieser Reihenfolge:

1. `$CHROME_PATH`, wenn gesetzt
2. den Pfad der Bauumgebung, wenn er existiert
3. sonst `None` — dann nimmt Playwright sein eigenes mitgeliefertes Chromium

Es ist also nichts einzustellen, solange Playwright installiert ist:

```bash
pip install playwright && playwright install chromium
```

## Der Vertrag

**Die Tests lesen `tests/page.html`, niemals die Arbeitsdatei.**

Das ist keine Kosmetik. Im November 2026 lasen 22 Tests eine Woche lang die
Arbeitsdatei statt der geprueften Fassung. Sie waren gruen, waehrend die
veroeffentlichte Seite den Fehler trug. Ein falsch gruener Test ist schlimmer als
ein fehlender: der fehlende laesst eine Luecke, der falsch gruene behauptet
Schutz, den es nicht gibt.

Derselbe Fehler steckte in `websweep.py`, das eine Woche gegen eine Datei vom
7. November lief: 431 Quellen statt 601, 24 Reiter statt 28.

Darum gilt: wer einen Test anfasst, prueft nach, **gegen welche Datei er laeuft**,
und ob er einen echten Fehler noch findet. Ein Test, der nie rot war, ist nicht
bewiesen.

### Und niemand schreibt in die Pruefkopie

Am 21.11.2026 kam derselbe Fehler aus der anderen Richtung zurueck. `run.py`
packt die Seite zum Pruefen in eine zweite HTML-Huelle und schiebt ihr eine
Attrappe fuer `window.claude` unter, damit die Registerabfragen gefaelscht
antworten. Dieses Ergebnis schrieb es nach `tests/page.html` zurueck und stellte
die Datei nie wieder her. Die 20 Tests, die alphabetisch nach `run.py` laufen,
prueften damit nicht die Seite, sondern die praeparierte Fassung - darunter die
Sprung- und Scrollpruefungen, also genau die, die eine zusaetzliche
Dokumenthuelle stoeren kann. Aufgefallen ist es nur, weil `page.html` nach einem
Lauf 7160 Byte groesser war als der Pruefling.

Wer einen Test braucht, der die Seite veraendert, gibt ihm **eine eigene Datei**
und raeumt sie hinterher weg. Die Probe dafuer ist billig: Pruefsumme von
`page.html` vor und nach dem Lauf vergleichen.

### Ein Test, der meldet, muss auch rot werden koennen

Am selben Tag meldete `verwandt.py` zwei Probleme und zaehlte trotzdem gruen.
Seine Zeile lautet `Faelle: 12 | Probleme: [...] | Konsole: keine` und beginnt
weder mit `FEHLER` noch mit `FEHLT` - also griff keine Regel des Laeufers. Die
Suite sagte "alle gruen", waehrend ein Test widersprach.

`run-all.sh` kennt dafuer jetzt Regel 5. Aber die Lehre ist allgemeiner: Die
Suite ist uneinheitlich (61 zusichernde, 45 berichtende Tests), und ein
berichtender Test ist nur so viel wert, wie der Laeufer von ihm mitbekommt.
Wer einen neuen Test schreibt, der etwas bloss druckt, prueft nach, **ob der
Laeufer diese Druckform ueberhaupt als Fehler erkennt**.

## Was die Suite leistet - und was nicht

| | Zahl | heisst |
|---|---|---|
| Tests mit Rueckgabewert | 59 | melden selbst, maschinell pruefbar |
| nur berichtende Tests | 52 | drucken Befunde, die gelesen werden muessen |
| davon mit JS-Fehlersammlung | 28 | drucken Seitenfehler, ohne zu scheitern |

Gezaehlt am 21.11.2026 so, und damit nachrechenbar: `ls tests/*.py | wc -l` fuer
die Gesamtzahl, `grep -l 'sys.exit(1)' tests/*.py | wc -l` fuer die mit
Rueckgabewert, `grep -L async_playwright tests/*.py` fuer die ohne Browser. Die
Zahlen standen vorher auf 107/106/94 und 61/45 - drei verschiedene Gesamtzahlen
in einer Datei. Am selben Tag habe ich 59/51 geraten statt gezaehlt und es
wieder richtiggestellt; darum stehen die Befehle hier. Wer eine davon aendert, rechnet die anderen mit nach.

Die 52 berichtenden Tests sind **keine** Durchfallpruefungen. Sie drucken Zahlen
und Textstellen, die ein Mensch oder ein Agent beurteilen muss. `run-all.sh`
schliesst eine Luecke davon selbst: es nennt jeden Test rot, dessen Ausgabe eine
nicht leere JavaScript-Fehlerliste enthaelt. Diese Pruefung liegt im Laeufer, nicht
in den Tests.

Ein gruener Lauf heisst also: keine abgestuerzte Seite, keine verletzte Zusicherung,
kein JavaScript-Fehler. Er heisst **nicht**, dass die 45 Berichte in Ordnung sind.
Wer `run-all.sh` laufen laesst, liest `tests/lauf.log` trotzdem durch.

## Was die Tests pruefen

Grob vier Gruppen:

- **Belege.** Jede Angabe mit Evidenzstufe braucht eine PMID oder eine
  NCT-Nummer. `organbelege.py` zaehlt die Felder ohne Quelle und kennt eine
  Obergrenze. Die Obergrenze wird nicht angehoben, wenn ein neuer Stoff sie
  reisst — dann fehlen Belege, nicht Spielraum.
- **Die eigene Legendenregel.** Befunde nur aus Tier- oder Zellversuch erreichen
  hoechstens „schwache Wirkung". `wirkstufe.py` prueft das gegen die Quellentypen,
  nicht gegen eine Liste von Feldern — die alte Fassung tat Letzteres und liess
  neun Verstoesse durch.
- **Verdrahtung.** Ein neuer Stoff braucht sechs Eintragungen (`SUBS`, `COL`,
  `PERM`, Legendennamen, Formregel, Querverweis). Fehlt eine, ist er zwar da,
  aber nicht erreichbar. Ebenso: jeder Reiter muss in `KNOW` **und** in `GROUPS`
  stehen, sonst kommt man mit der Maus nicht hin.
- **Darstellung.** Kein Ueberlauf, kein Kontrastbruch, keine toten Glossarlinks,
  keine Suchfelder, die etwas anderes tun als angeschrieben.

## Ausgelassen

Drei Tests aus der Entwicklungsumgebung sind hier nicht dabei:
`parity.py`, `visual.py`, `webvisual.py`. Sie verglichen die Seite gegen eine
Netlify-Kopie vom 7. November. Netlify wird nicht mehr benutzt, die Kopie ist
veraltet — die Tests wuerden gegen eine Datei pruefen, die es nicht mehr gibt.

## Fuer Agenten

Wer die Seite aendert und veroeffentlicht, laeuft vorher `bash tests/run-all.sh`
und veroeffentlicht nicht bei Rueckgabewert 1. Das gilt auch fuer kleine
Aenderungen: die meisten Fehler dieses Projekts entstanden nicht beim Hinzufuegen,
sondern dadurch, dass das Hinzugefuegte dem widersprach, was schon auf der Seite
stand — achtmal hat eine neue Angabe einer bestehenden widersprochen.

Zwei weitere Regeln aus Schaden:

- **Einen Satz nie ohne seine Karte beurteilen.** Vier Fehlalarme entstanden, weil
  ein mit Suchmuster herausgezogener Satz falsch wirkte, waehrend die Ueberschrift
  darueber ihn richtig einordnete.
- **Eine Zusicherung kann einfach veralten.** „Nie am Menschen geprueft" war bei
  einem dualen FAAH/MAGL-Hemmer richtig, als es geschrieben wurde, und falsch,
  als es jemand nachsah: drei Phase-2-Studien. Behauptungen dieser Art gehoeren
  regelmaessig gegen ClinicalTrials.gov geprueft.
