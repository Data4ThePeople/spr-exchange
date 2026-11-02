#!/usr/bin/env python3
"""Static charts for post 3 (round 4 and FY27-1).

Chart 01: who borrowed oil in round 4 and FY27-1.
  data/processed/spr_2026_exchange_awards.csv   from scripts/build_ledger.py
  data/reference/rounds.csv                     offered barrels, award dates, release names
Chart 02: what round 4 borrowers could make per barrel, every lot and return window.
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
    def __init__(self):
        self.parts, self.y = [], 0

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
        H = int(self.y + 24)
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
    meta = rounds["4"]
    rows = [r for r in csv.DictReader((ROOT / "data/processed/trade_example_round_4.csv").open())
            if r["priced_on"] == "bids due"]
    if not rows or {r["date"] for r in rows} != {meta["bids_due"]}:
        sys.exit("round 4 trade example is not priced on the bid due date")
    keys = [(r["site"], r["delivery"], r["return_window"]) for r in rows]
    if len(set(keys)) != len(keys):
        sys.exit("duplicate lot and window")
    for r in rows:
        for k in ("premium_pct", "return_price", "cost_to_return", "sale_delivery_contract", "margin_delivery_contract"):
            r[k] = float(r[k])
        # the margin must follow from the parts shown on the chart
        if abs(r["sale_delivery_contract"] - (1 + r["premium_pct"] / 100) * r["return_price"] - r["margin_delivery_contract"]) > 0.011:
            sys.exit(f"margin does not follow from its parts: {r}")
    best = max(rows, key=lambda r: r["margin_delivery_contract"])
    lots = []
    for r in rows:
        if (r["site"], r["delivery"]) not in lots:
            lots.append((r["site"], r["delivery"]))

    vals = [r["margin_delivery_contract"] for r in rows]
    lo, hi = min(0, min(vals)), max(vals)
    label_w, right_pad, bar_h, gap = 430, 90, 22, 8
    plot_l = label_w + 100   # room for a negative bar and its label left of zero
    x = lambda v: plot_l + (v - lo) / (hi - lo) * (W - 24 - plot_l - right_pad)
    s = Svg()
    s.y += 40; s.text(24, s.y, "What round 4 borrowers could make per barrel", 28, BRIGHT, 700)
    s.y += 30; s.text(24, s.y, f"Dollars per barrel borrowed, using futures prices on {long_date(meta['bids_due'])}, the day bids were due, and the lowest premium allowed.", 16)
    s.y += 22; s.text(24, s.y, "The borrower sells the oil now and locks in the price of the oil it owes back by buying futures for the return months.", 16)
    owe = 1 + best["premium_pct"] / 100
    s.y += 40; s.text(24, s.y, "The math for the best lot and window", 17, BRIGHT, 700)
    s.y += 26; s.text(24, s.y, f"{best['site']}, {best['delivery']} pickup, returned {best['return_window']}:", 16)
    s.y += 24; s.text(44, s.y, f"Sell 1 barrel at the futures price for the month after pickup: {money(best['sale_delivery_contract'])}", 16)
    s.y += 24; s.text(44, s.y, f"Owe {owe:.3f} barrels back ({best['premium_pct']:g}% extra), bought ahead at {money(best['return_price'])} each: "
                               f"{money(best['cost_to_return'])}", 16)
    s.y += 24; s.text(44, s.y, f"Left per barrel borrowed: {money(best['sale_delivery_contract'])} - {money(best['cost_to_return'])} = "
                               f"{money(best['margin_delivery_contract'])}", 16, BRIGHT, 700)
    s.y += 16
    out = []
    for site, deliv in lots:
        mine = [r for r in rows if r["site"] == site and r["delivery"] == deliv]
        s.y += 36; s.text(24, s.y, f"{site}, {deliv} pickup (sold at {money(mine[0]['sale_delivery_contract'])})", 17, BRIGHT, 700)
        s.y += 8
        top = s.y
        for r in mine:
            s.y += gap
            v = r["margin_delivery_contract"]
            s.text(label_w + 12, s.y + bar_h / 2 + 5, f"Returned {r['return_window']}, {r['premium_pct']:g}% extra owed", 15, anchor="end")
            s.bar(x(0), x(v), s.y, bar_h, BAR)
            s.text(x(v) + (8 if v >= 0 else -8), s.y + bar_h / 2 + 5, money(v), 15, weight=700, anchor="start" if v >= 0 else "end")
            s.y += bar_h
            out.append([site, deliv, r["return_window"], r["premium_pct"], r["sale_delivery_contract"], r["return_price"],
                        r["cost_to_return"], v])
        s.line(x(0), top, x(0), s.y, "#5A5E62")
    s.y += 40; s.text(24, s.y, "This is the most a borrower could make: the premium each company bid is not public and can be higher than the minimum.", 13, MUTED)
    s.y += 20; s.text(24, s.y, "Leaves out shipping, differences in crude quality, the cost of the required bank guarantee, and interest on the sale money.", 13, MUTED)
    s.y += 20; s.text(24, s.y, "Source: U.S. Department of Energy request for proposals DE-RP96-26PO00006; NYMEX WTI futures closes as relayed by Yahoo Finance,", 13, MUTED)
    s.y += 20; s.text(24, s.y, "retrieved October 11, 2026. A return price is the average of the window's monthly contracts; Yahoo does not serve September and", 13, MUTED)
    s.y += 20; s.text(24, s.y, "October 2029, so Aug-Oct 2029 uses August alone.", 13, MUTED)
    s.y += 20; s.text(24, s.y, "Built by Data 4 The People", 13, INK, 700)
    s.render("02-round-4-profit", out, ["site", "pickup", "return_window", "premium_pct", "sale_price", "return_price",
                                         "cost_to_return_per_barrel_borrowed", "left_per_barrel"])


def main():
    rounds = {r["round"]: r for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open())}
    chart_awards(rounds)
    chart_profit(rounds)


if __name__ == "__main__":
    main()
