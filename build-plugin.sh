#!/usr/bin/env bash
# Buduje artefakty wydania:
#   cykl-lifecycle.plugin              — paczka dla Claude Cowork (przeciągasz do rozmowy)
#   cykl-lifecycle-skills.zip          — 7 skilli do rozpakowania wprost w katalogu skilli
#
# DLACZEGO ten skrypt istnieje: paczka .plugin zawiera WŁASNĄ KOPIĘ całego skills/
# oraz manifestu. Kto instaluje z .plugin, dostaje treść z paczki, nie z repozytorium.
# Zapomniana przebudowa = wydanie, w którym zmiana nie dociera do nikogo
# instalującego przez Cowork. Zdarzyło się raz: paczka wiozła skille o dwie
# wersje starsze niż repo.
#
# Uruchom z katalogu głównego repo:  ./build-plugin.sh

set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

OUT="cykl-lifecycle.plugin"
SKILLS_ZIP="cykl-lifecycle-skills.zip"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# 1. Staging — dokładnie to, co ma trafić do paczki
mkdir -p "$STAGE/.claude-plugin"
cp packaging/plugin-README.md "$STAGE/README.md"   # UWAGA: inny plik niż README.md repo
cp .claude-plugin/plugin.json "$STAGE/.claude-plugin/plugin.json"
cp -R skills "$STAGE/skills"
find "$STAGE" -name '.DS_Store' -delete

# 2. Pakowanie (-X = bez atrybutów systemu plików, powtarzalny wynik)
rm -f "$OUT"
( cd "$STAGE" && zip -r -q -X "$ROOT/$OUT" README.md .claude-plugin skills )

# 3. Weryfikacja — paczka bez tego kroku jest nieodróżnialna od zepsutej
VERIFY="$(mktemp -d)"
trap 'rm -rf "$STAGE" "$VERIFY"' EXIT
unzip -tq "$OUT"
unzip -q "$OUT" -d "$VERIFY"

manifest_ver="$(grep -o '"version": *"[^"]*"' "$VERIFY/.claude-plugin/plugin.json" | head -1)"
markers="$(grep -rh 'cykl-lifecycle v' "$VERIFY/skills" --include='SKILL.md' | sort -u)"
marker_count="$(printf '%s\n' "$markers" | grep -c . || true)"

diff -r "$VERIFY/skills" skills > /dev/null \
  || { echo "BŁĄD: skills/ w paczce różni się od repo"; exit 1; }

[ "$marker_count" -eq 1 ] \
  || { echo "BŁĄD: niejednolite markery wersji w paczce:"; printf '%s\n' "$markers"; exit 1; }

echo "OK  $OUT"
echo "    manifest : $manifest_ver"
echo "    markery  : $markers"
echo "    wpisów   : $(unzip -l "$OUT" | tail -1 | awk '{print $2}')"
echo "    skills/  : identyczne z repo"

# 3b. Osobne zipy per skill — aplikacja Claude / Cowork importuje JEDEN skill z JEDNEGO zipa
#     (korzeń archiwum = folder skilla). Zbiorczy zip niżej służy tylko instalacji w terminalu.
mkdir -p dist && rm -f dist/cykl-*.zip
for d in skills/cykl-*; do
  n="$(basename "$d")"
  ( cd skills && zip -r -q -X "$ROOT/dist/$n.zip" "$n" -x '*.DS_Store' )
  [ "$(unzip -Z1 "dist/$n.zip" | head -1)" = "$n/" ] || { echo "BŁĄD: $n.zip nie ma folderu $n/ w korzeniu"; exit 1; }
done
echo "OK  dist/cykl-*.zip ($(ls dist/cykl-*.zip | wc -l | tr -d ' ') paczek, po jednym skillu)"

# 4. Zip skilli — foldery cykl-* w KORZENIU archiwum, nie pod skills/.
#    Dzięki temu instalacja to jedna komenda bez przenoszenia plików:
#      unzip cykl-lifecycle-skills.zip -d ~/.claude/skills/     (Claude Code)
#      unzip cykl-lifecycle-skills.zip -d ~/.agents/skills/     (Codex)
rm -f "$SKILLS_ZIP"
( cd skills && zip -r -q -X "$ROOT/$SKILLS_ZIP" cykl-* )

VZ="$(mktemp -d)"
trap 'rm -rf "$STAGE" "$VERIFY" "$VZ"' EXIT
unzip -tq "$SKILLS_ZIP"
unzip -q "$SKILLS_ZIP" -d "$VZ"

# W korzeniu archiwum ma być dokładnie 7 katalogów cykl-* i ani jednego "skills"
top_dirs="$(find "$VZ" -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | sort)"
top_count="$(printf '%s\n' "$top_dirs" | grep -c '^cykl-' || true)"

[ "$top_count" -eq 7 ] \
  || { echo "BŁĄD: w korzeniu zipa ma być 7 katalogów cykl-*, jest $top_count:"; printf '%s\n' "$top_dirs"; exit 1; }

printf '%s\n' "$top_dirs" | grep -qx 'skills' \
  && { echo "BŁĄD: zip zawiera nadrzędny katalog skills/ — instalacja jedną komendą nie zadziała"; exit 1; }

for d in $top_dirs; do
  diff -r "$VZ/$d" "skills/$d" > /dev/null \
    || { echo "BŁĄD: $d w zipie różni się od repo"; exit 1; }
done

echo "OK  $SKILLS_ZIP"
echo "    katalogi : $top_count x cykl-* w korzeniu (bez nadrzędnego skills/)"
echo "    treść    : identyczna z repo"
