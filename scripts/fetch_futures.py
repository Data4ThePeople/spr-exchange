#!/usr/bin/env python3
"""Pull daily closes for each dated NYMEX WTI and ICE Brent futures contract.

Source: Yahoo Finance chart endpoint, which relays exchange closes for each
contract month (CLZ26.NYM is December 2026 WTI, BZZ26.NYM is December 2026
Brent). These are closes as relayed by Yahoo, not the official CME or ICE
settlement file, which is not free. A contract that Yahoo no longer serves
(it drops some expired months) is recorded as missing, not filled in.

Writes one raw JSON per contract to data/raw/futures/ and a tidy long CSV to
data/processed/futures_closes.csv (date, product, contract, delivery, close).
"""
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import load_env
load_env()

import csv, datetime, json, time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "futures"
OUT = ROOT / "data" / "processed" / "futures_closes.csv"

# Contact address for the User-Agent: read at run time, never hardcoded in the repo.
UA = {"User-Agent": f"Mozilla/5.0 (Data 4 The People research; {os.environ.get('D4TP_CONTACT_EMAIL', '')})"}
MONTH_CODES = "FGHJKMNQUVXZ"   # Jan..Dec
START, END = datetime.date(2026, 1, 1), datetime.date.today() + datetime.timedelta(days=1)
PRODUCTS = {"WTI": ("CL", "NYM"), "Brent": ("BZ", "NYM")}
FIRST, LAST = (2026, 4), (2029, 12)   # delivery months April 2026 through December 2029


def contracts():
    y, m = FIRST
    while (y, m) <= LAST:
        yield y, m
        y, m = (y, m + 1) if m < 12 else (y + 1, 1)


def fetch(symbol):
    epoch = lambda d: int(datetime.datetime(d.year, d.month, d.day, tzinfo=datetime.timezone.utc).timestamp())
    for attempt in range(4):
        r = requests.get(f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}",
                         params={"period1": epoch(START), "period2": epoch(END), "interval": "1d"},
                         headers=UA, timeout=60)
        if r.status_code == 429:
            time.sleep(5 * (attempt + 1))
            continue
        return r
    return r


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    rows, missing = [], []
    for product, (root, exch) in PRODUCTS.items():
        for y, m in contracts():
            symbol = f"{root}{MONTH_CODES[m - 1]}{y % 100:02d}.{exch}"
            r = fetch(symbol)
            result = (r.json().get("chart", {}).get("result") or [None])[0] if r.status_code == 200 else None
            if not result or not result.get("timestamp"):
                missing.append(symbol)
                continue
            (RAW / f"{symbol}.json").write_text(json.dumps(result))
            tz = datetime.timezone(datetime.timedelta(seconds=result["meta"]["gmtoffset"]))
            seen = set()
            for ts, close in zip(result["timestamp"], result["indicators"]["quote"][0]["close"]):
                if close is None:
                    continue
                d = datetime.datetime.fromtimestamp(ts, tz).date().isoformat()
                if d in seen:
                    sys.exit(f"duplicate date {d} in {symbol}")  # hard failure by house rule
                seen.add(d)
                rows.append((d, product, symbol, f"{y}-{m:02d}", round(close, 2)))
            time.sleep(0.4)
    # Front-month continuous contract, used as the sale price in scripts/trade_math.py.
    r = fetch("CL=F")
    front = (r.json().get("chart", {}).get("result") or [None])[0] if r.status_code == 200 else None
    if not front or not front.get("timestamp"):
        sys.exit("CL=F not served")
    (RAW / "CL=F.json").write_text(json.dumps(front))
    rows.sort()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "product", "contract", "delivery", "close"])
        w.writerows(rows)
    (RAW / "_retrieved.json").write_text(json.dumps(
        {"retrieved": datetime.date.today().isoformat(), "missing": missing}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} rows, {len(set(r[2] for r in rows))} contracts")
    print("not served by Yahoo:", ", ".join(missing) or "none")


if __name__ == "__main__":
    main()
