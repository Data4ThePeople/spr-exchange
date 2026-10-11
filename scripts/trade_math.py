#!/usr/bin/env python3
"""Worked example of the borrow, sell and hedge trade for one exchange round.

For each return window in the round's RFP: one barrel is borrowed and sold at
the front-month WTI futures close, and (1 + premium) barrels are bought back
with the WTI futures for that window (mean of the window's contract months).
Gross margin per barrel borrowed = sale price - (1 + premium) x return price.

The premium used is the RFP minimum plus the window's add-on. What each firm
actually bid is not public, so this is the most a bidder could have made, not
what any firm made. Left out: the grade's price gap to WTI, pipeline and
shipping costs, the letter of credit, and interest earned on the sale proceeds.

Inputs
  data/reference/rfp_terms.csv, data/reference/rounds.csv
  data/processed/spr_2026_exchange_awards.csv
  data/processed/futures_closes.csv        dated contracts, scripts/fetch_futures.py
  data/raw/futures/CL=F.json               front-month continuous contract, Yahoo
Output
  data/processed/trade_example.csv
"""
import csv, datetime, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROUND = sys.argv[1] if len(sys.argv) > 1 else "1.b"
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def front_month():
    res = json.loads((ROOT / "data/raw/futures/CL=F.json").read_text())
    tz = datetime.timezone(datetime.timedelta(seconds=res["meta"]["gmtoffset"]))
    return {datetime.datetime.fromtimestamp(t, tz).date().isoformat(): c
            for t, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]) if c is not None}


def windows(text):
    """'2028: Jan-Mar +0.0; Apr-Jun +0.5' -> [(label, [yyyy-mm, ...], add_on)]"""
    year, rest = re.match(r"(\d{4}): (.+)", text).groups()
    out = []
    for part in rest.split("; "):
        a, b, add = re.match(r"(\w{3})-(\w{3}) \+([\d.]+)", part).groups()
        months = [f"{year}-{m + 1:02d}" for m in range(MONTHS.index(a), MONTHS.index(b) + 1)]
        out.append((f"{a}-{b} {year}", months, float(add)))
    return out


def main():
    terms = [r for r in csv.DictReader((ROOT / "data/reference/rfp_terms.csv").open()) if r["round"] == ROUND]
    rnd = [r for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open()) if r["round"] == ROUND][0]
    if len({(r["min_premium_pct"], r["return_options"]) for r in terms}) != 1:
        sys.exit(f"round {ROUND} has more than one set of terms; this example needs one")
    base = float(terms[0]["min_premium_pct"])
    awards = [r for r in csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open()) if r["round"] == ROUND]
    total = sum(int(r["barrels"]) for r in awards)
    traders = sum(int(r["barrels"]) for r in awards if r["type"] == "Trading house")
    curve = {}
    for r in csv.DictReader((ROOT / "data/processed/futures_closes.csv").open()):
        if r["product"] == "WTI":
            if (r["date"], r["delivery"]) in curve:
                sys.exit(f"duplicate {r['date']} {r['delivery']}")   # hard failure by house rule
            curve[r["date"], r["delivery"]] = float(r["close"])
    front = front_month()

    rows = []
    for label, day in (("bids due", rnd["bids_due"]), ("award", rnd["award_date"])):
        for window, months, add in windows(terms[0]["return_options"]):
            ret = sum(curve[day, m] for m in months) / len(months)
            owed = 1 + (base + add) / 100
            margin = front[day] - owed * ret
            rows.append(dict(round=ROUND, priced_on=label, date=day, sale_price=round(front[day], 2),
                             return_window=window, premium_pct=base + add, return_price=round(ret, 2),
                             cost_to_return=round(owed * ret, 2), gross_margin_per_bbl=round(margin, 2),
                             breakeven_premium_pct=round((front[day] / ret - 1) * 100, 1),
                             trader_barrels=traders, gross_margin_traders_usd_m=round(margin * traders / 1e6)))
    out = ROOT / "data/processed/trade_example.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"round {ROUND}: {total:,} barrels awarded, {traders:,} to trading houses ({traders / total:.1%})")
    for r in rows:
        print("  {priced_on:9s} {date} sell ${sale_price:6.2f} | return {return_window}: {premium_pct}% x ${return_price} "
              "= ${cost_to_return} | margin ${gross_margin_per_bbl}/bbl, ${gross_margin_traders_usd_m}M, "
              "breakeven {breakeven_premium_pct}%".format(**r))
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
