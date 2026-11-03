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


# 1. Ledger: every award sheet's stated total and its contract lines, straight from the PDF text.
#    The round id comes from rounds.csv by release name ("FY27 SPR Oil Release No. 1" is round FY27-1, not 1).
#    dist/ledger.html is embedded in post 1 and frozen: it is checked against the sheets for the rounds it holds.
#    data/processed/spr_2026_exchange_awards.csv must hold every sheet.
RELEASE = {r["release_name"]: r["round"] for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open())}
CMAP = {r["company_as_listed"]: r["type"] for r in csv.DictReader((ROOT / "data/reference/company_map.csv").open())}
sheets = {}
for pdf in sorted((ROOT / "data/raw/doe_awards").glob("*.pdf")):
    text = re.sub(r"[ \t]+", " ", "\n".join(p.extract_text() for p in PdfReader(pdf).pages))
    rnd = RELEASE[re.search(r"(FY\d\d SPR Oil Release No\. [\w.]+?) Award", pdf.name).group(1)]
    lines = [(n.strip(), int(b.replace(",", ""))) for n, b in re.findall(r"^ ?(.+?) ?[–-] ?([\d,]+) barrels ?$", text, flags=re.M)]
    sheets[rnd] = dict(total=int(re.search(r"exchange of\s+([\d,]+)\s+barrels", text).group(1).replace(",", "")), lines=lines)
    check(f"sheet {rnd}: contract lines add to the stated total", sum(b for _, b in lines), sheets[rnd]["total"])
frozen = page_data("ledger.html")
for rnd in sorted({r["round"] for r in frozen["ledger"]}):
    check(f"ledger.html (frozen) round {rnd} total", sum(r["barrels"] for r in frozen["ledger"] if r["round"] == rnd), sheets[rnd]["total"])
stated = sum(r["barrels"] for r in frozen["ledger"])   # what the frozen post-1 pages hold
check("ledger.html (frozen) grand total, as published in post 1", stated, 133560000)
# The full ledger file (all rounds) stands in for a page: post 3 publishes static charts only.
ledger = {"ledger": [dict(r, barrels=int(r["barrels"]), offered_bbl=int(r["offered_bbl"]))
                     for r in csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open())],
          "spr": [(r["period"], float(r["value"])) for r in csv.DictReader((ROOT / "data/processed/eia_series.csv").open())
                  if r["name"] == "spr_stocks_kbbl"]}
ledger["spr"].sort()
for rnd, sh in sheets.items():
    check(f"ledger file round {rnd} total", sum(r["barrels"] for r in ledger["ledger"] if r["round"] == rnd), sh["total"])
    check(f"ledger file round {rnd} contracts", sorted((r["company_as_listed"], r["barrels"]) for r in ledger["ledger"] if r["round"] == rnd), sorted(sh["lines"]))
stated_all = sum(sh["total"] for sh in sheets.values())
check("ledger file grand total", sum(r["barrels"] for r in ledger["ledger"]), stated_all)
check("ledger file contracts", len(ledger["ledger"]), len({(r["round"], r["company_as_listed"]) for r in ledger["ledger"]}))

# 1b. Post 3 figures for round 4 and FY27-1, recomputed from the sheet lines and company_map.csv.
rinfo = {r["round"]: r for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open())}
for rnd in ("4", "FY27-1"):
    sh, meta = sheets[rnd], rinfo[rnd]
    page = [r for r in ledger["ledger"] if r["round"] == rnd]
    check(f"post 3: round {rnd} award date on page", page[0]["award_date"], meta["award_date"])
    check(f"post 3: round {rnd} share of offered barrels taken, %", round(sh["total"] / int(meta["offered_bbl"]) * 100, 1),
          round(sum(r["barrels"] for r in page) / page[0]["offered_bbl"] * 100, 1))
    for ty in sorted(set(CMAP.values())):
        check(f"post 3: round {rnd} {ty} barrels", sum(b for n, b in sh["lines"] if CMAP[n] == ty), sum(r["barrels"] for r in page if r["type"] == ty))
    below = sorted(n for n, b in sh["lines"] if b < int(meta["min_offer_bbl"]))
    print(f"INFO post 3: round {rnd} awards below the {int(meta['min_offer_bbl']):,}-barrel minimum offer: {below}")
check("post 3: round 4 plus FY27-1", sheets["4"]["total"] + sheets["FY27-1"]["total"], 40550000)
chart = list(csv.DictReader((ROOT / "charts/01-newest-rounds.csv").open()))
for rnd in ("4", "FY27-1"):
    names = {r["company"]: r["company_as_listed"] for r in ledger["ledger"] if r["round"] == rnd}
    check(f"chart 01: round {rnd} bars match the award sheet",
          sorted((names[r["company"]], int(r["barrels"])) for r in chart if r["round"] == rnd), sorted(sheets[rnd]["lines"]))
    check(f"chart 01: round {rnd} type colors follow company_map",
          all(CMAP[names[r["company"]]] == r["type"] for r in chart if r["round"] == rnd), True)
    check(f"chart 01: round {rnd} offered", {int(r["offered_bbl"]) for r in chart if r["round"] == rnd}, {int(rinfo[rnd]["offered_bbl"])})

