#!/usr/bin/env python3
"""Download DOE's award sheets for its crude oil purchases for the reserve.

DOE lists its purchase solicitations as JSON feeds at
  https://www.spr.doe.gov/posting/PURCHASE/archive/   closed
  https://www.spr.doe.gov/posting/PURCHASE/current/   open
Each solicitation's first folder holds an "Award Information" PDF once DOE has
decided it, including the ones marked "NO AWARDS MADE".

This pulls every file with "Award Information" in its name into
data/raw/doe_purchases/ and writes manifest.json (solicitation, URL, bytes,
SHA-256, DOE's posting date), plus dated copies of both listings.
"""
import datetime, hashlib, json, os, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import load_env, get_key

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.spr.doe.gov/posting/PURCHASE/"
OUT = ROOT / "data/raw/doe_purchases"


def get(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    load_env()
    ua = f"Data4ThePeople research ({get_key('D4TP_CONTACT_EMAIL')})"   # read at run time, never stored here
    today = datetime.date.today().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    manifest, seen = [], set()
    for where in ("archive", "current"):
        listing = get(BASE + where + "/", ua)
        (OUT / f"purchase_{where}_listing_{today}.json").write_bytes(listing)
        for rel in json.loads(listing):
            found = False
            for folder in rel["folders"]:
                for f in folder["files"]:
                    if "award information" not in f["name"].lower():
                        continue
                    if f["name"] in seen:
                        sys.exit(f"duplicate file name {f['name']}")   # hard failure by house rule
                    seen.add(f["name"])
                    # Closed solicitations are served under archive/. Open ones are served with no folder prefix.
                    path = f"{rel['name']}/{folder['name']}/{f['name']}"
                    url = BASE + urllib.parse.quote(f"archive/{path}" if where == "archive" else path)
                    body = get(url, ua)
                    if not body.startswith(b"%PDF"):
                        sys.exit(f"{f['name']}: download is not a PDF")
                    (OUT / f["name"]).write_bytes(body)
                    manifest.append(dict(solicitation=rel["name"], listing=where, file=f["name"], url=url, bytes=len(body),
                                         sha256=hashlib.sha256(body).hexdigest(), is_pdf=body.startswith(b"%PDF"),
                                         posted=f["timeLastModified"], retrieved=today))
                    found = True
            if not found:
                manifest.append(dict(solicitation=rel["name"], listing=where, file="", url="", bytes=0, sha256="",
                                     is_pdf=False, posted="", retrieved=today))
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"{sum(1 for m in manifest if m['file'])} award sheets from {len(manifest)} solicitations in {OUT.relative_to(ROOT)}")
    for m in manifest:
        if not m["file"]:
            print("  no award sheet:", m["solicitation"])


if __name__ == "__main__":
    main()
