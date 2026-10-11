#!/usr/bin/env python3
"""Worked example of the borrow, sell and hedge trade for one exchange round.

For each lot and return window in the round's RFP: one barrel is borrowed and
sold, and (1 + premium) barrels are bought back with the WTI futures for that
window (mean of the window's contract months). Gross margin per barrel
borrowed = sale price - (1 + premium) x return price. Two sale prices are
shown: the front-month WTI futures close, and the contract for the month after
the lot's delivery month where Yahoo still serves it.

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
  data/processed/trade_example_round_<round>.csv
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


def ym(mon, year, shift=0):
    n = int(year) * 12 + MONTHS.index(mon) + shift
    return f"{n // 12}-{n % 12 + 1:02d}"


def span(a, b):
    out = [a]
    while out[-1] < b:
        y, m = map(int, out[-1].split("-"))
        out.append(f"{y + m // 12}-{m % 12 + 1:02d}")
    return out


def windows(text):
    """Return windows as [(label, [yyyy-mm, ...], add_on)]. Handles the three
    spellings in rfp_terms.csv: '2028: Jan-Mar +0.0', 'Jan-Mar 2027 +0.0',
    'Nov 2027-Jan 2028 +2.0' and the single month 'Jul 2029 +4.5'."""
    head = re.match(r"(\d{4}): (.+)", text)
    parts = [f"{p.rsplit(' ', 1)[0]} {head.group(1)} {p.rsplit(' ', 1)[1]}" for p in head.group(2).split("; ")] \
        if head else text.split("; ")
    out = []
    for part in parts:
        m = re.fullmatch(r"(\w{3})(?: (\d{4}))?(?:-(\w{3}))? (\d{4}) \+([\d.]+)", part)
        if not m:
            sys.exit(f"cannot read return window '{part}'")
        a, ya, b, yb, add = m.groups()
        out.append((part.rsplit(" ", 1)[0], span(ym(a, ya or yb), ym(b or a, yb)), float(add)))
    return out


def main():
    terms = [r for r in csv.DictReader((ROOT / "data/reference/rfp_terms.csv").open()) if r["round"] == ROUND]
    rnd = [r for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open()) if r["round"] == ROUND][0]
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

    rows, seen = [], set()
    # No award yet: price the round on the bid date and on the latest close we hold.
    last = min(max(d for d, _ in curve), max(front))
    days = [("bids due", rnd["bids_due"])] + ([("award", rnd["award_date"])] if rnd["award_date"] else [("latest", last)])
    for label, day in days:
        for t in terms:
            mon, year = t["delivery_period"].split()
            # Oil lifted in a month prices off the next month's contract. Yahoo drops
            # expired contracts, so this is blank where that contract is not served.
            later = curve.get((day, ym(mon, year, 1)))
            for window, months, add in windows(t["return_options"]):
                key = (label, t["site"], t["delivery_period"], window)
                if key in seen:
                    sys.exit(f"duplicate key {key}")   # hard failure by house rule
                seen.add(key)
                have = [curve[day, m] for m in months if (day, m) in curve]   # Yahoo lacks a few far months
                if not have:
                    sys.exit(f"no futures for {window} on {day}")
                ret = sum(have) / len(have)
                prem = float(t["min_premium_pct"]) + add
                owed = 1 + prem / 100
                rows.append(dict(
                    round=ROUND, priced_on=label, date=day, site=t["site"], delivery=t["delivery_period"],
                    offered_bbl=t["offered_bbl"], return_window=window, premium_pct=prem, return_price=round(ret, 2),
                    cost_to_return=round(owed * ret, 2), sale_front_month=round(front[day], 2),
                    margin_front_month=round(front[day] - owed * ret, 2),
                    breakeven_premium_front_pct=round((front[day] / ret - 1) * 100, 1),
                    sale_delivery_contract=later if later else "",
                    margin_delivery_contract=round(later - owed * ret, 2) if later else "",
                    breakeven_premium_delivery_pct=round((later / ret - 1) * 100, 1) if later else ""))
    out = ROOT / f"data/processed/trade_example_round_{ROUND}.csv"
    with out.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"round {ROUND}: {total:,} barrels awarded, {traders:,} to trading houses")
    for r in rows:
        print("  {priced_on:8s} {date} {site:11s} {delivery} | return {return_window:17s} {premium_pct:4}% x ${return_price:5} = ${cost_to_return:5} "
              "| front ${sale_front_month} margin {margin_front_month:6} be {breakeven_premium_front_pct}% "
              "| delivery ${sale_delivery_contract} margin {margin_delivery_contract} be {breakeven_premium_delivery_pct}%".format(**r))
    print(f"wrote {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