# 2. SPR weekly stocks on both ledger pages against the raw EIA response.
raw = {r["period"]: float(r["value"]) for r in json.loads((ROOT / "data/raw/eia/PET.WCSSTUS1.W.json").read_text()) if r["value"] is not None}
check("SPR weeks on ledger.html (frozen) match raw EIA", sum(1 for d, v in frozen["spr"] if raw.get(d) != v), 0)
check("SPR weeks on ledger file match raw EIA", sum(1 for d, v in ledger["spr"] if raw.get(d) != v), 0)
check("SPR latest week in eia_series.csv", ledger["spr"][-1][1], raw[max(raw)])

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
        check(f"trade {r['round']} barrels taken", r["taken"], sum(x["barrels"] for x in frozen["ledger"] if x["round"] == r["round"]))
        check(f"trade {r['round']} trader barrels", r["trader_taken"],
              sum(x["barrels"] for x in frozen["ledger"] if x["round"] == r["round"] and x["type"] == "Trading house"))

# 4. Returns page (frozen, post 1): both scenarios hold every barrel the frozen ledger holds.
#    The return schedule file, rebuilt with every round, must hold every barrel on the award sheets.
ret = page_data("returns.html")
for s in ("earliest", "latest"):
    check(f"returns.html (frozen) {s} total", sum(n for _, n in ret[s]), stated)
sched = list(csv.DictReader((ROOT / "data/processed/return_schedule.csv").open()))
for scen in sorted({r["scenario"] for r in sched}):
    check(f"return_schedule.csv {scen} total", sum(int(r["barrels"]) for r in sched if r["scenario"] == scen), stated_all)
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
check("2026 total matches the frozen ledger page (post 2 compare.html)", p26["total"], sum(r["barrels"] for r in frozen["ledger"]))
for t in p26["types"]:
    check(f"2026 type {t['type']}", t["barrels"], sum(r["barrels"] for r in frozen["ledger"] if r["type"] == t["type"]))
check("2026 borrowers", len(p26["firms"]), len({r["company"] for r in frozen["ledger"]}))

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
    for sid, key in (("PET.WPULEUS3.W", "refinery_utilization_pct"), ("PET.WCRRIUS2.W", "refiner_crude_inputs_weekly_kbd"), ("PET.WCREXUS2.W", "crude_exports_weekly_kbd"),
                     ("PET.W_NA_YUP_R30_PER.W", "gulf_refinery_utilization_pct"), ("PET.WCRRIP32.W", "gulf_refiner_crude_inputs_weekly_kbd"),
                     ("PET.WCEIMP32.W", "gulf_crude_imports_weekly_kbd")):
        raw = [float(x["value"]) for x in json.loads((ROOT / "data/raw/eia" / f"{sid}.json").read_text()) if x["value"] is not None and a <= x["period"] <= b]
        check(f"{year} {key}", m[key]["mean"], round(sum(raw) / len(raw), 1))

# 7. The comparison page carries the evidence file's figures unchanged.
check("page bids match the evidence file", {b["type"]: b["barrels_won"] for b in comp["bids"]},
      {t: b["barrels_won"] for t, b in bid_types.items() if t in comp["types"]})
check("page price gaps match the evidence file", comp["paf"], ev["paf_2022"])
agreements = list(csv.DictReader((ROOT / "data/reference/exchange_2021_22.csv").open()))
check("2021-22 loan total in the evidence file", ev["loans_2021_22"]["total"], sum(int(r["barrels"]) for r in agreements))
check("2021-22 agreements signed January 21 to 25 match DOE's release",
      sum(int(r["barrels"]) for r in agreements if "2022-01-21" <= r["signed"] <= "2022-01-25"), sum(listed.values()))
want = {}
for r in agreements:
    want[cmap[r["company_as_listed"]]["type"]] = want.get(cmap[r["company_as_listed"]]["type"], 0) + int(r["barrels"])
check("2021-22 loan types in the evidence file", {t: v["barrels"] for t, v in ev["loans_2021_22"]["by_type"].items()}, want)

# 8. Monthly Gulf Coast exports and Persian Gulf imports, and the loan return delays.
for year, m in ev["market"].items():
    for sid, key in (("PET.MCREXP32.M", "gulf_crude_exports_monthly_kbd"), ("PET.MCRIMUSPG2.M", "us_crude_imports_persian_gulf_monthly_kbd")):
        raw = {x["period"]: float(x["value"]) for x in json.loads((ROOT / "data/raw/eia" / f"{sid}.json").read_text()) if x["value"] is not None}
        check(f"{year} {key}", m[key]["mean"], round(sum(raw[p] for p in m[key]["months"]) / len(m[key]["months"]), 1))
