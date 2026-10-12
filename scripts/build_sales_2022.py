#!/usr/bin/env python3
"""Build the 2022 emergency sale ledger from DOE's Successful Awards Reports.

Reads the seven "Successful Awards Report" PDFs in data/raw/doe_sales_2022/
(scripts/fetch_doe_sales.py). Each page is one contract: the buyer, a contract
number, and one line per delivery line item with the unit price, the barrels
awarded (in thousands) and the total price. The build stops if

  - a line's price times barrels is not its total price,
  - a contract's lines do not add to its "TOTAL OFFER AWARD" line,
  - a contract number or a line key appears twice,
  - a buyer is not in data/reference/company_map.csv.

Company names are kept as DOE listed them; company_map.csv supplies the merged
name and the firm type, the same file the 2026 ledger uses.

Writes data/processed/spr_2022_sale_awards.csv, one row per line item.
Barrels are awarded volumes at the offered price. Contract prices were later
adjusted by a price index up to delivery, so these are not dollars received.
"""
import csv, datetime, json, re, sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/doe_sales_2022"
OUT = ROOT / "data/processed/spr_2022_sale_awards.csv"
COLS = ["sale", "run_date", "contract_no", "offer_no", "company_as_listed", "company", "type",
        "line", "mli", "dli", "delivery_mode", "unit_price", "barrels", "dollars", "source_pdf", "source_url"]
# A line item. The offer number shows on a contract's first line only, the MLI on
# the first line of each MLI only, and MAXQ is sometimes blank.
LINE = re.compile(r"^(?:\d{4,6} )?(?:(\d{3}) )?(?:[\d,]+ )?([A-Z]) \d+ ([A-Z]+) \$([\d.,]+) ([\d,]+) \$([\d,]+)$")
MLI_TOTAL = re.compile(r"^TOTAL MLI AWDQ ([\d,]+) TOTAL PRICE \$([\d,]+)$")
TOTAL = re.compile(r"^TOTAL OFFER AWARD ([\d,]+) TOTAL PRICE \$([\d,]+)$")


def num(s):
    return int(s.replace(",", ""))


def parse(pdf, url):
    """One contract per page. Returns the line items and {contract number: buyer}."""
    rows, contracts = [], {}
    for page in PdfReader(pdf).pages:
        lines = [l.strip() for l in page.extract_text().splitlines()]
        start = next((i for i, l in enumerate(lines) if l.startswith("OFR# OFFEROR INFORMATION")), None)
        if start is None:
            if any(LINE.match(l) for l in lines):
                sys.exit(f"{pdf.name}: a page has line items but no contract header")
            continue
        sale = next(l for l in lines if l.startswith("SALES CYCLE:")).split(":", 1)[1].rsplit(" V.", 1)[0].strip()
        run = datetime.datetime.strptime(next(l for l in lines if l.startswith("RUN DATE:")).split(":")[1].strip(), "%m/%d/%Y").date()
        offer_no, name = lines[start + 1].split(" ", 1)
        contract = next(l for l in lines if l.startswith("Contract Number:")).split(":")[1].strip()
        if contract in contracts:
            sys.exit(f"{pdf.name}: contract {contract} appears twice")   # hard failure by house rule
        got, mli, mli_bbl, mli_usd, total = [], None, 0, 0, None
        for l in lines[start:]:
            m = LINE.match(l)
            if m:
                mli = m.group(1) or mli
                if mli is None:
                    sys.exit(f"{pdf.name} contract {contract}: line item before any MLI")
                price, qty, dollars = float(m.group(4).replace(",", "")), num(m.group(5)) * 1000, num(m.group(6))
                if abs(price * qty - dollars) > 1:
                    sys.exit(f"{pdf.name} contract {contract}: ${price} x {qty:,} is not ${dollars:,}")
                got.append(dict(sale=sale, run_date=run.isoformat(), contract_no=contract, offer_no=offer_no,
                                company_as_listed=name.strip(), line=len(got) + 1, mli=mli, dli=m.group(2),
                                delivery_mode=m.group(3).title(), unit_price=price, barrels=qty, dollars=dollars,
                                source_pdf=pdf.name, source_url=url))
                mli_bbl, mli_usd = mli_bbl + qty, mli_usd + dollars
            elif MLI_TOTAL.match(l):
                want = MLI_TOTAL.match(l).groups()
                if (mli_bbl, mli_usd) != (num(want[0]) * 1000, num(want[1])):
                    sys.exit(f"{pdf.name} contract {contract} MLI {mli}: lines add to {mli_bbl:,} and ${mli_usd:,}; report says {want}")
                mli_bbl = mli_usd = 0
            elif TOTAL.match(l):
                total = TOTAL.match(l).groups()
        if total is None:
            sys.exit(f"{pdf.name} contract {contract}: no TOTAL OFFER AWARD line")
        if sum(r["barrels"] for r in got) != num(total[0]) * 1000 or sum(r["dollars"] for r in got) != num(total[1]):
            sys.exit(f"{pdf.name} contract {contract}: lines add to {sum(r['barrels'] for r in got):,} barrels and "
                     f"${sum(r['dollars'] for r in got):,}; report says {total[0]} thousand and ${total[1]}")
        rows += got
        contracts[contract] = name
    return rows, contracts


def main():
    cmap = {r["company_as_listed"]: r for r in csv.DictReader((ROOT / "data/reference/company_map.csv").open())}
    urls = {m["file"]: m["url"] for m in json.loads((RAW / "manifest.json").read_text())}
    rows, seen, all_contracts = [], set(), set()
    for pdf in sorted(RAW.glob("*Successful Awards Report.pdf")):
        got, contracts = parse(pdf, urls[pdf.name])
        if all_contracts & set(contracts):
            sys.exit(f"{pdf.name}: contract numbers repeat from an earlier sale")
        all_contracts |= set(contracts)
        for r in got:
            key = (r["contract_no"], r["line"])
            if key in seen:
                sys.exit(f"duplicate key {key}")   # hard failure by house rule
            seen.add(key)
            if r["company_as_listed"] not in cmap:
                sys.exit(f"'{r['company_as_listed']}' is not in company_map.csv")
            r["company"] = cmap[r["company_as_listed"]]["company"]
            r["type"] = cmap[r["company_as_listed"]]["type"]
        rows += got
        print(f"{got[0]['sale']} ({got[0]['run_date']}): {len(contracts)} contracts, {len({r['company'] for r in got})} buyers, "
              f"{sum(r['barrels'] for r in got):,} barrels, ${sum(r['dollars'] for r in got):,}; every contract ties to its total")
    rows.sort(key=lambda r: (r["run_date"], r["contract_no"], r["line"]))
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)
    bbl, usd = sum(r["barrels"] for r in rows), sum(r["dollars"] for r in rows)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} lines, {len(all_contracts)} contracts, "
          f"{len({r['company'] for r in rows})} buyers, {bbl:,} barrels, ${usd:,}, average ${usd / bbl:.2f}")


if __name__ == "__main__":
    main()
