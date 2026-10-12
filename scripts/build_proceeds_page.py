#!/usr/bin/env python3
"""Build dist/proceeds.html: where the money from the 2022 emergency oil sales went.

Inputs
  data/processed/sale_proceeds_use.json   from scripts/sale_proceeds.py
  scripts/proceeds_template.html, logo/d4tp-text-dark.svg

Output
  dist/proceeds.html   self-contained page, data inlined, no CDN

Every number on the page comes from the inlined data; the template holds none.
"""
import base64, datetime, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    use = json.loads((ROOT / "data/processed/sale_proceeds_use.json").read_text())
    parts = [use["rescinded_with_cancelled_sales"], use["rescinded_in_energy_appropriation"], use["left_after_rescissions"]]
    if sum(parts) != use["dollars_received"]:
        sys.exit("the three parts do not add to the money received")
    data = dict(built=datetime.date.today().isoformat(), **use)
    logo = "data:image/svg+xml;base64," + base64.b64encode((ROOT / "logo/d4tp-text-dark.svg").read_bytes()).decode()
    html = (ROOT / "scripts/proceeds_template.html").read_text()
    if "/*__DATA__*/null" not in html or "__LOGO__" not in html:
        sys.exit("template slots missing")
    html = html.replace("/*__DATA__*/null", json.dumps(data, separators=(",", ":"))).replace("__LOGO__", logo)
    out = ROOT / "dist/proceeds.html"
    out.write_text(html)
    print(f"wrote {out.relative_to(ROOT)}: {len(html):,} bytes")


if __name__ == "__main__":
    main()
