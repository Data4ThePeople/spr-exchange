#!/usr/bin/env python3
"""Download the FY22 Winter Exchange contracts from DOE's FOIA reading room.

DOE's Strategic Petroleum Reserve office posts the loan ("exchange") agreements
made under RFP DE-RP96-22PO00001 and their later modifications at
  https://www.spr.doe.gov/FOIA/FY22WtrEx.htm
This pulls every PDF linked from that page into data/raw/doe_foia_2022/ and
writes manifest.json with the URL, size and SHA-256 of each, plus a copy of the
index page.
"""
import datetime, hashlib, json, os, re, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import load_env, get_key

ROOT = Path(__file__).resolve().parent.parent
INDEX = "https://www.spr.doe.gov/FOIA/FY22WtrEx.htm"
OUT = ROOT / "data/raw/doe_foia_2022"


def get(url, ua):
    req = urllib.request.Request(url, headers={"User-Agent": ua})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def main():
    load_env()
    ua = f"Data4ThePeople research ({get_key('D4TP_CONTACT_EMAIL')})"   # read at run time, never stored here
    today = datetime.date.today().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    page = get(INDEX, ua)
    (OUT / f"index_{today}.htm").write_bytes(page)
    links = re.findall(r'href="(FY22WtrExchange/[^"]+\.pdf)"[^>]*>(.*?)</a>', page.decode("utf-8", "ignore"), flags=re.S | re.I)
    manifest, seen = [], set()
    for href, label in links:
        name = href.split("/")[-1]
        if name in seen:
            sys.exit(f"duplicate file name {name}")   # hard failure by house rule
        seen.add(name)
        url = urllib.parse.urljoin(INDEX, urllib.parse.quote(href))
        body = get(url, ua)
        (OUT / name).write_bytes(body)
        manifest.append(dict(file=name, label=re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", label)).strip(), url=url,
                             bytes=len(body), sha256=hashlib.sha256(body).hexdigest(), is_pdf=body.startswith(b"%PDF"),
                             retrieved=today))
        print(f"{name}: {len(body):,} bytes")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))
    print(f"wrote {len(manifest)} files and manifest.json to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
