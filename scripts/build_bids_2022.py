#!/usr/bin/env python3
"""Every offer in the 2022 emergency sales, winners and losers.

DOE's "Offeror Abstract Report" for each sale has one page per offer: the
offeror and, for each master line item (MLI), the most oil the offer would
take ("MAXQ") and one or more delivery choices with a price each. This reads
the seven reports in data/raw/doe_sales_2022/ and writes one row per offer and
MLI to data/processed/spr_2022_sale_offers.csv.

"Barrels bid" is MAXQ. A company often files several offers for the same oil
at different prices, so barrels bid add up to more than a company wanted. Use
it to see who showed up and how often they won, not as a measure of demand.
The awarded column comes from data/processed/spr_2022_sale_awards.csv, matched
on offer number and MLI.
"""
import csv, re, sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/doe_sales_2022"
OUT = ROOT / "data/processed/spr_2022_sale_offers.csv"
COLS = ["sale", "offer_no", "company_as_listed", "company", "type", "mli", "barrels_bid",
        "low_price", "high_price", "barrels_awarded", "source_pdf"]
FIRST = re.compile(r"^(\d{3}) (?:([\d,]+) )?[A-Z] \d+ \$([\d.,]+) ([\d,]+) \$")   # MLI, MAXQ (sometimes blank), DLI, PRE, price, DESQ
MORE = re.compile(r"^[A-Z] \d+ \$([\d.,]+) ([\d,]+) \$")              # another delivery choice for the same MLI


def main():
    cmap = {r["company_as_listed"]: r for r in csv.DictReader((ROOT / "data/reference/company_map.csv").open())}
    won = {}
    for r in csv.DictReader((ROOT / "data/processed/spr_2022_sale_awards.csv").open()):
        key = (r["sale"], r["offer_no"], r["mli"])
        won[key] = won.get(key, 0) + int(r["barrels"])
    rows, seen = [], set()
    for pdf in sorted(RAW.glob("*Offeror Abstract Report.pdf")):
        for page in PdfReader(pdf).pages:
            lines = [l.strip() for l in page.extract_text().splitlines()]
            start = next((i for i, l in enumerate(lines) if l.startswith("OFR# OFFEROR INFORMATION")), None)
            if start is None:
                continue
            sale = next(l for l in lines if l.startswith("SALES CYCLE:")).split(":", 1)[1].strip()
            offer_no, name = lines[start + 1].split(" ", 1)
            name = name.strip()
            if name not in cmap:
                sys.exit(f"'{name}' is not in company_map.csv")
            cur = None
            for l in lines[start:]:
                m = FIRST.match(l)
                if m:
                    key = (sale, offer_no, m.group(1))
                    if key in seen:
                        sys.exit(f"duplicate key {key}")   # hard failure by house rule
                    seen.add(key)
                    price = float(m.group(3).replace(",", ""))
                    cur = dict(sale=sale, offer_no=offer_no, company_as_listed=name, company=cmap[name]["company"],
                               type=cmap[name]["type"], mli=m.group(1), maxq=m.group(2),
                               barrels_bid=int((m.group(2) or m.group(4)).replace(",", "")) * 1000,
                               low_price=price, high_price=price, barrels_awarded=won.get(key, 0), source_pdf=pdf.name)
                    rows.append(cur)
                elif cur and MORE.match(l):
                    price = float(MORE.match(l).group(1).replace(",", ""))
                    cur["low_price"], cur["high_price"] = min(cur["low_price"], price), max(cur["high_price"], price)
                    if not cur["maxq"]:     # no MAXQ printed: take the largest quantity asked for on any delivery choice
                        cur["barrels_bid"] = max(cur["barrels_bid"], int(MORE.match(l).group(2).replace(",", "")) * 1000)
            if cur is None:
                sys.exit(f"{pdf.name} offer {offer_no}: no line items read")
    matched = sum(r["barrels_awarded"] for r in rows)
    if matched != sum(won.values()):
        sys.exit(f"awards matched to offers: {matched:,}; awards in the ledger: {sum(won.values()):,}")
    over = [r for r in rows if r["barrels_awarded"] > r["barrels_bid"]]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} offer lines, {len({(r['sale'], r['offer_no']) for r in rows})} offers, "
          f"{len({r['company'] for r in rows})} bidders, {sum(r['barrels_bid'] for r in rows):,} barrels bid, "
          f"{matched:,} awarded (every award matched to an offer); {len(over)} lines awarded more than MAXQ")
    types = {}
    for r in rows:
        t = types.setdefault(r["type"], [0, 0, set()])
        t[0] += r["barrels_bid"]; t[1] += r["barrels_awarded"]; t[2].add(r["company"])
    bid = sum(t[0] for t in types.values())
    for k, (b, a, names) in sorted(types.items(), key=lambda x: -x[1][0]):
        print(f"  {k}: {len(names)} bidders, bid {b:,} ({b / bid * 100:.1f}% of barrels bid), won {a:,} ({a / b * 100:.1f}% of what they bid)")


if __name__ == "__main__":
    main()
