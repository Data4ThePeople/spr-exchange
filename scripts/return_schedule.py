#!/usr/bin/env python3
"""Bound when the borrowed barrels are due back, from the RFP return windows.

DOE publishes how many barrels each firm won per round, but not which lot
(site and pickup month) or which return window each firm chose. So the return
schedule can only be bounded:

  earliest  every awarded barrel sits in the lot whose first window opens
            soonest, and comes back the day that window opens
  latest    every awarded barrel sits in the lot whose last window closes
            latest, and comes back the day that window closes

Within a round, barrels are placed lot by lot up to each lot's offered volume,
so neither bound puts more oil in a lot than DOE offered there. Premium
barrels are not counted; only the barrels lent.

Inputs   data/reference/rfp_terms.csv, data/processed/spr_2026_exchange_awards.csv
Output   data/processed/return_schedule.csv   (scenario, round, date, barrels)
"""
import calendar, csv, datetime, re, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from trade_math import MONTHS, windows

ROOT = Path(__file__).resolve().parent.parent


def span(text):
    """First day the lot's earliest window opens, last day its latest window closes."""
    m = re.fullmatch(r"(\w{3}) (\d+) (\d{4}) to (\w{3}) (\d+) (\d{4})", text)
    if m:   # round 1 gives one continuous window with exact days
        a, da, ya, b, db, yb = m.groups()
        return (datetime.date(int(ya), MONTHS.index(a) + 1, int(da)),
                datetime.date(int(yb), MONTHS.index(b) + 1, int(db)))
    months = sorted(mm for _, ms, _ in windows(text) for mm in ms)
    (y0, m0), (y1, m1) = (map(int, months[0].split("-")), map(int, months[-1].split("-")))
    return datetime.date(y0, m0, 1), datetime.date(y1, m1, calendar.monthrange(y1, m1)[1])


def main():
    lots = defaultdict(list)
    for r in csv.DictReader((ROOT / "data/reference/rfp_terms.csv").open()):
        first, last = span(r["return_options"])
        lots[r["round"]].append(dict(cap=int(r["offered_bbl"]), first=first, last=last))
    awarded = defaultdict(int)
    for r in csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open()):
        awarded[r["round"]] += int(r["barrels"])

    rows = []
    for rnd, total in awarded.items():
        if sum(l["cap"] for l in lots[rnd]) < total:
            sys.exit(f"round {rnd}: awarded more than the lots in rfp_terms.csv offer")
        for scenario, key, order in (("earliest", "first", False), ("latest", "last", True)):
            left, by_date = total, defaultdict(int)
            for lot in sorted(lots[rnd], key=lambda l: l[key], reverse=order):
                take = min(left, lot["cap"])
                if take:
                    by_date[lot[key]] += take
                left -= take
            rows += [dict(scenario=scenario, round=rnd, date=d.isoformat(), barrels=n) for d, n in by_date.items()]
    rows.sort(key=lambda r: (r["scenario"], r["date"], r["round"]))
    keys = [(r["scenario"], r["round"], r["date"]) for r in rows]
    if len(set(keys)) != len(keys):
        sys.exit("duplicate scenario, round and date")   # hard failure by house rule
    out = ROOT / "data/processed/return_schedule.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for scenario in ("earliest", "latest"):
        s = [r for r in rows if r["scenario"] == scenario]
        if sum(r["barrels"] for r in s) != sum(awarded.values()):
            sys.exit(f"{scenario}: barrels do not add to the ledger total")
        print(scenario, "| " + "; ".join(
            f"by end {y}: {sum(r['barrels'] for r in s if r['date'] <= f'{y}-12-31') / 1e6:.2f}M" for y in (2026, 2027, 2028, 2029)))
    print(f"wrote {out.relative_to(ROOT)}: {len(rows)} rows, {sum(awarded.values()):,} barrels per scenario")


if __name__ == "__main__":
    main()
