#!/usr/bin/env python3
"""Evidence on why the 2022 sales and the 2026 loans drew different companies.

Writes data/processed/design_evidence.json and prints it. Five parts:

  bids_2022     who bid in the seven 2022 sales and how often they won, by firm
                type, and how each type's prices compared with the lowest
                winning price for the same oil (same sale and line item).
  paf_2022      how far winning offers sat from DOE's reference price. Under the
                sale terms the buyer pays the market price around delivery plus
                this gap, so the gap is all a bidder competes on.
  firms         which companies appear in the 2022 offers and the 2026 awards.
  loan_jan_2022 who received the seven loans DOE announced on January 25, 2022.
  market        refinery runs, crude exports and the front-month price over the
                fourth month, during each program (EIA weekly and daily data).

Also writes data/processed/spr_2022_sale_streams.csv: the site and crude type
of each master line item, read from Attachment A of each Notice of Sale.
"""
import csv, json, re, sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/doe_sales_2022"
WINDOWS = {"2022": ("2022-03-01", "2022-11-30"), "2026": ("2026-03-20", "2026-10-02")}   # first award report to last; first award to latest EIA week


def read(path):
    return list(csv.DictReader((ROOT / path).open()))


def streams():
    out = {}
    for pdf in sorted(RAW.glob("*NOS.pdf")):
        sale = pdf.name.replace(" NOS.pdf", "")
        text = " ".join(" ".join((p.extract_text() or "").split()) for p in PdfReader(pdf).pages)
        text = text[text.index("CRUDE OIL QUANTITIES OFFERED FOR SALE"):]
        for site, kind, mli in re.findall(r"(Bryan Mound|Big Hill|West Hackberry|Bayou Choctaw) (Sour|Sweet) (\d{3}) ", text):
            if out.get((sale, mli), (site, kind)) != (site, kind):
                sys.exit(f"{sale} MLI {mli}: two streams")   # hard failure by house rule
            out[sale, mli] = (site, kind)
    return out


def wmean(pairs):
    return sum(v * w for v, w in pairs) / sum(w for _, w in pairs)


def main():
    awards, offers = read("data/processed/spr_2022_sale_awards.csv"), read("data/processed/spr_2022_sale_offers.csv")
    a26, cmap = read("data/processed/spr_2026_exchange_awards.csv"), {r["company_as_listed"]: r for r in read("data/reference/company_map.csv")}
    ref = {r["sale"]: r for r in read("data/reference/sales_2022.csv")}
    st = streams()
    with (ROOT / "data/processed/spr_2022_sale_streams.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sale", "mli", "site", "crude_type"])
        w.writerows([s, m, *v] for (s, m), v in sorted(st.items()))

    # 1. Bids: who showed up, how often they won, and their price against the lowest winner on the same oil.
    cut = {}
    for r in awards:
        k = (r["sale"], r["mli"])
        cut[k] = min(cut.get(k, 1e9), float(r["unit_price"]))
    bid_total = sum(int(r["barrels_bid"]) for r in offers)
    bids = {}
    for r in offers:
        b = bids.setdefault(r["type"], dict(bidders=set(), bid=0, won=0, gap=[]))
        b["bidders"].add(r["company"]); b["bid"] += int(r["barrels_bid"]); b["won"] += int(r["barrels_awarded"])
        if (r["sale"], r["mli"]) in cut:
            b["gap"].append((float(r["high_price"]) - cut[r["sale"], r["mli"]], int(r["barrels_bid"])))
    bids_out = {t: dict(bidders=len(b["bidders"]), barrels_bid=b["bid"], share_of_bid_pct=round(b["bid"] / bid_total * 100, 1),
                        barrels_won=b["won"], won_pct_of_bid=round(b["won"] / b["bid"] * 100, 1),
                        best_price_vs_lowest_winner=round(wmean(b["gap"]), 2),
                        bid_below_lowest_winner_pct=round(sum(w for g, w in b["gap"] if g < 0) / sum(w for _, w in b["gap"]) * 100, 1))
                for t, b in bids.items()}

    # 2. Winning offers against the reference price for their crude type.
    paf = []
    for r in awards:
        kind = st[r["sale"], r["mli"]][1]
        brp = ref[r["sale"]]["base_reference_price_" + kind.lower()]
        if not brp:
            sys.exit(f"{r['sale']}: no {kind} reference price in sales_2022.csv")
        paf.append((float(r["unit_price"]) - float(brp), int(r["barrels"]), r["delivery_mode"]))
    total = sum(w for _, w, _ in paf)
    paf_out = dict(mean=round(wmean([(g, w) for g, w, _ in paf]), 2), low=round(min(g for g, _, _ in paf), 2),
                   high=round(max(g for g, _, _ in paf), 2),
                   within_5_dollars_pct=round(sum(w for g, w, _ in paf if abs(g) <= 5) / total * 100, 1),
                   pipeline_pct=round(sum(w for _, w, m in paf if m == "Pipeline") / total * 100, 1))

    # 3. Companies in one program and not the other.
    bidders22, buyers22 = {r["company"] for r in offers}, {r["company"] for r in awards}
    b26 = {r["company"] for r in a26}
    firms = dict(bidders_2022=len(bidders22), offers_2022=len({(r["sale"], r["offer_no"]) for r in offers}),
                 borrowers_2026_that_did_not_bid_in_2022=sorted(b26 - bidders22),
                 buyers_2022_not_in_2026_awards=sorted(buyers22 - b26))

    # 4. The loans DOE announced on January 25, 2022.
    loan = {}
    rows = read("data/reference/exchange_jan_2022.csv")
    for r in rows:
        if r["company_as_listed"] not in cmap:
            sys.exit(f"'{r['company_as_listed']}' is not in company_map.csv")
        t = cmap[r["company_as_listed"]]["type"]
        loan[t] = loan.get(t, 0) + int(r["barrels"])
    ltot = sum(loan.values())
    loan_out = dict(total=ltot, by_type={t: dict(barrels=v, pct=round(v / ltot * 100, 1)) for t, v in loan.items()},
                    firms=[dict(company=cmap[r["company_as_listed"]]["company"], type=cmap[r["company_as_listed"]]["type"],
                                barrels=int(r["barrels"])) for r in rows])

    # 5. Market backdrop from EIA.
    eia = {}
    for r in read("data/processed/eia_series.csv"):
        if r["value"]:
            eia.setdefault(r["name"], {})[r["period"]] = float(r["value"])
    market = {}
    for year, (a, b) in WINDOWS.items():
        m = dict(window=[a, b])
        for name in ("refinery_utilization_pct", "refiner_crude_inputs_weekly_kbd", "crude_exports_weekly_kbd"):
            v = [x for d, x in eia[name].items() if a <= d <= b]
            m[name] = dict(weeks=len(v), mean=round(sum(v) / len(v), 1))
        f1, f4 = eia["wti_fut1_usd"], eia["wti_fut4_usd"]
        g = [(f1[d] / f4[d] - 1) * 100 for d in f1 if a <= d <= b and d in f4]
        m["front_over_fourth_month_pct"] = dict(days=len(g), mean=round(sum(g) / len(g), 1), high=round(max(g), 1)) if g else None
        market[year] = m

    out = dict(bids_2022=bids_out, paf_2022=paf_out, firms=firms, loan_jan_2022=loan_out, market=market)
    (ROOT / "data/processed/design_evidence.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
