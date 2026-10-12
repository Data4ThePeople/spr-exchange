#!/usr/bin/env python3
"""Where the money from the 2022 emergency sales went, as far as DOE's documents show.

Three inputs:
  data/reference/sale_proceeds_2022.csv   figures keyed from DOE's annual report for 2022, with page and phrase
  data/processed/spr_2022_sale_awards.csv the sales at the prices offered (scripts/build_sales_2022.py)
  data/processed/spr_purchase_rounds.csv  the oil bought back (scripts/build_purchases.py)

Writes data/processed/sale_proceeds_use.json. The "left" figure is arithmetic,
not a balance DOE has published: receipts, less the rescission, less the
purchase awards. It leaves out the cost of moving oil, other receipts into the
same account, and anything Congress did after 2023.
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ref = {r["item"]: int(r["value"]) for r in csv.DictReader((ROOT / "data/reference/sale_proceeds_2022.csv").open())}
    sales = list(csv.DictReader((ROOT / "data/processed/spr_2022_sale_awards.csv").open()))
    bought = [r for r in csv.DictReader((ROOT / "data/processed/spr_purchase_rounds.csv").open()) if r["outcome"] == "Awarded"]
    sold_bbl, bid_usd = sum(int(r["barrels"]) for r in sales), sum(int(r["dollars"]) for r in sales)
    received, rescinded = ref["Received from the 2022 emergency sales"], ref["Rescinded by Congress in exchange for cancelling mandated sales"]
    cancelled = ref["Mandated sales cancelled in that exchange"]
    buy_bbl, buy_usd = sum(int(r["barrels"]) for r in bought), sum(int(r["dollars"]) for r in bought)
    pct = lambda a, b: round(a / b * 100, 1)
    out = dict(
        barrels_sold=sold_bbl, dollars_at_prices_bid=bid_usd, price_bid=round(bid_usd / sold_bbl, 2),
        dollars_received=received, price_received_per_awarded_barrel=round(received / sold_bbl, 2),
        received_below_bid_pct=pct(bid_usd - received, bid_usd),
        rescinded=rescinded, rescinded_pct_of_received=pct(rescinded, received),
        mandated_sales_cancelled_bbl=cancelled, rescission_per_cancelled_barrel=round(rescinded / cancelled, 2),
        purchases_bbl=buy_bbl, purchases_dollars=buy_usd, purchases_pct_of_received=pct(buy_usd, received),
        purchase_price=round(buy_usd / buy_bbl, 2), purchases_pct_of_barrels_sold=pct(buy_bbl, sold_bbl),
        left_after_rescission_and_purchases=received - rescinded - buy_usd,
        left_pct_of_received=pct(received - rescinded - buy_usd, received))
    (ROOT / "data/processed/sale_proceeds_use.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
