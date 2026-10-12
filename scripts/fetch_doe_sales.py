#!/usr/bin/env python3
"""Download DOE's reports for the 2022 emergency crude oil sales.

DOE lists its closed sales as a JSON feed at
  https://www.spr.doe.gov/posting/SALE/archive/
Each sale folder holds a "1-Reports" folder with the Notice of Sale and three
reports from DOE's offer evaluation program: Offeror Abstract, Apparently
Successful Offers, and Successful Awards.

This pulls every file in "1-Reports" for the seven emergency sales (folders
12 to 18, "FY22 Emergency Drawdown" to "FY23 Emergency Drawdown No. 3D") into
data/raw/doe_sales_2022/ and writes manifest.json with the URL, size and
SHA-256 of each. The folder listing is saved beside them.
"""
import datetime, hashlib, json, os, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import load_env, get_key

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.spr.doe.gov/posting/SALE/archive/"
OUT = ROOT / "data/raw/doe_sales_2022"
FOLDERS = range(12, 19)     # DOE numbers its sale folders; 12 to 18 are the emergency sales


def get(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    load_env()
    ua = f"Data4ThePeople research ({get_key('D4TP_CONTACT_EMAIL')})"   # read at run time, never stored here
    today = datetime.date.today().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    listing = get(BASE, ua)
    (OUT / f"sale_archive_listing_{today}.json").write_bytes(listing)
    manifest, seen = [], set()
    for rel in sorted(json.loads(listing), key=lambda r: r["name"]):
        if not rel["name"][:2].isdigit() or int(rel["name"][:2]) not in FOLDERS:
            continue
        for folder in rel["folders"]:
            if folder["name"] != "1-Reports":
                continue
            for f in folder["files"]:
                if f["name"] in seen:
                    sys.exit(f"duplicate file name {f['name']}")   # hard failure by house rule
                seen.add(f["name"])
                url = BASE + urllib.parse.quote(f"{rel['name']}/{folder['name']}/{f['name']}")
                body = get(url, ua)
                (OUT / f["name"]).write_bytes(body)
                manifest.append(dict(sale=rel["name"], file=f["name"], url=url, bytes=len(body),
                                     sha256=hashlib.sha256(body).hexdigest(), is_pdf=body.startswith(b"%PDF"),
                                     posted=f["timeLastModified"], retrieved=today))
                print(f"{f['name']}: {len(body):,} bytes")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"wrote {len(manifest)} files and manifest.json to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
