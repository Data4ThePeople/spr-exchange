#!/usr/bin/env python3
"""Build the ledger of crude oil DOE bought for the reserve, 2023 to 2025.

Reads every "Award Information" PDF in data/raw/doe_purchases/
(scripts/fetch_doe_purchases.py). Each one-page sheet gives an "as of" date, the
barrels bought, the total dollars, and one line per seller with its barrels; a
sheet marked "NO AWARDS MADE" gives nothing else.

DOE writes quantities three ways on these sheets ("3.25MMB", "600MB",
"2,774,658 barrels", and sometimes a full barrel count followed by "MMB" or
"MB"). A number of 1,000 or more is read as barrels; otherwise MMB is millions
and MB is thousands. The build stops unless each sheet's seller lines add to
its stated total, to within 10 barrels.

The sheets give one dollar total per solicitation, not a price per seller, so
price per barrel is the sheet's dollars over its barrels.

Writes data/processed/spr_purchases.csv (one row per seller and solicitation)
and data/processed/spr_purchase_rounds.csv (one row per solicitation, including
those with no award).
"""
import csv, datetime, json, re, sys
from pathlib import Path
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/doe_purchases"
QTY = r"([\d,]*\.?\d+) ?(MMB|MB|barrels)"


def barrels(num, unit):
    v = float(num.replace(",", ""))
    if v >= 1000:
        return round(v)                     # a full barrel count, whatever unit follows it
    return round(v * (1e6 if unit == "MMB" else 1e3 if unit == "MB" else 1))


def main():
    cmap = {r["company_as_listed"]: r for r in csv.DictReader((ROOT / "data/reference/company_map.csv").open())}
    meta = {m["file"]: m for m in json.loads((RAW / "manifest.json").read_text()) if m["file"]}
    lines, rounds, seen = [], [], set()
    for pdf in sorted(RAW.glob("*Award Information*.pdf")):
        text = " ".join(" ".join((p.extract_text() or "").split()) for p in PdfReader(pdf).pages)
        sol = re.search(r"Solicitation No\. (\w+)", text)
        base = dict(solicitation=meta[pdf.name]["solicitation"], solicitation_no=sol.group(1) if sol else "",
                    source_pdf=pdf.name, source_url=meta[pdf.name]["url"])
        if "NO AWARDS MADE" in text:
            rounds.append(dict(base, as_of="", barrels=0, dollars=0, price_per_barrel="", sellers=0, outcome="No awards made"))
            continue
        head = re.search(r"As of (\w+ \d+, \d{4}),? the following contracts? for the purchase of " + QTY + r", totaling \$([\d,]+)\.00", text)
        if not head:
            sys.exit(f"{pdf.name}: cannot read the total line")
        date = datetime.datetime.strptime(head.group(1), "%B %d, %Y").date().isoformat()
        total, dollars = barrels(head.group(2), head.group(3)), int(head.group(4).replace(",", ""))
        body = text[text.rindex(":") + 1:] if ":" in text[head.end():] else text[head.end():]
        got = [(n.strip(), barrels(q, u)) for n, q, u in re.findall(r"(.+?) [–-] " + QTY, body)]
        if abs(sum(b for _, b in got) - total) > 10:
            sys.exit(f"{pdf.name}: seller lines add to {sum(b for _, b in got):,}, sheet says {total:,}")
        for name, b in got:
            key = (base["solicitation"], name)
            if key in seen:
                sys.exit(f"duplicate key {key}")   # hard failure by house rule
            seen.add(key)
            if name not in cmap:
                sys.exit(f"'{name}' is not in company_map.csv")
            lines.append(dict(base, as_of=date, company_as_listed=name, company=cmap[name]["company"], type=cmap[name]["type"], barrels=b))
        rounds.append(dict(base, as_of=date, barrels=sum(b for _, b in got), dollars=dollars,
                           price_per_barrel=round(dollars / sum(b for _, b in got), 2), sellers=len(got), outcome="Awarded"))
    rounds.sort(key=lambda r: (r["as_of"] or "9999", r["solicitation"]))
    lines.sort(key=lambda r: (r["as_of"], r["solicitation"], r["company_as_listed"]))
    for name, rows in (("spr_purchases.csv", lines), ("spr_purchase_rounds.csv", rounds)):
        with (ROOT / "data/processed" / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    won = [r for r in rounds if r["outcome"] == "Awarded"]
    bbl, usd = sum(r["barrels"] for r in won), sum(r["dollars"] for r in won)
    print(f"{len(rounds)} solicitations: {len(won)} awarded, {len(rounds) - len(won)} with no awards")
    print(f"bought {bbl:,} barrels for ${usd:,}, an average of ${usd / bbl:.2f} a barrel; "
          f"awards dated {won[0]['as_of']} to {won[-1]['as_of']}; {len({l['company'] for l in lines})} sellers")
    for y in sorted({r["as_of"][:4] for r in won}):
        sub = [r for r in won if r["as_of"][:4] == y]
        print(f"  awarded in {y}: {sum(r['barrels'] for r in sub):,} barrels, ${sum(r['dollars'] for r in sub):,}, "
              f"${sum(r['dollars'] for r in sub) / sum(r['barrels'] for r in sub):.2f} a barrel")
    by = {}
    for l in lines:
        by[l["company"]] = by.get(l["company"], 0) + l["barrels"]
    for c, v in sorted(by.items(), key=lambda x: -x[1]):
        print(f"  {v:>11,} {v / bbl * 100:5.1f}%  {c}")
    types = {}
    for l in lines:
        types[l["type"]] = types.get(l["type"], 0) + l["barrels"]
    print("  " + ", ".join(f"{t} {v / bbl * 100:.1f}%" for t, v in sorted(types.items(), key=lambda x: -x[1])))


if __name__ == "__main__":
    main()
