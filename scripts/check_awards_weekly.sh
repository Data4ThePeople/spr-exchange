#!/bin/zsh
# Unattended weekly check, run by launchd (Monday at 10:30).
#   1. scripts/check_awards.py looks for a new award sheet or a new round on DOE's site.
#   2. If it finds one: the PDF is saved in data/raw/doe_awards/, a STATUS.md log
#      line is added, and both are committed and pushed.
# It does not rebuild the ledger or the charts. That takes a by-hand update of
# rounds.csv and company_map.csv first.
# A finding or a failure shows a macOS alert box; details are in logs/check_awards.log.
set -u
ROOT="${0:A:h:h}"
PY="$ROOT/.venv/bin/python3"
LOG="$ROOT/logs/check_awards.log"
mkdir -p "$ROOT/logs"
exec >>"$LOG" 2>&1
cd "$ROOT" || exit 1
echo "\n=== $(date '+%Y-%m-%d %H:%M %Z') ==="

# An alert box stays on screen until clicked; a banner notification can come
# and go unseen.
alert() {
  osascript -e "display alert \"$1\" message \"$2\" buttons {\"OK\"} default button \"OK\" giving up after 86400" >/dev/null 2>&1
}

fail() {
  echo "FAILED: $1"
  alert "SPR award check failed" "$1. Details in logs/check_awards.log."
  exit 1
}

git pull -q --rebase || fail "git pull"
out=$("$PY" scripts/check_awards.py 2>&1) || { echo "$out"; fail "DOE folder check"; }
echo "$out"
[[ "$out" == "nothing new" ]] && exit 0

line="- $(date +%F) Automatic weekly check: ${out//$'\n'/; }. Ledger and charts not rebuilt yet."
echo "$line" >> STATUS.md
git add STATUS.md data/raw/doe_awards
git commit -q -m "spr-exchange: weekly award check found something $(date +%F)" || fail "git commit"
git push -q || fail "git push"
echo "pushed: $line"
alert "SPR exchange: something new from DOE" "${out//$'\n'/; }. The ledger and charts need a rebuild."
