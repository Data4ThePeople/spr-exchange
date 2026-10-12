#!/usr/bin/env python3
"""Build dist/compare.html: who got the oil in the 2022 sales and the 2026 loans.

Inputs
  data/processed/spr_2022_sale_awards.csv      from scripts/build_sales_2022.py
  data/processed/spr_2026_exchange_awards.csv  from scripts/build_ledger.py
  data/reference/sales_2022.csv                offered volume and reference price per sale, from the notices
  data/reference/rounds.csv                    2026 rounds
  data/reference/program_comparison.csv        the feature table; {slots} are filled from the data here
  data/processed/design_evidence.json          from scripts/design_evidence.py: 2022 bids, price gaps, the January 2022 loans
  scripts/compare_template.html, logo/d4tp-text-dark.svg

Output
  dist/compare.html   self-contained page, data inlined, no CDN

Every number on the page comes from the inlined data; the template holds none.
"""
import base64, csv, datetime, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MONTHS = "January February March April May June July August September October November December".split()
TYPES = ["Trading house", "Major trading arm", "Foreign oil company trading arm", "Refiner", "Midstream"]


def read(path):
    return list(csv.DictReader((ROOT / path).open()))


def month_year(iso):
    y, m, _ = iso.split("-")
    return f"{MONTHS[int(m) - 1]} {y}"


def long_date(iso):
    y, m, d = map(int, iso.split("-"))
    return f"{MONTHS[m - 1]} {d}, {y}"


def side(rows, offered):
    """Totals, shares by firm type and one line per company for one program."""
    total = sum(int(r["barrels"]) for r in rows)
    firms = {}
    for r in rows:
        if r["type"] not in TYPES:
            sys.exit(f"unknown firm type '{r['type']}'")
        f = firms.setdefault(r["company"], dict(company=r["company"], type=r["type"], barrels=0))
        if f["type"] != r["type"]:
            sys.exit(f"{r['company']} has two firm types")   # hard failure by house rule
        f["barrels"] += int(r["barrels"])
    types = [dict(type=t, barrels=sum(f["barrels"] for f in firms.values() if f["type"] == t)) for t in TYPES]
    if sum(t["barrels"] for t in types) != total:
        sys.exit("firm types do not add to the total")
    return dict(total=total, offered=offered, firms=sorted(firms.values(), key=lambda f: (-f["barrels"], f["company"])),
                types=types)


