#!/usr/bin/env python3
"""Where the money from the 2022 emergency sales went, as far as the documents show.

Inputs:
  data/reference/sale_proceeds_2022.csv   figures keyed from DOE's annual reports, Public Law 117-328 and the
                                          President's Budget Appendix, each with the phrase it comes from
  data/processed/spr_2022_sale_awards.csv the sales at the prices offered (scripts/build_sales_2022.py)
  data/processed/spr_purchase_rounds.csv  the oil bought back (scripts/build_purchases.py)

Writes data/processed/sale_proceeds_use.json.

Congress rescinded money from the account twice in the same law. What was
left after both is receipts less the two rescissions. Purchases are counted
through 2024 only: the one award in 2025 was paid from a new appropriation, not
from the 2022 money. Award totals include one 2023 contract that was later
cancelled; DOE gives its barrels but not its seller or dollar value, so the
purchase dollars are slightly overstated.
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAST_YEAR_OF_2022_MONEY = "2024"     # purchases awarded after this were funded by Public Law 119-21


def main():
    ref = {r["item"]: int(r["value"]) for r in csv.DictReader((ROOT / "data/reference/sale_proceeds_2022.csv").open())}
    sales = list(csv.DictReader((ROOT / "data/processed/spr_2022_sale_awards.csv").open()))
    bought = [r for r in csv.DictReader((ROOT / "data/processed/spr_purchase_rounds.csv").open()) if r["outcome"] == "Awarded"]
    early = [r for r in bought if r["as_of"][:4] <= LAST_YEAR_OF_2022_MONEY]
    sold_bbl, bid_usd = sum(int(r["barrels"]) for r in sales), sum(int(r["dollars"]) for r in sales)
    received = ref["Received from the 2022 emergency sales"]
    r1, r2 = ref["Rescinded with the cancelled mandated sales"], ref["Rescinded in the annual energy appropriation"]
    cancelled_sales, cancelled_buy = ref["Mandated sales cancelled"], ref["Purchase contract cancelled after award"]
    buy_bbl, buy_usd = sum(int(r["barrels"]) for r in early), sum(int(r["dollars"]) for r in early)
    after = received - r1 - r2
    pct = lambda a, b: round(a / b * 100, 1)
    out = dict(
        barrels_sold=sold_bbl, dollars_at_prices_bid=bid_usd, price_bid=round(bid_usd / sold_bbl, 2),
        dollars_received=received, price_received_per_awarded_barrel=round(received / sold_bbl, 2),
        received_below_bid_pct=pct(bid_usd - received, bid_usd),
        rescinded_with_cancelled_sales=r1, rescinded_in_energy_appropriation=r2, rescinded_total=r1 + r2,
        rescinded_pct_of_received=pct(r1 + r2, received),
        mandated_sales_cancelled_bbl=cancelled_sales, rescission_per_cancelled_barrel=round(r1 / cancelled_sales, 2),
        left_after_rescissions=after, left_after_rescissions_pct=pct(after, received),
        balance_end_fy2023=ref["Account balance at the end of fiscal year 2023"],
        purchases_awarded_through_2024_bbl=buy_bbl, purchases_awarded_through_2024_dollars=buy_usd,
        purchase_price_through_2024=round(buy_usd / buy_bbl, 2),
        purchases_pct_of_left_after_rescissions=pct(buy_usd, after),
        purchase_contract_cancelled_bbl=cancelled_buy, purchases_less_cancelled_bbl=buy_bbl - cancelled_buy,
        purchases_less_cancelled_pct_of_barrels_sold=pct(buy_bbl - cancelled_buy, sold_bbl),
        purchases_awarded_after_2024_bbl=sum(int(r["barrels"]) for r in bought) - buy_bbl,
        purchases_awarded_after_2024_dollars=sum(int(r["dollars"]) for r in bought) - buy_usd)
    (ROOT / "data/processed/sale_proceeds_use.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
