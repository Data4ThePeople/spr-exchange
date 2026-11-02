#!/usr/bin/env python3
"""Static chart for post 3: who borrowed oil in round 4 and FY27-1.

Inputs
  data/processed/spr_2026_exchange_awards.csv   from scripts/build_ledger.py
  data/reference/rounds.csv                     offered barrels, award dates, release names

Output
  charts/01-newest-rounds.html   the chart as SVG in a page (dark palette, house rules for static PNGs)
  charts/01-newest-rounds.png    rendered by headless Chrome at 2x
  charts/01-newest-rounds.csv    the rows drawn, one per contract

Every figure is read from the inputs; nothing is typed in. Colors are the
ledger page's firm-type hues, stepped for the dark surface (#181A1B) and
checked with the dataviz palette validator (all checks pass).
"""
import csv, datetime, html, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "charts"
ROUNDS = ["4", "FY27-1"]
BG, INK, MUTED, GRID = "#181A1B", "#BBBDC0", "#8C8F93", "#2E3133"
COLOR = {"Trading house": "#3987e5", "Major trading arm": "#d95926", "Refiner": "#199e70", "Midstream": "#c98500"}
TYPES = list(COLOR)
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
W = 1200


def long_date(iso):
    d = datetime.date.fromisoformat(iso)
    return f"{d.strftime('%B')} {d.day}, {d.year}"


def mil(n):
    return f"{n / 1e6:.3f}".rstrip("0").rstrip(".")


def main():
    ledger = list(csv.DictReader((ROOT / "data/processed/spr_2026_exchange_awards.csv").open()))
    rounds = {r["round"]: r for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open())}
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
    plot_w = W - 48 - label_w - right_pad
    x = lambda v: label_w + 24 + v / vmax * plot_w

    s, y = [], 0
    t = lambda x0, y0, txt, size=15, fill=INK, weight=400, anchor="start": s.append(
        f'<text x="{x0}" y="{y0}" font-size="{size}" fill="{fill}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(txt)}</text>')
    y += 40; t(24, y, "Who borrowed oil in the two newest rounds", 28, "#E6E7E8", 700)
    y += 30; t(24, y, "Million barrels awarded to each company. Bar color is the type of company.", 16, INK)
    y += 30
    xw = 24
    for ty in TYPES:   # legend as colored words
        s.append(f'<text x="{xw}" y="{y}" font-size="16" font-weight="700" fill="{COLOR[ty]}">{ty}</text>')
        xw += 16 + 9.2 * len(ty)
    y += 18
    for rnd in ROUNDS:
        meta = rounds[rnd]
        mine = sorted([r for r in rows if r["round"] == rnd], key=lambda r: -r["barrels"])
        taken, offered = sum(r["barrels"] for r in mine), int(meta["offered_bbl"])
        name = meta["release_name"].replace(" SPR Oil", "")
        y += 38; t(24, y, f"{name}: {mil(taken)} of {mil(offered)} million barrels offered ({taken / offered * 100:.1f}%)", 19, "#E6E7E8", 700)
        y += 22; t(24, y, f"Awards as of {long_date(meta['award_date'])}", 14, MUTED)
        y += 14
        for r in mine:
            y += gap
            x1 = x(r["barrels"]); x0 = label_w + 24
            s.append(f'<text x="{label_w + 12}" y="{y + bar_h / 2 + 5}" font-size="15" fill="{INK}" text-anchor="end">{html.escape(r["company"])}</text>')
            s.append(f'<path d="M{x0} {y} H{x1 - 4} Q{x1} {y} {x1} {y + 4} V{y + bar_h - 4} Q{x1} {y + bar_h} {x1 - 4} {y + bar_h} H{x0} Z" fill="{COLOR[r["type"]]}"/>')
            s.append(f'<text x="{x1 + 8}" y="{y + bar_h / 2 + 5}" font-size="15" fill="{INK}" font-weight="700">{mil(r["barrels"])}</text>')
            y += bar_h
        s.append(f'<line x1="{label_w + 24}" x2="{label_w + 24}" y1="{y - len(mine) * (bar_h + gap)}" y2="{y}" stroke="{GRID}" stroke-width="1"/>')
    y += 44
    t(24, y, "Source: U.S. Department of Energy award sheets and requests for proposals (spr.doe.gov). Type of company is our classification.", 13, MUTED)
    y += 20
    t(24, y, "Barrels awarded are loans owed back with extra barrels, and are not the same as barrels delivered.", 13, MUTED)
    y += 20
    t(24, y, "Built by Data 4 The People", 13, INK, 700)
    H = int(y + 24)

    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
           f'font-family="-apple-system, Helvetica Neue, Arial, sans-serif"><rect width="{W}" height="{H}" fill="{BG}"/>' + "".join(s) + "</svg>")
    OUT.mkdir(exist_ok=True)
    page = OUT / "01-newest-rounds.html"
    page.write_text(f'<!doctype html><html><head><meta charset="utf-8"><title>Newest rounds</title>'
                    f'<style>html,body{{margin:0;background:{BG}}}</style></head><body>{svg}</body></html>')
    with (OUT / "01-newest-rounds.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["round", "release_name", "award_date", "offered_bbl", "company", "type", "barrels"])
        for r in sorted(rows, key=lambda r: (ROUNDS.index(r["round"]), -r["barrels"])):
            m = rounds[r["round"]]
            w.writerow([r["round"], m["release_name"], m["award_date"], m["offered_bbl"], r["company"], r["type"], r["barrels"]])
    png = OUT / "01-newest-rounds.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=2",
                    f"--window-size={W},{H}", f"--screenshot={png}", page.as_uri()],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"wrote {png.relative_to(ROOT)} ({W}x{H} at 2x), {len(rows)} contracts")


if __name__ == "__main__":
    main()
