#!/usr/bin/env python3
"""Build dist/trade.html, the "how borrowing oil can make money" explainer.

Inputs
  data/processed/trade_example_round_<round>.csv   from scripts/trade_math.py
  data/processed/spr_2026_exchange_awards.csv      from scripts/build_ledger.py
  data/reference/rounds.csv
  data/reference/transport_costs.csv              published pipeline rates, for the notes
  scripts/trade_template.html, logo/d4tp-text-dark.svg

Output
  dist/trade.html   self-contained page, data inlined, no CDN

One example per round: the lot and return window that left the most money per
barrel on the day bids were due, at the minimum premium. The sale price is the
futures contract for the month after pickup where we hold it, and the
front-month price where we do not. Every number on the page comes from the
inlined data; the template holds none.
"""
import base64, csv, datetime, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROUNDS = ["1.b", "3", "4"]      # the rounds shown, left to right
SHOW_PENDING_MATH = True        # show the math for a round DOE has not reported yet


def best_example(rnd):
    subprocess.run([sys.executable, str(ROOT / "scripts/trade_math.py"), rnd], check=True, capture_output=True)
    rows = [r for r in csv.DictReader((ROOT / f"data/processed/trade_example_round_{rnd}.csv").open())
            if r["priced_on"] == "bids due"]
    keys = [(r["site"], r["delivery"], r["return_window"]) for r in rows]
    if len(set(keys)) != len(keys):
        sys.exit(f"round {rnd}: duplicate lot and return window")   # hard failure by house rule
    def pick(r):
        basis = "delivery" if r["sale_delivery_contract"] else "front"
        sale = float(r["sale_delivery_contract"] or r["sale_front_month"])
        margin = float(r["margin_delivery_contract"] or r["margin_front_month"])
        be = float(r["breakeven_premium_delivery_pct"] or r["breakeven_premium_front_pct"])
        return dict(site=r["site"], pickup=r["delivery"], window=r["return_window"], date=r["date"],
                    premium_pct=float(r["premium_pct"]), later_price=float(r["return_price"]),
                    cost=float(r["cost_to_return"]), sale=sale, sale_basis=basis, left=margin, gap_pct=be)
    return max((pick(r) for r in rows), key=lambda x: x["left"])


def main():
    rounds = {r["round"]: r for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open())}
    awards = list(csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open()))
    out_rounds = []
    for rnd in ROUNDS:
        meta = rounds[rnd]
        posted = meta["award_sheet_posted"] == "yes"
        ex = best_example(rnd)
        if not posted and not SHOW_PENDING_MATH:
            ex = None
        out_rounds.append(dict(
            round=rnd, bids_due=meta["bids_due"], award_date=meta["award_date"] or None,
            offered=int(meta["offered_bbl"]),
            taken=sum(int(a["barrels"]) for a in awards if a["round"] == rnd) if posted else None,
            trader_taken=sum(int(a["barrels"]) for a in awards
                             if a["round"] == rnd and a["type"] == "Trading house") if posted else None,
            example=ex))
    pipes = [float(r["cents_per_bbl"]) for r in csv.DictReader((ROOT / "data/reference/transport_costs.csv").open())
             if r["item"] == "Pipeline"]
    data = dict(built=datetime.date.today().isoformat(), rounds=out_rounds,
                pipeline_cents=dict(low=min(pipes), high=max(pipes)))
    logo = "data:image/svg+xml;base64," + base64.b64encode((ROOT / "logo/d4tp-text-dark.svg").read_bytes()).decode()
    html = (ROOT / "scripts/trade_template.html").read_text()
    if "/*__DATA__*/null" not in html or "__LOGO__" not in html:
        sys.exit("template slots missing")
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))).replace("__LOGO__", logo)
    out = ROOT / "dist/trade.html"
    out.write_text(html)
    print(f"wrote {out.relative_to(ROOT)}: {len(html):,} bytes")
    for r in out_rounds:
        print(" ", r["round"], r["taken"], r["example"])


if __name__ == "__main__":
    main()
