#!/usr/bin/env python3
"""Pull every EIA series this project uses and save the raw responses.

Source: EIA Open Data API v2, series-id route. One JSON file per series goes in
data/raw/eia/ exactly as EIA returned it. A tidy long CSV of all series goes in
data/processed/eia_series.csv. Re-running refreshes everything; EIA revises
recent weeks, so the retrieval date is written into data/raw/eia/_retrieved.json.
Give series ids as arguments to pull only those and leave the others as saved,
so charts already published from the saved copies do not shift.
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
    # Gulf Coast (PADD 3) and import detail, added October 12, 2026 for the 2022 and 2026 comparison
    "PET.W_NA_YUP_R30_PER.W": ("gulf_refinery_utilization_pct", "Weekly Gulf Coast (PADD 3) percent utilization of refinery operable capacity"),
    "PET.WCRRIP32.W": ("gulf_refiner_crude_inputs_weekly_kbd", "Weekly Gulf Coast (PADD 3) refiner net input of crude oil, thousand barrels per day"),
    "PET.WCESTP31.W": ("gulf_commercial_crude_stocks_kbbl", "Weekly Gulf Coast (PADD 3) ending stocks of crude oil excluding SPR, thousand barrels"),
    "PET.WCEIMP32.W": ("gulf_crude_imports_weekly_kbd", "Weekly Gulf Coast (PADD 3) commercial crude oil imports excluding SPR, thousand barrels per day"),
    "PET.MCREXP32.M": ("gulf_crude_exports_monthly_kbd", "Monthly Gulf Coast (PADD 3) exports of crude oil, thousand barrels per day"),
    "PET.MCRIMUSPG2.M": ("us_crude_imports_persian_gulf_monthly_kbd", "Monthly U.S. imports of crude oil from Persian Gulf countries, thousand barrels per day"),
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
    only = set(sys.argv[1:])          # series ids to pull; the rest are read back from disk unchanged
    if only - set(SERIES):
        sys.exit(f"unknown series: {sorted(only - set(SERIES))}")
    for sid, (name, desc) in SERIES.items():
        if only and sid not in only:
            rows = json.loads((RAW / f"{sid}.json").read_text())
        else:
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
    stamp = RAW / "_retrieved.json"
    dates = json.loads(stamp.read_text()).get("retrieved_by_series", {}) if stamp.exists() and only else {}
    old = json.loads(stamp.read_text())["retrieved"] if stamp.exists() and only else None
    today = datetime.date.today().isoformat()
    by_series = {sid: (today if not only or sid in only else dates.get(sid, old)) for sid in SERIES}
    stamp.write_text(json.dumps(
        {"retrieved": today if not only else old, "retrieved_by_series": by_series,
         "series": {sid: desc for sid, (_, desc) in SERIES.items()}}, indent=1))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(tidy)} rows")


if __name__ == "__main__":
    main()