mods = list(csv.DictReader((ROOT / "data/reference/exchange_2021_22_mods.csv").open()))
check("loan modifications keyed", len(mods), len(list((ROOT / "data/raw/doe_foia_2022").glob("*Mod*.pdf"))))
late = list(csv.DictReader((ROOT / "data/processed/spr_2021_22_return_delays.csv").open()))
check("loan agreements in the delay table", len(late), len(agreements))

# 9. Lot margins: the best lot in a round must equal the published trade card where both use the front-month price,
#    and each round's lots must add to the barrels offered.
lots = list(csv.DictReader((ROOT / "data/processed/lot_margins_2026.csv").open()))
for r in trade["rounds"]:
    if r["example"]["sale_basis"] == "front":
        check(f"lot margins, round {r['round']} best lot matches the trade page",
              max(float(l["left_per_barrel"]) for l in lots if l["round"] == r["round"]), r["example"]["left"])
held_to = max(r["date"] for r in csv.DictReader((ROOT / "data/processed/futures_closes.csv").open()))
for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open()):
    if r["bids_due"] > held_to:
        print(f"INFO lot margins: round {r['round']} not priced (bids due {r['bids_due']}, saved futures end {held_to})")
        continue
    check(f"lot margins, round {r['round']} barrels offered", sum(int(l["offered_bbl"]) for l in lots if l["round"] == r["round"]), int(r["offered_bbl"]))
for r in csv.DictReader((ROOT / "data/processed/round_uptake_2026.csv").open()):
    if r["taken_bbl"]:
        check(f"round {r['round']} uptake", int(r["taken_bbl"]), sum(x["barrels"] for x in ledger["ledger"] if x["round"] == r["round"]))

# 10. Purchases: dollars straight from each sheet's "totaling $" figure, and sheets counted by outcome.
bought = list(csv.DictReader((ROOT / "data/processed/spr_purchase_rounds.csv").open()))
dollars, none = 0, 0
for pdf in sorted((ROOT / "data/raw/doe_purchases").glob("*.pdf")):
    text = re.sub(r"\s+", " ", " ".join(p.extract_text() or "" for p in PdfReader(pdf).pages))
    m = re.search(r"totaling \$([\d,]+)\.00", text)
    dollars += int(m.group(1).replace(",", "")) if m else 0
    none += "NO AWARDS MADE" in text
check("purchase dollars", sum(int(r["dollars"]) for r in bought), dollars)
check("purchase solicitations with no award", sum(1 for r in bought if r["outcome"] != "Awarded"), none)
check("purchase barrels, seller lines against round totals",
      sum(int(r["barrels"]) for r in csv.DictReader((ROOT / "data/processed/spr_purchases.csv").open())), sum(int(r["barrels"]) for r in bought))

# 11. Where the 2022 sale money went: each keyed figure's phrase must be in its source (a page of a DOE report,
#     or the saved passages of the law and the Budget Appendix), and the totals are arithmetic on them.
squash = lambda s: re.sub(r"[^a-z0-9$.]", "", s.lower())
money = {}
for r in csv.DictReader((ROOT / "data/reference/sale_proceeds_2022.csv").open()):
    if r["source_file"].endswith(".pdf"):
        text = PdfReader(ROOT / "data/raw/doe_reports" / r["source_file"]).pages[int(r["pdf_page"]) - 1].extract_text() or ""
    else:
        text = (ROOT / "data/raw/law" / r["source_file"]).read_text()
    check(f"proceeds: '{r['item']}' is in {r['source_file']}", squash(r["check_phrase"]) in squash(text), True)
    money[r["item"]] = int(r["value"])
use = json.loads((ROOT / "data/processed/sale_proceeds_use.json").read_text())
both = money["Rescinded with the cancelled mandated sales"] + money["Rescinded in the annual energy appropriation"]
check("proceeds: two rescissions", use["rescinded_total"], both)
check("proceeds left after both rescissions", use["left_after_rescissions"], money["Received from the 2022 emergency sales"] - both)
check("purchases awarded through 2024", use["purchases_awarded_through_2024_dollars"], sum(int(r["dollars"]) for r in bought if r["as_of"][:4] <= "2024" and r["outcome"] == "Awarded"))
check("loan program: contract barrels within 1% of DOE's delivered total",
      abs(sum(int(r["barrels"]) for r in agreements) - money["Oil delivered under the 2021-22 Winter Exchange"]) / money["Oil delivered under the 2021-22 Winter Exchange"] < 0.01, True)

