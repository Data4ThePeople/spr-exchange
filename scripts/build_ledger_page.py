#!/usr/bin/env python3
"""Build dist/ledger.html, the "Who took the barrels" tool.

Inputs
  data/processed/spr_2026_exchange_awards.csv   from scripts/build_ledger.py
  data/reference/rounds.csv                     per-round terms keyed from the RFPs
  data/processed/eia_series.csv                 from scripts/fetch_eia.py
  scripts/ledger_template.html, logo/d4tp-text-dark.svg

Output
  dist/ledger.html   self-contained page, data inlined, no CDN

Nothing is hardcoded in the page: the template carries a /*__DATA__*/ slot and
every figure on the page is computed from the inlined data at render time.
"""
import base64, csv, datetime, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPR_START = "2025-07-01"   # first week shown on the reserve chart


def main():
    ledger = list(csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open()))
    keys = [(r["round"], r["company_as_listed"]) for r in ledger]
    if len(set(keys)) != len(keys):
        sys.exit("ledger: duplicate round and company")   # hard failure by house rule
    for r in ledger:
        r["barrels"], r["offered_bbl"] = int(r["barrels"]), int(r["offered_bbl"])
        del r["source_pdf"]
    rounds = list(csv.DictReader((ROOT / "data/reference/rounds.csv").open()))
    for r in rounds:
        for k in ("offered_bbl", "min_offer_bbl", "max_per_offeror_bbl"):
            r[k] = int(r[k])
        for k in ("min_premium_low_pct", "min_premium_high_pct"):
            r[k] = float(r[k]) if float(r[k]) % 1 else int(float(r[k]))
    for r in ledger:   # the award sheet and the RFP must agree on what was offered
        match = [x for x in rounds if x["round"] == r["round"]]
        if len(match) != 1 or match[0]["offered_bbl"] != r["offered_bbl"] or match[0]["award_date"] != r["award_date"]:
            sys.exit(f"round {r['round']}: award sheet and rounds.csv disagree")
    spr = [(r["period"], float(r["value"])) for r in csv.DictReader((ROOT / "data/processed/eia_series.csv").open())
           if r["name"] == "spr_stocks_kbbl" and r["period"] >= SPR_START]
    if len({d for d, _ in spr}) != len(spr):
        sys.exit("spr: duplicate week")
    data = dict(built=datetime.date.today().isoformat(), ledger=ledger, rounds=rounds, spr=sorted(spr))
    logo = "data:image/svg+xml;base64," + base64.b64encode((ROOT / "logo/d4tp-text-dark.svg").read_bytes()).decode()
    html = (ROOT / "scripts/ledger_template.html").read_text()
    if "/*__DATA__*/null" not in html or "__LOGO__" not in html:
        sys.exit("template slots missing")
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))).replace("__LOGO__", logo)
    out = ROOT / "dist/ledger.html"
    out.parent.mkdir(exist_ok=True)
    out.write_text(html)
    print(f"wrote {out.relative_to(ROOT)}: {len(html):,} bytes, {len(ledger)} contracts, {len(spr)} weeks of SPR stocks")


if __name__ == "__main__":
    main()
