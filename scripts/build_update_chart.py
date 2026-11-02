#!/usr/bin/env python3
"""Static charts for post 3 (round 4 and FY27-1).

Chart 01: who borrowed oil in round 4 and FY27-1.
  data/processed/spr_2026_exchange_awards.csv   from scripts/build_ledger.py
  data/reference/rounds.csv                     offered barrels, award dates, release names
Chart 02: post 1's round 4 trade card as a static image, results filled in (best lot and window).
  data/processed/trade_example_round_4.csv      from scripts/trade_math.py (bid day, saved futures)
  data/reference/rounds.csv                     bid due date

Outputs, in charts/: <name>.html (the chart as SVG in a page), <name>.png
(rendered by headless Chrome at 2x), <name>.csv (the values drawn).

Every figure is read from the inputs; nothing is typed in. Dark palette for
static PNGs. Firm-type hues are the ledger page's, stepped for the dark surface
(#181A1B) and checked with the dataviz palette validator (all checks pass).
Chart 02 uses the sale price post 1 used for round 4: the futures contract for
the month after pickup.
"""
import csv, datetime, html, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "charts"
ROUNDS = ["4", "FY27-1"]
BG, INK, BRIGHT, MUTED, GRID = "#181A1B", "#BBBDC0", "#E6E7E8", "#8C8F93", "#2E3133"
COLOR = {"Trading house": "#3987e5", "Major trading arm": "#d95926", "Refiner": "#199e70", "Midstream": "#c98500"}
BAR = "#3987e5"
TYPES = list(COLOR)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W = 1200
MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


def long_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{MONTHS[d.month - 1]} {d.day}, {d.year}"


def mil(n):
    return f"{n / 1e6:.3f}".rstrip("0").rstrip(".")


def money(v):
    return ("-$" if v < 0 else "$") + f"{abs(v):,.2f}"


class Svg:
    def __init__(self, width=W):
        self.parts, self.y, self.w = [], 0, width

    def text(self, x, y, txt, size=15, fill=INK, weight=400, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" '
                          f'text-anchor="{anchor}">{html.escape(txt)}</text>')

    def bar(self, x0, x1, y, h, fill):
        """Horizontal bar from the zero line x0 to x1, 4px rounded at the data end only."""
        r = min(4, abs(x1 - x0))
        if x1 >= x0:
            d = f"M{x0} {y} H{x1 - r} Q{x1} {y} {x1} {y + r} V{y + h - r} Q{x1} {y + h} {x1 - r} {y + h} H{x0} Z"
        else:
            d = f"M{x0} {y} H{x1 + r} Q{x1} {y} {x1} {y + r} V{y + h - r} Q{x1} {y + h} {x1 + r} {y + h} H{x0} Z"
        self.parts.append(f'<path d="{d}" fill="{fill}"/>')

    def line(self, x1, y1, x2, y2, stroke=GRID):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="1"/>')

    def render(self, name, rows, header):
        H, W = int(self.y + 24), self.w
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
               f'font-family="-apple-system, Helvetica Neue, Arial, sans-serif"><rect width="{W}" height="{H}" fill="{BG}"/>'
               + "".join(self.parts) + "</svg>")
        OUT.mkdir(exist_ok=True)
        page = OUT / f"{name}.html"
        page.write_text(f'<!doctype html><html><head><meta charset="utf-8"><title>{name}</title>'
                        f'<style>html,body{{margin:0;background:{BG}}}</style></head><body>{svg}</body></html>')
        with (OUT / f"{name}.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(header)
            w.writerows(rows)
        png = OUT / f"{name}.png"
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                        f"--window-size={W},{H}", f"--screenshot={png}", page.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"wrote {png.relative_to(ROOT)} ({W}x{H} at 2x), {len(rows)} rows")


