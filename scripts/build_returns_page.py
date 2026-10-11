#!/usr/bin/env python3
"""Build dist/returns.html, the "when is the oil due back" chart.

Inputs
  data/processed/return_schedule.csv   from scripts/return_schedule.py (re-run here)
  scripts/returns_template.html, logo/d4tp-text-dark.svg
Output
  dist/returns.html   self-contained page, data inlined, no CDN

Every number on the page is computed from the inlined schedule at render time.
"""
import base64, csv, datetime, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    subprocess.run([sys.executable, str(ROOT / "scripts/return_schedule.py")], check=True, capture_output=True)
    rows = list(csv.DictReader((ROOT / "data/processed/return_schedule.csv").open()))
    data = dict(built=datetime.date.today().isoformat())
    for scenario in ("earliest", "latest"):
        by_date = {}
        for r in rows:
            if r["scenario"] == scenario:
                by_date[r["date"]] = by_date.get(r["date"], 0) + int(r["barrels"])
        data[scenario] = sorted(by_date.items())
    if sum(n for _, n in data["earliest"]) != sum(n for _, n in data["latest"]):
        sys.exit("the two scenarios do not hold the same barrels")
    logo = "data:image/svg+xml;base64," + base64.b64encode((ROOT / "logo/d4tp-text-dark.svg").read_bytes()).decode()
    html = (ROOT / "scripts/returns_template.html").read_text()
    if "/*__DATA__*/null" not in html or "__LOGO__" not in html:
        sys.exit("template slots missing")
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))).replace("__LOGO__", logo)
    out = ROOT / "dist/returns.html"
    out.write_text(html)
    print(f"wrote {out.relative_to(ROOT)}: {len(html):,} bytes")


if __name__ == "__main__":
    main()
