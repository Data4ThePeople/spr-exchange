#!/usr/bin/env python3
"""Check and build the catalogue of changes to the 2021-22 loan agreements.

Each of the 30 modification PDFs in data/raw/doe_foia_2022/ was read (through
the recognized text in data/processed/doe_foia_2022_text/) and keyed by hand
into data/reference/exchange_2021_22_mods.csv: the agreement, the date DOE
signed, the kind of change, any new return window and guarantee date, a plain
description, and a short phrase copied from the document.

This script stops unless every modification file has exactly one row, every
check phrase is found in that file's text, and every date and barrel count
written in a row's new return window and description is also in the text
(ignoring punctuation and spacing, which text recognition gets wrong). It then
writes data/processed/spr_2021_22_exchange_mods.csv and prints a summary.
"""
import csv, datetime, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = ROOT / "data/processed/doe_foia_2022_text"
OUT = ROOT / "data/processed/spr_2021_22_exchange_mods.csv"
MONTHS = "January February March April May June July August September October November December".split()


def loose(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())


def main():
    rows = list(csv.DictReader((ROOT / "data/reference/exchange_2021_22_mods.csv").open()))
    files = {p.stem for p in TEXT.glob("*Mod*.txt")}
    keyed = [r["file"] for r in rows]
    if len(set(keyed)) != len(keyed):
        sys.exit("a modification file is keyed twice")   # hard failure by house rule
    if set(keyed) != files:
        sys.exit(f"files and rows differ: {sorted(files ^ set(keyed))}")
    for r in rows:
        text = loose((TEXT / f"{r['file']}.txt").read_text())
        if loose(r["check_phrase"]) not in text:
            sys.exit(f"{r['file']}: check phrase not found")
        # every barrel count and every "Month D, YYYY" date in the description must be in the document
        for item in re.findall(r"\d{1,3}(?:,\d{3})+", r["what_changed"]) + \
                re.findall(r"(?:%s) \d{1,2}, \d{4}" % "|".join(MONTHS), r["what_changed"]):
            num = re.fullmatch(r"(\w+) (\d{1,2}), (\d{4})", item)
            forms = [item]
            if num:      # dates also appear as 9/27/24, 9/27/2024 or 2024.10.25
                m, d, y = MONTHS.index(num.group(1)) + 1, int(num.group(2)), num.group(3)
                forms += [f"{m}/{d}/{y}", f"{m}/{d}/{y[2:]}", f"{m:02d}/{d:02d}/{y}", f"{y}.{m:02d}.{d:02d}", f"{d} {num.group(1)} {y}"]
            if not any(loose(f) in text for f in forms):
                sys.exit(f"{r['file']}: '{item}' in the description is not in the document text")
        if r["doe_signed"]:
            datetime.date.fromisoformat(r["doe_signed"])
    rows.sort(key=lambda r: (r["doe_signed"] or "9999", r["agreement_no"], r["mod_no"]))
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    kinds = {}
    for r in rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} modifications, every one checked against its document")
    print("  " + ", ".join(f"{k}: {v}" for k, v in sorted(kinds.items(), key=lambda x: -x[1])))
    moved = [r for r in rows if r["kind"] == "Return date moved"]
    print(f"  return dates moved: {len(moved)} changes on {len({r['agreement_no'] for r in moved})} agreements, "
          f"{len({r['company'] for r in moved})} companies; {sum(1 for r in moved if '2026' in r['new_return_window'])} set a window in 2026")
    for r in moved:
        if "2026" in r["new_return_window"]:
            print(f"    {r['doe_signed'] or 'undated':10s} {r['agreement_no']:18s} {r['company']:45s} {r['new_return_window']}")


if __name__ == "__main__":
    main()
