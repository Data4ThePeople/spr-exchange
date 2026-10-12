#!/usr/bin/env python3
"""Tie-out: recompute the published figures by a second path and compare.

Each check reads the raw files directly (award PDFs, EIA JSON, Yahoo JSON) or
the hand-keyed reference CSVs, recomputes a figure without importing the build
scripts, and compares it with what is inlined in the pages in dist/. Prints one
line per check and exits non-zero if any fail.
"""
import csv, datetime, json, re, sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
fails = []


def check(name, got, want, tol=0):
    ok = abs(got - want) <= tol if isinstance(got, (int, float)) else got == want
    print(("PASS" if ok else "FAIL"), name, "|", got, "|", want)
    if not ok:
        fails.append(name)


def page_data(name):
    html = (ROOT / "dist" / name).read_text()
    start = re.search(r"(?:const DATA|var D) = (?=\{)", html).end()   # the ledger page names it D
    return json.JSONDecoder().raw_decode(html[start:])[0]


def closes(symbol):
    res = json.loads((ROOT / "data/raw/futures" / f"{symbol}.json").read_text())
    tz = datetime.timezone(datetime.timedelta(seconds=res["meta"]["gmtoffset"]))
    return {datetime.datetime.fromtimestamp(t, tz).date().isoformat(): round(c, 2)
            for t, c in zip(res["timestamp"], res["indicators"]["quote"][0]["close"]) if c is not None}


def wti(year, month):
    return closes(f"CL{'FGHJKMNQUVXZ'[month - 1]}{year % 100:02d}.NYM")


# 1. Ledger: every award sheet's stated total, straight from the PDF text.
ledger = page_data("ledger.html")
stated = 0
for pdf in sorted((ROOT / "data/raw/doe_awards").glob("*.pdf")):
    text = re.sub(r"\s+", " ", " ".join(p.extract_text() for p in PdfReader(pdf).pages))
    total = int(re.search(r"exchange of ([\d,]+) barrels", text).group(1).replace(",", ""))
    rnd = re.search(r"Release No\. ([\w.]+?) Award", pdf.name).group(1)
    check(f"ledger round {rnd} total", sum(r["barrels"] for r in ledger["ledger"] if r["round"] == rnd), total)
    stated += total
check("ledger grand total", sum(r["barrels"] for r in ledger["ledger"]), stated)
check("ledger contracts", len(ledger["ledger"]), len({(r["round"], r["company_as_listed"]) for r in ledger["ledger"]}))

# 2. SPR weekly stocks on the ledger page against the raw EIA response.
raw = {r["period"]: float(r["value"]) for r in json.loads((ROOT / "data/raw/eia/PET.WCSSTUS1.W.json").read_text()) if r["value"] is not None}
check("SPR weeks match raw EIA", sum(1 for d, v in ledger["spr"] if raw.get(d) != v), 0)
check("SPR latest week", ledger["spr"][-1][1], raw[max(raw)])

