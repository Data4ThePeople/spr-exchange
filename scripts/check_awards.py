#!/usr/bin/env python3
"""Check DOE's exchange folders for award sheets and rounds we do not hold yet.

DOE lists its exchange documents as a JSON feed at
  https://www.spr.doe.gov/posting/EXCHANGE/current/   open rounds
  https://www.spr.doe.gov/posting/EXCHANGE/archive/   closed rounds
A round moves from current/ to archive/ after it closes, so both are read.

Any "Award Information" PDF that is not in data/raw/doe_awards/ is downloaded
there. Any release that is not in data/reference/rounds.csv is reported.
Nothing else is changed: the ledger and the pages are rebuilt by hand after
rounds.csv and company_map.csv are updated (see DATASETS.md).

Output: one line starting "NEW AWARD SHEET" or "NEW ROUND" per finding, or
"nothing new". Exit code 0 unless a fetch fails.
"""
import csv, json, os, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import load_env, get_key

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://www.spr.doe.gov/posting/EXCHANGE/"
AWARDS = ROOT / "data/raw/doe_awards"
OLD = {"FY22 Winter Exchange", "Exchange for Storage"}   # earlier exchanges in DOE's archive, not 2026 rounds


def get(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    load_env()
    ua = f"Data4ThePeople research ({get_key('D4TP_CONTACT_EMAIL')})"   # read at run time, never stored here
    known = {r["release_name"] for r in csv.DictReader((ROOT / "data/reference/rounds.csv").open())} | OLD
    held = {p.name for p in AWARDS.glob("*.pdf")}
    found, seen = [], set()
    for where in ("current", "archive"):
        for rel in json.loads(get(BASE + where + "/", ua)):
            if rel["name"] not in known and rel["name"] not in seen:
                found.append(f"NEW ROUND {rel['name']} (in {where}/, not in rounds.csv)")
            seen.add(rel["name"])
            for folder in rel["folders"]:
                for f in folder["files"]:
                    name = f["name"]
                    if "award" not in name.lower() or name in held:
                        continue
                    # Closed rounds are served under archive/. Open rounds are served with no folder prefix.
                    path = f"{rel['name']}/{folder['name']}/{name}"
                    url = BASE + urllib.parse.quote(f"archive/{path}" if where == "archive" else path)
                    body = get(url, ua)
                    if not body.startswith(b"%PDF"):
                        sys.exit(f"{name}: download is not a PDF")
                    (AWARDS / name).write_bytes(body)
                    held.add(name)
                    found.append(f"NEW AWARD SHEET {name} (posted {f['timeLastModified']}, {len(body):,} bytes, from {where}/)")
    print("\n".join(found) if found else "nothing new")


if __name__ == "__main__":
    main()