def chart_awards(rounds):
    ledger = list(csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open()))
    rows = [r for r in ledger if r["round"] in ROUNDS]
    for r in rows:
        r["barrels"] = int(r["barrels"])
        if r["type"] not in COLOR:
            sys.exit(f"no color for type {r['type']}")
    keys = [(r["round"], r["company"]) for r in rows]
    if len(set(keys)) != len(keys):
        sys.exit("duplicate round and company")   # hard failure by house rule

    vmax = max(r["barrels"] for r in rows)
    label_w, right_pad, bar_h, gap = 300, 120, 26, 10
    x0 = label_w + 24
    x = lambda v: x0 + v / vmax * (W - 48 - label_w - right_pad)
    s = Svg()
    s.y += 40; s.text(24, s.y, "Who borrowed oil in the two newest rounds", 28, BRIGHT, 700)
    s.y += 30; s.text(24, s.y, "Million barrels awarded to each company. Bar color is the type of company.", 16)
    s.y += 30
    xw = 24
    for ty in TYPES:   # legend as colored words
        s.text(xw, s.y, ty, 16, COLOR[ty], 700)
        xw += 16 + 9.2 * len(ty)
    s.y += 18
    for rnd in ROUNDS:
        meta = rounds[rnd]
        mine = sorted([r for r in rows if r["round"] == rnd], key=lambda r: -r["barrels"])
        taken, offered = sum(r["barrels"] for r in mine), int(meta["offered_bbl"])
        s.y += 38; s.text(24, s.y, f"{meta['release_name'].replace(' SPR Oil', '')}: {mil(taken)} of {mil(offered)} "
                                   f"million barrels offered ({taken / offered * 100:.1f}%)", 19, BRIGHT, 700)
        s.y += 22; s.text(24, s.y, f"Awards as of {long_date(meta['award_date'])}", 14, MUTED)
        s.y += 14
        top = s.y
        for r in mine:
            s.y += gap
            s.text(label_w + 12, s.y + bar_h / 2 + 5, r["company"], 15, anchor="end")
            s.bar(x0, x(r["barrels"]), s.y, bar_h, COLOR[r["type"]])
            s.text(x(r["barrels"]) + 8, s.y + bar_h / 2 + 5, mil(r["barrels"]), 15, weight=700)
            s.y += bar_h
        s.line(x0, top, x0, s.y)
    s.y += 44; s.text(24, s.y, "Source: U.S. Department of Energy award sheets and requests for proposals (spr.doe.gov). Type of company is our classification.", 13, MUTED)
    s.y += 20; s.text(24, s.y, "These are loans: the oil is owed back with extra barrels. DOE publishes barrels awarded, not barrels delivered.", 13, MUTED)
    s.y += 20; s.text(24, s.y, "Built by Data 4 The People", 13, INK, 700)
    out = [[r["round"], rounds[r["round"]]["release_name"], rounds[r["round"]]["award_date"], rounds[r["round"]]["offered_bbl"],
            r["company"], r["type"], r["barrels"]]
           for r in sorted(rows, key=lambda r: (ROUNDS.index(r["round"]), -r["barrels"]))]
    s.render("01-newest-rounds", out, ["round", "release_name", "award_date", "offered_bbl", "company", "type", "barrels"])


