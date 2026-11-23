"""Stage 0: confirm that every data source is reachable and returns what we expect.

Run locally first, then paste into a Databricks notebook cell to confirm the
workspace can reach the internet too.

    python check_sources.py
    CENSUS_API_KEY=your_key python check_sources.py   # optional key
"""

import os
import re
import sys

import requests

TIMEOUT = 30


def check_fema() -> bool:
    url = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
    params = {"$top": 3, "$orderby": "declarationDate desc", "$inlinecount": "allpages"}
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    body = resp.json()
    rows = body.get("DisasterDeclarationsSummaries", [])
    total = body.get("metadata", {}).get("count")
    print(f"[FEMA]   OK  total declarations: {total}")
    for r in rows:
        print(f"         {r.get('declarationDate', '')[:10]}  {r.get('state')}  "
              f"{r.get('incidentType')}  {r.get('designatedArea')}")
    return bool(rows)


def check_census() -> bool:
    # B25001_001E = housing units, B25077_001E = median home value
    url = "https://api.census.gov/data/2023/acs/acs5"
    params = {"get": "NAME,B25001_001E,B25077_001E", "for": "county:*", "in": "state:48"}
    key = os.getenv("CENSUS_API_KEY")
    if key:
        params["key"] = key
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    try:
        rows = resp.json()
    except ValueError:
        print(f"[Census] FAIL  response is not JSON. First 200 chars: {resp.text[:200]!r}")
        return False
    header, data = rows[0], rows[1:]
    print(f"[Census] OK  columns: {header}")
    print(f"         Texas counties returned: {len(data)}; first: {data[0]}")
    return len(data) > 0


def check_noaa() -> bool:
    url = "https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/"
    resp = requests.get(url, timeout=TIMEOUT)
    resp.raise_for_status()
    files = sorted(set(re.findall(r"StormEvents_details-ftp_v1\.0_d(\d{4})_c(\d{8})\.csv\.gz", resp.text)))
    if not files:
        print("[NOAA]   FAIL  no details files found in the listing")
        return False
    years = sorted({y for y, _ in files})
    latest_year, latest_created = max(files)
    print(f"[NOAA]   OK  details files for {years[0]}-{years[-1]} ({len(years)} years)")
    print(f"         latest: year {latest_year}, created {latest_created}")
    return True


def main() -> int:
    results = {}
    checks = [("FEMA", check_fema), ("NOAA", check_noaa)]
    if os.getenv("CENSUS_API_KEY"):
        checks.append(("Census", check_census))
    else:
        print("[Census] SKIPPED  no CENSUS_API_KEY set")

    for name, fn in checks:
        try:
            results[name] = fn()
        except requests.RequestException as exc:
            print(f"[{name}] FAIL  {type(exc).__name__}: {exc}")
            results[name] = False
    print("\nSummary:", ", ".join(f"{k}={'OK' if v else 'FAIL'}" for k, v in results.items()))
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
