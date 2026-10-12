#!/usr/bin/env python3
"""Did companies take more oil in the 2026 rounds where the trade paid more?

For every lot DOE offered in 2026 (data/reference/rfp_terms.csv) this prices the
borrow, sell and buy-back trade on the day bids were due, the same way
scripts/trade_math.py does: one barrel sold at the front-month WTI futures
close, and (1 + premium) barrels bought back at the WTI futures for the return
window, at DOE's minimum premium plus the window's add-on. Each lot is given
the return window that leaves the most per barrel.

DOE does not publish which lots were taken, only barrels per company per
round. So the comparison with uptake is by round: the offered-weighted average
of what the lots left per barrel, beside the share of that round's oil that was
taken.

Round 1's RFP gives one continuous return window per lot, not a menu. It is
priced at the last three months of that window, the dates a borrower would
pick when later oil is cheaper.

The front-month price is used for every round so they are on one basis; the
contracts for the pickup months have expired and are not served. This flatters
later pickups (see DATASETS.md). Left out, as before: the premium each company
actually bid, the grade's price gap to WTI, shipping, and the bank guarantee.

Writes data/processed/lot_margins_2026.csv and data/processed/round_uptake_2026.csv.
"""
import csv, re, sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

sys.argv = sys.argv[:1]                       # trade_math reads a round from argv at import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from trade_math import MONTHS, cents, front_month, span, windows, ym

ROOT = Path(__file__).resolve().parent.parent
LAST = 3    # months at the end of a continuous window used to price it


def options(text):
    """[(label, [yyyy-mm, ...], add_on)] for a lot's return terms."""
    m = re.fullmatch(r"(\w{3}) \d+ (\d{4}) to (\w{3}) \d+ (\d{4})", text)
    if not m:
        return windows(text)
    months = span(ym(m.group(1), m.group(2)), ym(m.group(3), m.group(4)))[-LAST:]
    first = months[0].split("-")
    return [(f"{MONTHS[int(first[1]) - 1]}-{m.group(3)} {m.group(4)}", months, 0.0)]


def main():
    terms = list(csv.DictReader((ROOT / "data/reference/rfp_terms.csv").open()))
    rounds = {r["round"]: r for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open())}
    awards = list(csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open()))
    curve = {}
    for r in csv.DictReader((ROOT / "data/processed/futures_closes.csv").open()):
        if r["product"] == "WTI":
            curve[r["date"], r["delivery"]] = float(r["close"])
    front = front_month()

    lots, seen = [], set()
    for t in terms:
        day = rounds[t["round"]]["bids_due"]
        best = None
        for label, months, add in options(t["return_options"]):
            have = [curve[day, m] for m in months if (day, m) in curve]
            if not have:
                continue
            later = sum(have) / len(have)
            prem = float(t["min_premium_pct"]) + add
            left = front[day] - (1 + prem / 100) * later
            if best is None or left > best["left"]:
                best = dict(window=label, premium_pct=prem, later_price=cents(later), left=left,
                            gap_pct=round((front[day] / later - 1) * 100, 1))
        if best is None:
            sys.exit(f"round {t['round']} {t['site']} {t['delivery_period']}: no futures for any return window on {day}")
        key = (t["round"], t["site"], t["stream"], t["delivery_period"], t["min_premium_pct"])
        if key in seen:
            sys.exit(f"duplicate lot {key}")   # hard failure by house rule
        seen.add(key)
        lots.append(dict(round=t["round"], bids_due=day, site=t["site"], stream=t["stream"], pickup=t["delivery_period"],
                         offered_bbl=int(t["offered_bbl"]), min_premium_pct=float(t["min_premium_pct"]),
                         best_window=best["window"], premium_pct=best["premium_pct"], sale_front_month=cents(front[day]),
                         later_price=best["later_price"], gap_pct=best["gap_pct"],
                         gap_minus_premium_pts=round(best["gap_pct"] - best["premium_pct"], 1), left_per_barrel=cents(best["left"])))
    with (ROOT / "data/processed/lot_margins_2026.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(lots[0]))
        w.writeheader()
        w.writerows(lots)

    out = []
    for rnd, meta in rounds.items():
        mine = [l for l in lots if l["round"] == rnd]
        offered = sum(l["offered_bbl"] for l in mine)
        if offered != int(meta["offered_bbl"]):
            sys.exit(f"round {rnd}: lots add to {offered:,}, rounds.csv says {meta['offered_bbl']}")
        posted = meta["award_sheet_posted"] == "yes"
        taken = sum(int(a["barrels"]) for a in awards if a["round"] == rnd) if posted else ""
        wavg = lambda k: sum(l[k] * l["offered_bbl"] for l in mine) / offered
        out.append(dict(round=rnd, bids_due=meta["bids_due"], lots=len(mine), offered_bbl=offered, taken_bbl=taken,
                        taken_pct=float(Decimal(str(round(taken / offered * 100, 6))).quantize(Decimal("0.1"), ROUND_HALF_UP)) if posted else "",   # halves up
                        min_premium_low_pct=min(l["min_premium_pct"] for l in mine), min_premium_high_pct=max(l["min_premium_pct"] for l in mine),
                        sale_front_month=mine[0]["sale_front_month"], avg_gap_pct=round(wavg("gap_pct"), 1),
                        avg_premium_pct=round(wavg("premium_pct"), 1), avg_left_per_barrel=cents(wavg("left_per_barrel")),
                        lowest_left=min(l["left_per_barrel"] for l in mine), highest_left=max(l["left_per_barrel"] for l in mine)))
    with (ROOT / "data/processed/round_uptake_2026.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print("round  bids due    lots  offered   taken    taken%  min premium   gap    premium  left/bbl (low to high)")
    for r in out:
        print(f"{r['round']:5s}  {r['bids_due']}  {r['lots']:3d}  {r['offered_bbl'] / 1e6:6.1f}M  "
              f"{(str(round(r['taken_bbl'] / 1e6, 2)) + 'M') if r['taken_bbl'] != '' else 'pending':>7s}  {str(r['taken_pct']):>5s}  "
              f"{r['min_premium_low_pct']:g}-{r['min_premium_high_pct']:g}%".ljust(78) +
              f"{r['avg_gap_pct']:5.1f}%  {r['avg_premium_pct']:5.1f}%  ${r['avg_left_per_barrel']:6.2f} (${r['lowest_left']:.2f} to ${r['highest_left']:.2f})")
    print("wrote data/processed/lot_margins_2026.csv and round_uptake_2026.csv")


if __name__ == "__main__":
    main()
