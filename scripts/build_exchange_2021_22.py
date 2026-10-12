#!/usr/bin/env python3
"""Build the 2021-22 loan ledger from DOE's own agreements.

The agreements are in data/raw/doe_foia_2022/FY2022_WinterExchangeAll.pdf, from
DOE's FOIA reading room (scripts/fetch_doe_foia_2022.py). About 40% of its pages
are scans, so the text used here is from macOS text recognition
(scripts/ocr_pdf.swift -> data/processed/doe_foia_2022_text/).

The terms were keyed by hand into data/reference/exchange_2021_22.csv with the
PDF page each agreement starts on. This script checks every keyed barrel
count, premium and guarantee amount against the recognized text of that
agreement's first pages and stops if one is not there, then adds the merged
company name and firm type and writes data/processed/spr_2021_22_exchange.csv.
"""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXT = ROOT / "data/processed/doe_foia_2022_text/FY2022_WinterExchangeAll.txt"
OUT = ROOT / "data/processed/spr_2021_22_exchange.csv"
SPAN = 4    # the terms sit in an agreement's first four pages


def main():
    parts = re.split(r"=== page (\d+) ===\n", TEXT.read_text())[1:]
    pages = {int(parts[i]): " ".join(parts[i + 1].split()) for i in range(0, len(parts), 2)}
    cmap = {r["company_as_listed"]: r for r in csv.DictReader((ROOT / "data/reference/company_map.csv").open())}
    rows, seen = [], set()
    for r in csv.DictReader((ROOT / "data/reference/exchange_2021_22.csv").open()):
        if r["agreement_no"] in seen:
            sys.exit(f"duplicate agreement {r['agreement_no']}")   # hard failure by house rule
        seen.add(r["agreement_no"])
        start = int(r["page"])
        text = " ".join(pages[n] for n in range(start, start + SPAN))
        loose = re.sub(r"[^a-z0-9]", "", text.lower())          # recognition drops and swaps punctuation
        need = [r["company_as_listed"]] + re.findall(r"[\d.]+", r["premium_pct"])
        need += [f"{int(r['guarantee_usd']):,}"] if r["guarantee_usd"] else []
        if r["agreement_no"] == "DE-AC96-22PO00003":
            need += ["3,300,000", "900,000", "600,000"]          # the contract form lists line items, not a total
        else:
            need += [f"{int(r['barrels']):,}"]
        for item in need:
            if re.sub(r"[^a-z0-9]", "", item.lower()) not in loose:
                sys.exit(f"{r['agreement_no']}: '{item}' not found on pages {start} to {start + SPAN - 1}")
        if r["company_as_listed"] not in cmap:
            sys.exit(f"'{r['company_as_listed']}' is not in company_map.csv")
        rows.append(dict(r, company=cmap[r["company_as_listed"]]["company"], type=cmap[r["company_as_listed"]]["type"]))
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    total = sum(int(r["barrels"]) for r in rows)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} agreements, {len({r['company'] for r in rows})} borrowers, {total:,} barrels; "
          f"every keyed figure found in the agreement text")
    for kind in ("Sour", "Sweet"):
        sub = [r for r in rows if r["crude"] == kind]
        print(f"  {kind}: {sum(int(r['barrels']) for r in sub):,} barrels in {len(sub)} agreements")
    types = {}
    for r in rows:
        types[r["type"]] = types.get(r["type"], 0) + int(r["barrels"])
    for t, v in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {v:,} ({v / total * 100:.1f}%)")


if __name__ == "__main__":
    main()