# 12. The money chart carries the proceeds file unchanged, and its three parts add to the money received.
pro = page_data("proceeds.html")
check("money chart matches the proceeds file", {k: pro[k] for k in use}, use)
check("money chart parts add to receipts", pro["rescinded_with_cancelled_sales"] + pro["rescinded_in_energy_appropriation"] + pro["left_after_rescissions"], pro["dollars_received"])

# 13. Post 3 chart 02 (the round 4 trade card): every lot and window recomputed from the raw futures files and
#     rfp_terms.csv; the card must show the best one. Sale = close of the contract for the month after pickup on the
#     bid due date; return price = mean close of the window's months that are served; margin = sale - (1 + premium) x return.
MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
def months_in(label):   # "Apr-Jun 2027", "Oct 2029", "Nov-Dec 2029"
    m = re.fullmatch(r"(\w{3})(?:-(\w{3}))? (\d{4})", label.strip())
    a, b, yr = MON.index(m.group(1)), MON.index(m.group(2) or m.group(1)), int(m.group(3))
    return [(yr, k + 1) for k in range(a, b + 1)]
day4 = rinfo["4"]["bids_due"]
cand = []
for t in terms:
    if t["round"] != "4":
        continue
    pm, py = MON.index(t["delivery_period"][:3]) + 1, int(t["delivery_period"][-4:])
    sale = wti(py + (pm == 12), pm % 12 + 1)[day4]
    for opt in t["return_options"].split(";"):
        label, add = opt.strip().rsplit(" ", 1)
        served = [(y, m) for y, m in months_in(label)
                  if (ROOT / "data/raw/futures" / f"CL{'FGHJKMNQUVXZ'[m - 1]}{y % 100:02d}.NYM.json").exists()]
        if len(served) < len(months_in(label)):
            print(f"INFO chart 02: {t['site']} {t['delivery_period']} {label} priced on {len(served)} of {len(months_in(label))} months")
        later = sum(wti(y, m)[day4] for y, m in served) / len(served)
        prem = float(t["min_premium_pct"]) + float(add)
        cand.append(dict(site=t["site"], pickup=t["delivery_period"], window=label, prem=prem, sale=sale, later=later,
                         left=sale - (1 + prem / 100) * later))
best = max(cand, key=lambda c: c["left"])
card = next(csv.DictReader((ROOT / "charts/02-round-4-profit.csv").open()))
check("chart 02: card shows the best lot and window", (card["site"], card["pickup"], card["return_window"]), (best["site"], best["pickup"], best["window"]))
check("chart 02: premium", float(card["premium_pct"]), best["prem"])
check("chart 02: sale price", float(card["sale_price"]), round(best["sale"], 2), 0.005)
check("chart 02: return price", float(card["return_price"]), round(best["later"], 2), 0.006)
check("chart 02: cost to return", float(card["cost_to_return"]), (1 + best["prem"] / 100) * best["later"], 0.011)
check("chart 02: left per barrel", float(card["left_per_barrel"]), best["left"], 0.011)
check("chart 02: bid-day price above return price, %", float(card["bid_day_price_above_return_price_pct"]), round((best["sale"] / best["later"] - 1) * 100, 1), 0.051)
check("chart 02: barrels taken and offered", (int(card["barrels_taken"]), int(card["barrels_offered"])), (sheets["4"]["total"], int(rinfo["4"]["offered_bbl"])))
traders4 = sum(b for n, b in sheets["4"]["lines"] if CMAP[n] == "Trading house")
check("chart 02: trading house barrels", int(card["trading_house_barrels"]), traders4)
check("chart 02: estimated profit = barrels x rounded margin", int(card["estimated_profit_trading_houses"]), round(traders4 * float(card["left_per_barrel"])))

# 14. Post 3 text: level after both rounds leave, when the reserve was last that low, trading-house share.
wk = {r["period"]: float(r["value"]) for r in json.loads((ROOT / "data/raw/eia/PET.WCSSTUS1.W.json").read_text()) if r["value"] is not None}
mo = {r["period"]: float(r["value"]) for r in json.loads((ROOT / "data/raw/eia/PET.MCSSTUS1.M.json").read_text()) if r["value"] is not None}
after = wk["2026-10-23"] * 1000 - (sheets["4"]["total"] + sheets["FY27-1"]["total"])
check("post 3: level after both rounds leave, barrels", after, 242033000)
check("post 3: last month at or below that level (end of month)", max(p for p, v in mo.items() if v * 1000 <= after and p < "2026"), "1982-02")
tr = sum(b for r in ("4", "FY27-1") for n, b in sheets[r]["lines"] if CMAP[n] == "Trading house")
check("post 3: trading houses across both rounds, %", round(tr / 40550000 * 100, 1), 49.8)

print(f"\n{len(fails)} failed" if fails else "\nall checks passed")
sys.exit(1 if fails else 0)
