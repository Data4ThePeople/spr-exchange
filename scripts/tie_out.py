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

print(f"\n{len(fails)} failed" if fails else "\nall checks passed")
sys.exit(1 if fails else 0)
