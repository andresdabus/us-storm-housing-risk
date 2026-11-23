# US Storm Exposure for Housing

**Which US counties carry the most hail and wind risk relative to the homes exposed, and where is that risk growing?**

Insurers and roofing companies need to know where storm damage concentrates relative to the housing stock. The data exists, but it lives in three federal agencies, keyed differently and partly stored as free text. This project consolidates it into a county-level model.

> Status: Stage 0 — setup and source validation. Sections marked *TBD* get filled as the pipeline is built.

## Questions

1. Which counties have the most hail and wind damage relative to their number of homes?
2. Where did storm exposure grow over the last 10 years?
3. Do FEMA disaster declarations follow the counties with the most recorded damage?

## Data sources

| Source | Content | Access |
|---|---|---|
| NOAA Storm Events Database | Storm events with location, damage and injuries, 1950 to present | Yearly bulk CSV files |
| OpenFEMA Disaster Declarations Summaries v2 | Federal disaster declarations since 1953 | REST API, no key |
| US Census ACS 5-year | Housing units, median home value, year built, by county | REST API |

## Architecture

Bronze (raw files as received) → Silver (typed, deduplicated, damage text converted to USD, events mapped to county FIPS) → Gold (star schema and county risk metrics). *TBD: diagram.*

## Stack

Python · Databricks · PySpark · Delta Lake · SQL · Databricks Workflows / Airflow · GitHub Actions

## Key design decisions

*TBD.* (Examples to document: immutable Bronze, county key mapping, lookback for revised months, idempotent `MERGE`.)

## Findings

*TBD.*

## How to run

```bash
python -m venv .venv && source .venv/bin/activate
pip install requests
python scripts/check_sources.py
```

## Limitations

*TBD.* (Known: some events are recorded against forecast zones instead of counties; many events report zero or missing damage.)