def chart_profit(rounds):
    """Post 1's round 4 trade card, as a static image, with the results filled in."""
    meta = rounds["4"]
    rows = [r for r in csv.DictReader((ROOT / "data/processed/trade_example_round_4.csv").open())
            if r["priced_on"] == "bids due"]
    if not rows or {r["date"] for r in rows} != {meta["bids_due"]}:
        sys.exit("round 4 trade example is not priced on the bid due date")
    for r in rows:
        for k in ("premium_pct", "return_price", "cost_to_return", "sale_delivery_contract", "margin_delivery_contract",
                  "breakeven_premium_delivery_pct"):
            r[k] = float(r[k])
    e = max(rows, key=lambda r: r["margin_delivery_contract"])   # the card shows the best lot and window, as in post 1
    sale, prem, later, cost, left = (e["sale_delivery_contract"], e["premium_pct"], e["return_price"],
                                     e["cost_to_return"], e["margin_delivery_contract"])
    if abs(sale - (1 + prem / 100) * later - left) > 0.011 or abs(sale - cost - left) > 0.011:
        sys.exit("card arithmetic does not hold")
    ledger = [r for r in csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open()) if r["round"] == "4"]
    taken, offered = sum(int(r["barrels"]) for r in ledger), int(meta["offered_bbl"])
    traders = sum(int(r["barrels"]) for r in ledger if r["type"] == "Trading house")
    profit = left * traders
    big = profit / 1e6
    big_txt = f"${round(big):,} million" if big >= 10 else f"${big:.1f} million"   # post 1's rounding
    win = " to ".join(MONTHS[["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"].index(m)]
                      for m in e["return_window"][:7].split("-")) + " " + e["return_window"][-4:]

    CW, L, R = 640, 32, 608
    s = Svg(CW)
    s.y += 44; s.text(L, s.y, "October round", 26, BRIGHT, 700)
    s.y += 26; s.text(L, s.y, f"Round 4. Bids due {long_date(meta['bids_due'])}", 15, MUTED)
    s.y += 26; s.text(L, s.y, f"Companies took {mil(taken)} million of the {mil(offered)} million barrels offered ({taken / offered * 100:.1f}%).", 15)
    x = lambda v: L + v / sale * (R - L)
    def row(label, value, segs):
        s.y += 34; s.text(L, s.y, label, 16, BRIGHT); s.text(R, s.y, money(value), 16, BRIGHT, 700, "end")
        s.y += 10; at = 0
        for j, (v, fill) in enumerate(segs):
            x0 = x(at) + (2 if j else 0)
            s.parts.append(f'<rect x="{x0:.1f}" y="{s.y}" width="{max(x(at + v) - x0, 1.5):.1f}" height="24" rx="4" fill="{fill}"/>')
            at += v
        s.y += 24
    row("Sell one barrel now", sale, [(sale, "#3987e5")])
    row(f"Buy back 1 barrel + {prem:g}% extra", cost, [(later, "#d95926"), (cost - later, "#c98500")])
    row("Left over", left, [(left, "#199e70")])
    s.y += 22; s.line(L, s.y, R, s.y)
    s.y += 28; s.text(L, s.y, "Left over per barrel", 15, MUTED)
    s.y += 44; s.text(L, s.y, money(left), 44, BRIGHT, 700)
    s.y += 20; s.line(L, s.y, R, s.y)
    s.y += 28; s.text(L, s.y, "How much higher the price on bid day was than", 16); s.text(R, s.y, f"{e['breakeven_premium_delivery_pct']:g}%", 16, BRIGHT, 700, "end")
    s.y += 22; s.text(L, s.y, f"the price for {win}", 16)
    s.y += 14; s.line(L, s.y, R, s.y)
    s.y += 28; s.text(L, s.y, "Extra oil the government asked for", 16); s.text(R, s.y, f"{prem:g}%", 16, BRIGHT, 700, "end")
    s.y += 14; s.line(L, s.y, R, s.y)
    s.y += 28; s.text(L, s.y, "Estimated profit before transportation costs, if prices", 15, MUTED)
    s.y += 20; s.text(L, s.y, "were locked in the day bids were due", 15, MUTED)
    s.y += 40; s.text(L, s.y, big_txt, 34, BRIGHT, 700)
    s.y += 26; s.text(L, s.y, f"Trading companies borrowed {mil(traders)} million barrels, times {money(left)}.", 15)
    s.y += 22; s.text(L, s.y, "The real figure could be much lower or higher.", 15)
    s.y += 36; s.text(L, s.y, f"Best lot and return window: {e['site']}, {e['delivery']} pickup, returned {e['return_window']}, at the", 12, MUTED)
    s.y += 17; s.text(L, s.y, "lowest premium allowed. Bids above the minimum would leave less. Sale price is the futures contract", 12, MUTED)
    s.y += 17; s.text(L, s.y, "for the month after pickup. Leaves out shipping, crude quality, the bank guarantee and interest.", 12, MUTED)
    s.y += 17; s.text(L, s.y, "Sources: U.S. Department of Energy award sheet and RFP DE-RP96-26PO00006; NYMEX WTI", 12, MUTED)
    s.y += 17; s.text(L, s.y, "futures closes as relayed by Yahoo Finance, retrieved October 11, 2026.", 12, MUTED)
    s.y += 22; s.text(L, s.y, "Built by Data 4 The People", 12, INK, 700)
    s.render("02-round-4-profit", [[meta["bids_due"], e["site"], e["delivery"], e["return_window"], prem, sale, later, cost, left,
                                    e["breakeven_premium_delivery_pct"], taken, offered, traders, round(profit)]],
             ["bids_due", "site", "pickup", "return_window", "premium_pct", "sale_price", "return_price", "cost_to_return",
              "left_per_barrel", "bid_day_price_above_return_price_pct", "barrels_taken", "barrels_offered",
              "trading_house_barrels", "estimated_profit_trading_houses"])


def main():
    rounds = {r["round"]: r for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open())}
    chart_awards(rounds)
    chart_profit(rounds)


if __name__ == "__main__":
    main()
