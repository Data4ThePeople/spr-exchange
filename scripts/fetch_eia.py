#!/usr/bin/env python3
"""Pull every EIA series this project uses and save the raw responses.

Source: EIA Open Data API v2, series-id route. One JSON file per series goes in
data/raw/eia/ exactly as EIA returned it. A tidy long CSV of all series goes in
data/processed/eia_series.csv. Re-running refreshes everything; EIA revises
recent weeks, so the retrieval date is written into data/raw/eia/_retrieved.json.
"""
import sys, os; sys.path.insert(0, os.path.expanduser("~/.claude/d4tp-process"))
from d4tp_env import load_env, get_key
load_env()

import csv, datetime, json
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "eia"
OUT = ROOT / "data" / "processed" / "eia_series.csv"

# series id -> (short name, what it is)
SERIES = {
    "PET.WCSSTUS1.W": ("spr_stocks_kbbl", "Weekly U.S. ending stocks of crude oil in the SPR, thousand barrels"),
    "PET.WCESTUS1.W": ("commercial_crude_stocks_kbbl", "Weekly U.S. ending stocks of crude oil excluding SPR, thousand barrels"),
    "PET.WCREXUS2.W": ("crude_exports_weekly_kbd", "Weekly U.S. exports of crude oil, thousand barrels per day"),
    "PET.WCRIMUS2.W": ("crude_imports_weekly_kbd", "Weekly U.S. imports of crude oil, thousand barrels per day"),
    "PET.WCRFPUS2.W": ("crude_production_weekly_kbd", "Weekly U.S. field production of crude oil, thousand barrels per day"),
    "PET.WCRRIUS2.W": ("refiner_crude_inputs_weekly_kbd", "Weekly U.S. refiner net input of crude oil, thousand barrels per day"),
    "PET.WPULEUS3.W": ("refinery_utilization_pct", "Weekly U.S. percent utilization of refinery operable capacity"),
    "PET.WDISTUS1.W": ("distillate_stocks_kbbl", "Weekly U.S. ending stocks of distillate fuel oil, thousand barrels"),
    "PET.MCREXUS2.M": ("crude_exports_monthly_kbd", "Monthly U.S. exports of crude oil, thousand barrels per day"),
    "PET.MCSSTUS1.M": ("spr_stocks_monthly_kbbl", "Monthly U.S. ending stocks of crude oil in the SPR, thousand barrels"),
    "PET.RWTC.D": ("wti_spot_usd", "Cushing, OK WTI spot price FOB, dollars per barrel, daily"),
    "PET.RBRTE.D": ("brent_spot_usd", "Europe Brent spot price FOB, dollars per barrel, daily"),
    "PET.RCLC1.D": ("wti_fut1_usd", "Cushing, OK crude oil future contract 1, dollars per barrel, daily"),
    "PET.RCLC2.D": ("wti_fut2_usd", "Cushing, OK crude oil future contract 2, dollars per barrel, daily"),
    "PET.RCLC3.D": ("wti_fut3_usd", "Cushing, OK crude oil future contract 3, dollars per barrel, daily"),
    "PET.RCLC4.D": ("wti_fut4_usd", "Cushing, OK crude oil future contract 4, dollars per barrel, daily"),
}


def fetch(series_id, key):
    rows, offset = [], 0
    while True:
        r = requests.get(f"https://api.eia.gov/v2/seriesid/{series_id}",
                         params={"api_key": key, "offset": offset, "length": 5000}, timeout=120)
        r.raise_for_status()
        body = r.json()["response"]
        rows += body["data"]
        offset += 5000
        if offset >= int(body["total"]):
            return rows, body


def main():
    key = get_key("EIA_API_KEY")
    RAW.mkdir(parents=True, exist_ok=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tidy = []
    for sid, (name, desc) in SERIES.items():
        rows, body = fetch(sid, key)
        (RAW / f"{sid}.json").write_text(json.dumps(rows, indent=0))
        seen = set()
        for row in rows:
            if row["period"] in seen:
                sys.exit(f"duplicate period {row['period']} in {sid}")  # hard failure by house rule
            seen.add(row["period"])
            if row["value"] is None:
                continue
            tidy.append((name, sid, row["period"], row["value"], row.get("units", "")))
        periods = sorted(seen)
        print(f"{sid:18s} {name:34s} n={len(rows):5d} {periods[0]} to {periods[-1]}")
    tidy.sort()
    with OUT.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "series_id", "period", "value", "units"])
        w.writerows(tidy)
    (RAW / "_retrieved.json").write_text(json.dumps(
        {"retrieved": datetime.date.today().isoformat(),
         "series": {sid: desc for sid, (_, desc) in SERIES.items()}}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(tidy)} rows")


if __name__ == "__main__":
    main()
