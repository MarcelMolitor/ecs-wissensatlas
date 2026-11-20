#!/usr/bin/env bash
# Laeuft die ganze Pruefsuite gegen index.html.
#
#   bash tests/run-all.sh                   # prueft ../index.html
#   bash tests/run-all.sh /pfad/seite.html  # prueft eine andere Datei
#
# Rueckgabewert 0 nur, wenn kein Test etwas gemeldet hat.
set -u

HIER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRUEFLING="${1:-$HIER/../index.html}"

if [ ! -f "$PRUEFLING" ]; then
  echo "Pruefling nicht gefunden: $PRUEFLING" >&2
  exit 2
fi

# Die Tests lesen alle dieselbe Datei: tests/page.html, die Kopie des Prueflings,
# nie die Arbeitsdatei. Diese Trennung ist nicht Kosmetik - im November 2026 lasen
# 22 Tests eine Woche lang die Arbeitsdatei statt der geprueften Fassung und waren
# gruen, obwohl die Seite den Fehler trug.
cp "$PRUEFLING" "$HIER/page.html"
echo "Pruefling: $PRUEFLING"
echo "Groesse:   $(wc -c < "$HIER/page.html") Bytes"
echo

LOG="$HIER/lauf.log"
: > "$LOG"
GELAUFEN=0; GRUEN=0
FEHLER=()

for T in "$HIER"/*.py; do
  NAME="$(basename "$T")"
  GELAUFEN=$((GELAUFEN + 1))
  printf '%-24s ' "$NAME"

  AUS="$(timeout 420 python3 "$T" 2>&1)"; RC=$?
  { echo "########## $NAME (rc=$RC)"; echo "$AUS"; } >> "$LOG"

  GRUND=""
  # 1) Die 61 Tests mit Rueckgabewert melden darueber.
  [ "$RC" -ne 0 ] && GRUND="rc=$RC"
  # 2) Abbruch im Test selbst.
  [ -z "$GRUND" ] && echo "$AUS" | grep -q "^Traceback" && GRUND="Traceback"
  # 3) Meldewoerter am Zeilenanfang.
  [ -z "$GRUND" ] && echo "$AUS" | grep -qE '^(FEHLER|FEHLT|ABBRUCH)' && GRUND="Meldung"
  # 4) Die 45 nur berichtenden Tests haben keinen Rueckgabewert. 28 von ihnen
  #    sammeln JavaScript-Fehler der Seite und drucken sie bloss - eine nicht
  #    leere Liste waere sonst durchgelaufen. Diese Pruefung liegt beim Laeufer,
  #    nicht im Test, und gilt darum fuer alle 106.
  [ -z "$GRUND" ] && echo "$AUS" | grep -qE 'Fehler[^[]*\[[^]]' && GRUND="JS-Fehler auf der Seite"

  if [ -n "$GRUND" ]; then
    echo "FEHLER ($GRUND)"
    FEHLER+=("$NAME: $GRUND")
  else
    echo "ok"
    GRUEN=$((GRUEN + 1))
  fi
done

echo
echo "gelaufen: $GELAUFEN, gruen: $GRUEN"
if [ ${#FEHLER[@]} -eq 0 ]; then
  echo "alle gruen"
  exit 0
fi
echo
echo "Fehler in ${#FEHLER[@]}:"
for F in "${FEHLER[@]}"; do echo "  $F"; done
echo "Einzelheiten: $LOG"
exit 1
