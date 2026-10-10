#!/usr/bin/env python3
"""Build the award ledger straight from DOE's award-information PDFs.

Reads every PDF in data/raw/doe_awards/, pulls the RFP number, the award date,
the barrels offered, the sheet's own stated total, and one line per contract.
Each sheet must add up to its stated total or the build stops. Company names
are kept exactly as DOE listed them; data/reference/company_map.csv supplies
the merged name and the firm type.

Writes data/processed/spr_2026_exchange_awards.csv. To add a round, drop the
new award PDF in data/raw/doe_awards/, add any new company spelling to
company_map.csv, add the round to data/reference/rounds.csv, and re-run.
"""
import csv, datetime, re, sys, urllib.parse
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
PDFS = ROOT / "data" / "raw" / "doe_awards"
REF = ROOT / "data" / "reference"
OUT = ROOT / "data" / "processed" / "spr_2026_exchange_awards.csv"
ARCHIVE = "https://www.spr.doe.gov/posting/EXCHANGE/archive/"
COLS = ["round", "rfp_no", "award_date", "offered_bbl", "company_as_listed", "company",
        "type", "barrels", "source_pdf", "source_url"]


def parse(pdf):
    text = "\n".join(p.extract_text() for p in PdfReader(pdf).pages)
    text = re.sub(r"[ \t]+", " ", text)
    release = re.search(r"(FY\d\d SPR Oil Release No\. [\w.]+?) Award Information", pdf.name).group(1)
    rnd = release.split("No. ")[1]
    rfp = re.search(r"RFP NO\. (DE-RP96-\d\dPO\d{5})", text).group(1)
    offered = float(re.search(r"UP TO ([\d.]+) MILLION BARRELS", text).group(1)) * 1e6
    date = datetime.datetime.strptime(re.search(r"As of (\w+ \d+, \d{4})", text).group(1), "%B %d, %Y").date()
    stated = int(re.search(r"exchange of\s+([\d,]+)\s+barrels", text).group(1).replace(",", ""))
    lines = re.findall(r"^ ?(.+?) ?[–-] ?([\d,]+) barrels ?$", text, flags=re.M)
    awards = [(name.strip(), int(n.replace(",", ""))) for name, n in lines]
    if sum(n for _, n in awards) != stated:
        sys.exit(f"{pdf.name}: lines add to {sum(n for _, n in awards):,}, sheet says {stated:,}")
    url = ARCHIVE + urllib.parse.quote(f"{release}/1-Request for Proposal/{pdf.name}")
    return [dict(round=rnd, rfp_no=rfp, award_date=date.isoformat(), offered_bbl=int(offered),
                 company_as_listed=name, barrels=n, source_pdf=pdf.name, source_url=url)
            for name, n in awards], stated


def main():
    cmap = {r["company_as_listed"]: r for r in csv.DictReader((REF / "company_map.csv").open())}
    rows, seen = [], set()
    for pdf in sorted(PDFS.glob("*Award Information.pdf")):
        awards, stated = parse(pdf)
        for a in awards:
            key = (a["round"], a["company_as_listed"])
            if key in seen:
                sys.exit(f"duplicate key {key}")  # hard failure by house rule
            seen.add(key)
            if a["company_as_listed"] not in cmap:
                sys.exit(f"'{a['company_as_listed']}' is not in company_map.csv")
            a["company"] = cmap[a["company_as_listed"]]["company"]
            a["type"] = cmap[a["company_as_listed"]]["type"]
            rows.append(a)
        print(f"{pdf.name}: {len(awards)} contracts, {stated:,} barrels, ties to the sheet's total")
    rows.sort(key=lambda r: (r["award_date"], r["company_as_listed"]))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} contracts, {sum(r['barrels'] for r in rows):,} barrels")


if __name__ == "__main__":
    main()