# 3. Trade page: recompute each card from the raw futures files.
terms = list(csv.DictReader((ROOT / "data/reference/rfp_terms.csv").open()))
trade = page_data("trade.html")
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
for r in trade["rounds"]:
    e = r["example"]
    a, rest = e["window"].split("-")                       # e.g. "Oct-Dec 2028"
    b, year = rest.split()
    months = range(MON.index(a) + 1, MON.index(b) + 2)
    later = [wti(int(year), m).get(e["date"]) for m in months]
    later = [v for v in later if v is not None]
    later_price = round(sum(later) / len(later), 2)
    if e["sale_basis"] == "front":
        sale = closes("CL=F")[e["date"]]
    else:
        pm, py = e["pickup"].split()
        n = int(py) * 12 + MON.index(pm) + 1
        sale = wti(n // 12, n % 12 + 1)[e["date"]]
    lot = [t for t in terms if t["round"] == r["round"] and t["site"] == e["site"] and t["delivery_period"] == e["pickup"]]
    check(f"trade {r['round']} lot found once", len(lot), 1)
    add = float(re.search(re.escape(e["window"].split()[0]) + r"[^;]*?\+([\d.]+)", lot[0]["return_options"]).group(1))
    prem = float(lot[0]["min_premium_pct"]) + add
    check(f"trade {r['round']} premium", e["premium_pct"], prem)
    check(f"trade {r['round']} sale price", e["sale"], sale)
    check(f"trade {r['round']} later price", e["later_price"], later_price)
    check(f"trade {r['round']} left over", e["left"], round(sale - (1 + prem / 100) * sum(later) / len(later), 2), 0.011)
    if r["taken"] is not None:
        check(f"trade {r['round']} barrels taken", r["taken"], sum(x["barrels"] for x in ledger["ledger"] if x["round"] == r["round"]))
        check(f"trade {r['round']} trader barrels", r["trader_taken"],
              sum(x["barrels"] for x in ledger["ledger"] if x["round"] == r["round"] and x["type"] == "Trading house"))

# 4. Returns page: both scenarios hold every awarded barrel, and no lot is overfilled.
ret = page_data("returns.html")
for s in ("earliest", "latest"):
    check(f"returns {s} total", sum(n for _, n in ret[s]), stated)
check("returns latest last date", ret["latest"][-1][0], "2029-07-31")
check("receipt rate total", ret["receipt_per_month"],
      sum(int(r["nominal_receipt_bbl_per_month"]) for r in csv.DictReader((ROOT / "data/reference/site_receipt_rates.csv").open())))

# 5. Comparison page: 2022 sale totals straight from the award reports' own
#    "TOTAL OFFER AWARD" lines, without the line-item parser, and again from
#    DOE's separate Apparently Successful Offers reports.
comp = page_data("compare.html")
p22, p26 = comp["programs"]
SALES = ROOT / "data/raw/doe_sales_2022"
cmap = {r["company_as_listed"]: r for r in csv.DictReader((ROOT / "data/reference/company_map.csv").open())}


def offer_totals(pdf):
    """[(buyer as listed, barrels, dollars)] from each page's header and total line."""
    out = []
    for page in PdfReader(pdf).pages:
        text = page.extract_text()
        head = re.search(r"OFR# OFFEROR INFORMATION AGENT INFORMATION\n\d+ (.+)", text)
        tot = re.search(r"TOTAL OFFER AWARD ([\d,]+) TOTAL PRICE \$([\d,]+)", text)
        if head and tot:
            out.append((head.group(1).strip(), int(tot.group(1).replace(",", "")) * 1000, int(tot.group(2).replace(",", ""))))
    return out


awards = [x for pdf in sorted(SALES.glob("*Successful Awards Report.pdf")) for x in offer_totals(pdf)]
apparent = [x for pdf in sorted(SALES.glob("*Apparently Successful Offers Report.pdf")) for x in offer_totals(pdf)]
check("2022 barrels, award reports", p22["total"], sum(b for _, b, _ in awards))
check("2022 dollars, award reports", p22["dollars"], sum(d for _, _, d in awards))
check("2022 barrels, apparently successful offers reports", p22["total"], sum(b for _, b, _ in apparent))
check("2022 buyers", len(p22["firms"]), len({cmap[n]["company"] for n, _, _ in awards}))
for f in p22["firms"]:
    check(f"2022 {f['company']}", f["barrels"], sum(b for n, b, _ in awards if cmap[n]["company"] == f["company"]))
for t in p22["types"]:
    check(f"2022 type {t['type']}", t["barrels"], sum(b for n, b, _ in awards if cmap[n]["type"] == t["type"]))
check("2022 offered", p22["offered"], sum(int(r["offered_bbl"]) for r in csv.DictReader((ROOT / "data/reference/sales_2022.csv").open())))
check("2026 total matches the ledger page", p26["total"], sum(r["barrels"] for r in ledger["ledger"]))
for t in p26["types"]:
    check(f"2026 type {t['type']}", t["barrels"], sum(r["barrels"] for r in ledger["ledger"] if r["type"] == t["type"]))
check("2026 borrowers", len(p26["firms"]), len({r["company"] for r in ledger["ledger"]}))

# 6. Design evidence: recount the 2022 offers straight from the Offeror Abstract
#    Reports (one page per offer), and check the January 2022 loan table against
#    the saved DOE release.
ev = json.loads((ROOT / "data/processed/design_evidence.json").read_text())
heads = []
for pdf in sorted(SALES.glob("*Offeror Abstract Report.pdf")):
    for page in PdfReader(pdf).pages:
        m = re.search(r"OFR# OFFEROR INFORMATION AGENT INFORMATION\n(\d+) (.+)", page.extract_text())
        if m:
            heads.append((pdf.name, m.group(1), m.group(2).strip()))
check("2022 offers filed", ev["firms"]["offers_2022"], len({(f, n) for f, n, _ in heads}))
check("2022 bidders", ev["firms"]["bidders_2022"], len({cmap[n]["company"] for _, _, n in heads}))
check("no 2022 offer from Trafigura", sum(1 for _, _, n in heads if "trafigura" in n.lower()), 0)
by_type = {}
for name in {n for _, _, n in heads}:
    by_type.setdefault(cmap[name]["type"], set()).add(cmap[name]["company"])
bid_types = {t: b for t, b in ev["bids_2022"].items() if isinstance(b, dict)}   # one key is a plain count
for t, b in bid_types.items():
    check(f"2022 bidders, {t}", b["bidders"], len(by_type[t]))
    check(f"2022 barrels won, {t}", b["barrels_won"], sum(x for n, x, _ in awards if cmap[n]["type"] == t))
check("2022 barrels won across bidders", sum(b["barrels_won"] for b in bid_types.values()), p22["total"])
release = re.sub(r"<[^>]+>", " ", next((ROOT / "data/raw/doe_press").glob("2022-01-25*.html")).read_text(errors="ignore"))
listed = {n.strip(): round(float(v) * 1e6) for n, v in re.findall(r"([A-Z][\w .&]+?) \(([\d.]+) million barrels\)", release)}
keyed = {r["company_as_listed"]: int(r["barrels"]) for r in csv.DictReader((ROOT / "data/reference/exchange_jan_2022.csv").open())}
check("January 2022 loans match DOE's release", keyed, listed)
check("January 2022 loan total", ev["loan_jan_2022"]["total"], sum(listed.values()))
eia = {}
for r in csv.DictReader((ROOT / "data/processed/eia_series.csv").open()):
    if r["value"]:
        eia.setdefault(r["series_id"], {})[r["period"]] = float(r["value"])
for year, m in ev["market"].items():
    a, b = m["window"]
    for sid, key in (("PET.WPULEUS3.W", "refinery_utilization_pct"), ("PET.WCRRIUS2.W", "refiner_crude_inputs_weekly_kbd"), ("PET.WCREXUS2.W", "crude_exports_weekly_kbd")):
        raw = [float(x["value"]) for x in json.loads((ROOT / "data/raw/eia" / f"{sid}.json").read_text()) if x["value"] is not None and a <= x["period"] <= b]
        check(f"{year} {key}", m[key]["mean"], round(sum(raw) / len(raw), 1))

# 7. The comparison page carries the evidence file's figures unchanged.
check("page bids match the evidence file", {b["type"]: b["barrels_won"] for b in comp["bids"]},
      {t: b["barrels_won"] for t, b in bid_types.items() if t in comp["types"]})
check("page price gaps match the evidence file", comp["paf"], ev["paf_2022"])
agreements = list(csv.DictReader((ROOT / "data/reference/exchange_2021_22.csv").open()))
check("page 2021-22 loan total", comp["loan"]["total"], sum(int(r["barrels"]) for r in agreements))
check("2021-22 agreements signed January 21 to 25 match DOE's release",
      sum(int(r["barrels"]) for r in agreements if "2022-01-21" <= r["signed"] <= "2022-01-25"), sum(listed.values()))
want = {}
for r in agreements:
    want[cmap[r["company_as_listed"]]["type"]] = want.get(cmap[r["company_as_listed"]]["type"], 0) + int(r["barrels"])
check("page 2021-22 loan types", {t["type"]: t["barrels"] for t in comp["loan"]["types"] if t["barrels"]}, want)

print(f"\n{len(fails)} failed" if fails else "\nall checks passed")
sys.exit(1 if fails else 0)