def main():
    s22, s26 = read("data/processed/spr_2022_sale_awards.csv"), read("data/processed/spr_2026_exchange_awards.csv")
    sales, rounds = read("data/reference/sales_2022.csv"), read("data/reference/rounds.csv")
    if {r["sale"] for r in s22} != {r["sale"] for r in sales}:
        sys.exit("sales_2022.csv and the award reports do not list the same sales")
    posted = [r for r in rounds if r["award_sheet_posted"] == "yes"]
    if {r["round"] for r in s26} != {r["round"] for r in posted}:
        sys.exit("rounds.csv and the 2026 ledger do not list the same rounds")

    a = side(s22, sum(int(r["offered_bbl"]) for r in sales))
    b = side(s26, sum(int(r["offered_bbl"]) for r in posted))
    a.update(key="2022", name="2022 emergency sales", verb="bought", noun="buyers",
             dollars=sum(int(r["dollars"]) for r in s22),
             events=[dict(name=r["sale"], date=min(x["run_date"] for x in s22 if x["sale"] == r["sale"]),
                          offered=int(r["offered_bbl"]),
                          taken=sum(int(x["barrels"]) for x in s22 if x["sale"] == r["sale"]),
                          dollars=sum(int(x["dollars"]) for x in s22 if x["sale"] == r["sale"])) for r in sales])
    b.update(key="2026", name="2026 emergency loans", verb="borrowed", noun="borrowers",
             events=[dict(name="Round " + r["round"], date=r["award_date"], offered=int(r["offered_bbl"]),
                          taken=sum(int(x["barrels"]) for x in s26 if x["round"] == r["round"])) for r in posted])
    a["events"].sort(key=lambda e: e["date"])
    b["events"].sort(key=lambda e: e["date"])

    sour = [float(r["base_reference_price_sour"]) for r in sales if r["base_reference_price_sour"]]
    by_date = sorted(rounds, key=lambda r: r["bids_due"])
    first, last = by_date[0], by_date[-1]
    low = min(posted, key=lambda r: float(r["min_premium_low_pct"]))     # lowest among rounds with results
    top = max(rounds, key=lambda r: float(r["min_premium_high_pct"]))
    month = lambda r: MONTHS[int(r["bids_due"].split("-")[1]) - 1]
    num = lambda v: f"{float(v):g}"
    slots = dict(
        n_sales=len(sales), first_2022=month_year(a["events"][0]["date"]), last_2022=month_year(a["events"][-1]["date"]),
        n_rounds=len(rounds), n_posted=len(posted), first_2026=month_year(min(r["award_date"] for r in posted)),
        last_2026=month_year(max(r["bids_due"] for r in rounds)),
        offered_2022=f"{a['offered'] / 1e6:.1f}", offered_2026=f"{b['offered'] / 1e6:.1f}",
        awarded_2022=f"{a['total'] / 1e6:.2f}", awarded_2026=f"{b['total'] / 1e6:.2f}",
        uptake_2022=f"{a['total'] / a['offered'] * 100:.1f}", uptake_2026=f"{b['total'] / b['offered'] * 100:.1f}",
        brp_low=f"{min(sour):.2f}", brp_high=f"{max(sour):.2f}",
        prem_first_low=num(first["min_premium_low_pct"]), prem_first_high=num(first["min_premium_high_pct"]),
        prem_low_low=num(low["min_premium_low_pct"]), prem_low_high=num(low["min_premium_high_pct"]),
        low_round_month=month(low), prem_max=num(top["min_premium_high_pct"]), max_round_month=month(top),
        prem_last_low=num(last["min_premium_low_pct"]), prem_last_high=num(last["min_premium_high_pct"]),
        last_round_month=month(last),
        dollars_2022=f"{a['dollars'] / 1e9:.2f}", avg_price_2022=f"{a['dollars'] / a['total']:.2f}",
        last_return_2026=month_year(max(r["last_return_date"] for r in posted)))   # the RFP gives a month, not a day
    features, seen = [], set()
    for r in read("data/reference/program_comparison.csv"):
        if r["feature"] in seen:
            sys.exit(f"duplicate feature '{r['feature']}'")   # hard failure by house rule
        seen.add(r["feature"])
        cells = {k: r[k].format(**slots) for k in ("sales_2022", "exchange_2026")}
        if any(re.search(r"[{}]", v) for v in cells.values()):
            sys.exit(f"unfilled slot in '{r['feature']}'")
        features.append(dict(feature=r["feature"], a=cells["sales_2022"], b=cells["exchange_2026"],
                             source_a=r["source_2022"], source_b=r["source_2026"]))

    ev = json.loads((ROOT / "data/processed/design_evidence.json").read_text())
    cmap = {r["company_as_listed"]: r for r in read("data/reference/company_map.csv")}
    bids = [dict(type=t, **ev["bids_2022"][t]) for t in TYPES if t in ev["bids_2022"]]
    other = {t: v for t, v in ev["bids_2022"].items() if t not in TYPES and isinstance(v, dict)}
    data = dict(built=datetime.date.today().isoformat(), types=TYPES, programs=[a, b], features=features,
                bids=bids, bids_other=other, uptake=ev["uptake_2026"], paf=ev["paf_2022"], firms=ev["firms"],
                )
    logo = "data:image/svg+xml;base64," + base64.b64encode((ROOT / "logo/d4tp-text-dark.svg").read_bytes()).decode()
    html = (ROOT / "scripts/compare_template.html").read_text()
    if "/*__DATA__*/null" not in html or "__LOGO__" not in html:
        sys.exit("template slots missing")
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))).replace("__LOGO__", logo)
    out = ROOT / "dist/compare.html"
    out.write_text(html)
    print(f"wrote {out.relative_to(ROOT)}: {len(html):,} bytes")
    for p in (a, b):
        print(f"  {p['name']}: {p['total']:,} of {p['offered']:,} barrels, {len(p['firms'])} firms; " +
              ", ".join(f"{t['type']} {t['barrels'] / p['total'] * 100:.1f}%" for t in p["types"]))
        print("   top:", ", ".join(f"{f['company']} {f['barrels'] / p['total'] * 100:.1f}%" for f in p["firms"][:4]))


if __name__ == "__main__":
    main()
