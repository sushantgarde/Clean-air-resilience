# Technical Design Document (TDD)

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026
**Author:** Sushant Garde

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Design Goals & Constraints](#2-design-goals--constraints)
- [3. Detailed Component Design](#3-detailed-component-design)
  - [3.1 Satellite Data Acquisition](#31-satellite-data-acquisition)
  - [3.2 Citizen Photo Classification](#32-citizen-photo-classification)
  - [3.3 Ground-Station Data Acquisition](#33-ground-station-data-acquisition)
  - [3.4 Storage Layer](#34-storage-layer)
  - [3.5 Forecasting Model](#35-forecasting-model)
  - [3.6 Hotspot Scoring Algorithm](#36-hotspot-scoring-algorithm)
  - [3.7 Alert Generation](#37-alert-generation)
  - [3.8 API & Serving Layer](#38-api--serving-layer)
- [4. Database Schema](#4-database-schema)
- [5. Algorithm Design Details](#5-algorithm-design-details)
- [6. Design Decisions Log](#6-design-decisions-log)
- [7. Failure Modes & Handling](#7-failure-modes--handling)
- [8. Testing Strategy](#8-testing-strategy)

---

## 1. Introduction

This document provides implementation-level detail for each component of
Clean Air & Climate Resilience — algorithms used, why they were chosen over
alternatives, exact formulas, and the specific bugs/edge cases encountered
and resolved during development. It complements the [Architecture
Document](./ARCHITECTURE.md), which covers system-level structure; this
document covers *how* each piece actually works.

## 2. Design Goals & Constraints

| Goal | Constraint driving it |
|---|---|
| Zero billing dependency | Hackathon judged on feasibility for resource-constrained deployers; no team card/budget |
| Real, live data only (no mocked pipelines) | Judging criteria rewards genuine functioning systems over static demos |
| Single-process deployability | Render free tier runs one start command per service |
| Explainable outputs | Alerts are consumed by non-technical local authorities — no black-box scoring |
| 5-day build timeline | Every design choice favors implementation speed over theoretical optimality |

## 3. Detailed Component Design

### 3.1 Satellite Data Acquisition

**Module:** `sh_config.py`, `day1_checkpoint.py`

**Design:** Uses the `sentinelhub` Python SDK against Copernicus Data
Space Ecosystem (CDSE) rather than the SDK's default (Sinergise) endpoints.

**Critical implementation detail:** `DataCollection.SENTINEL5P` by default
resolves to the legacy Sinergise service URL. Requesting data against CDSE
credentials with the default collection returns an HTML error page
(`header=b'<!do'`) instead of a TIFF, which fails silently as a decode error
rather than an auth error. The fix is to explicitly rebind the collection:

```python
s5p_cdse = DataCollection.SENTINEL5P.define_from(
    "s5p_cdse", service_url="https://sh.dataspace.copernicus.eu"
)
```

**Query parameters used:**
- Band: `AER_AI_340_380` (UV Aerosol Index)
- Bounding box: `[75.5, 29.5, 77.5, 31.5]` (Punjab-Haryana belt)
- Resolution: 1000m
- Time interval: `2025-10-15` to `2025-11-15` (stubble-burning season,
  chosen as a historical window with a known pollution signal rather than a
  live "today" query, which risks incomplete satellite passes)

**Output handling:** Only summary statistics (mean/min/max) are persisted to
`data/day1_sentinel_sample.json` — the full pixel grid array is intentionally
dropped after an early version caused a 115MB+ JSON file that exceeded
GitHub's 100MB per-file limit.

### 3.2 Citizen Photo Classification

**Module:** `vision_classifier.py`

**Design:** Sends raw image bytes to Gemini via `client.models.generate_content()`
with a `types.Part.from_bytes(...)` image part and a text instruction
requesting a Low/Moderate/High/Severe severity rating with visual reasoning.

**Model selection:** Initially implemented against `gemini-2.0-flash`, which
was found to be retired mid-project (`404 NOT_FOUND`). Migrated to
`gemini-3.5-flash`, then further migrated to `gemini-3.1-flash-lite` after
hitting the free tier's 5 requests/minute cap on `gemini-3.5-flash` during
batch classification — `flash-lite` offers a materially higher free-tier
quota (~15 RPM) suited to batch workloads.

**Batch processing design:** `test_vision_batch.py` implements:
- Per-request retry (up to 3 attempts) on `429 RESOURCE_EXHAUSTED` (30s backoff) and `503 UNAVAILABLE` (15s backoff)
- Fixed 5-second inter-request delay to stay under the RPM ceiling
- Results appended incrementally and written once at the end to `data/vision_test_results.json`

### 3.3 Ground-Station Data Acquisition

**Module:** `weather_client.py`

**Design:** Three-tier OpenAQ v3 API traversal:
1. `GET /locations` — find stations within a radius of a center point
2. `GET /locations/{id}/sensors` — enumerate pollutant sensors per station
3. `GET /sensors/{id}/measurements` — pull actual readings per sensor

**Known API constraint:** OpenAQ's `radius` parameter has a hard server-side
maximum of 25,000 meters (`422` validation error above this). To achieve
broader regional coverage despite this cap, the design queries **four
distinct center points** (Patiala, Chandigarh, Ludhiana, Karnal) rather than
one large-radius query — yielding 9 real stations across the target belt.

**Depth tuning:** Initial implementation used `limit=50` per sensor, which
in practice returned only the 50 most recent readings — clustering within a
~13-hour window for high-frequency sensors. This was insufficient for
day-level forecasting. Increased to `limit=500` per sensor to capture a
multi-day history.

### 3.4 Storage Layer

**Module:** `db_client.py`

**Design:** Single-table SQLite schema (see [Section 4](#4-database-schema)),
chosen over Firestore/BigQuery specifically to avoid billing requirements.
At ~7,500 rows, SQLite's performance is not a constraint at this scale.

**Load process:** `load_to_sqlite.py` parses the nested OpenAQ JSON
(region → station → sensor → readings) and flattens it into individual rows,
with live per-station progress output (added specifically to make bulk-insert
progress visible during demo recording, since silent multi-second inserts
read as "hung" on camera).

### 3.5 Forecasting Model

**Module:** `forecasting.py`

**Design:** `scikit-learn` `LinearRegression` fit on `day_index → PM2.5`.

**Two design iterations were required:**

1. **Naive raw-reading regression** (first version): fit against every
   individual reading with `day_index` computed from the full available
   timestamp range. Failure mode: the underlying data spanned 2016–2025, so
   a regression across the full range produced an almost-flat 9-year trend
   line, useless for detecting a near-term stubble-burning spike.

2. **Daily-aggregated, recency-windowed regression** (final version):
   readings are grouped by calendar date and averaged (`groupby('date').mean()`)
   before fitting, and restricted to a recent window (default 90 days,
   parameterized via `recent_days`). This smooths sensor noise and ensures
   the model reflects current conditions rather than historical drift.

**A further edge case**: because the underlying station data's "recent"
readings clustered within only ~6 distinct days once daily-aggregated, the
model is fit on a small-N series. This is disclosed as a known limitation
(see [Section 7](#7-failure-modes--handling)) rather than hidden — the
forecast output (34.5 → 32.5 → 30.5 µg/m³) is plausible and directionally
sound, but N=6 is a thin sample for a production-grade forecast.

### 3.6 Hotspot Scoring Algorithm

**Module:** `hotspot_scoring.py`

**Formula:**

```
score = 0.4 × normalize(satellite_aerosol)
      + 0.3 × normalize(citizen_severity)
      + 0.3 × normalize(forecasted_aqi)
```

**Normalization design:**
- Satellite: `(value + 2) / 4`, clamped `[0, 1]` — chosen because Sentinel-5P's
  `AER_AI` index empirically ranges roughly -2 to +2, and naively feeding a
  signed, non-unit-range value into a weighted sum would distort the fusion
  (this was caught and fixed before the first working version — the raw
  index was originally treated as already being in `[0,1]`, which is
  incorrect).
- Citizen: `severity_score / 4` — direct linear mapping of the 1–4
  categorical rating.
- Forecast: `min(forecast_value / 500, 1)` — 500 µg/m³ chosen as the
  ceiling because it corresponds to India's CPCB "Severe+" AQI category
  upper bound.

**Weight rationale:** Satellite is weighted highest (0.4) as the most
objective, spatially comprehensive, and least noisy signal; citizen and
forecast are weighted equally (0.3 each) as complementary but individually
noisier inputs (citizen: subjective/sparse; forecast: model uncertainty).

### 3.7 Alert Generation

**Module:** `alert_generator.py`

**Design:** A single prompt template embeds region name, numeric hotspot
score, and a natural-language forecast trend description, with an explicit
100-word cap and a requested structure (risk level, cause, recommended
action) to keep output consistent and consumable by non-technical
authorities.

### 3.8 API & Serving Layer

**Module:** `app.py`

**Design:** Flask app configured with `static_folder` pointed at
`src/dashboard/` and `static_url_path=""`, so the dashboard is served
directly from `/`. A separate explicit route (`/docs/<filename>`) serves the
`docs/` directory, since it sits outside the configured static folder and
would otherwise 404 — this was a real bug encountered when the header logo
referenced a relative path assuming folder-relative resolution, which breaks
because the browser resolves relative URLs against the *page's* URL path,
not the source file's location on disk.

**Deployment-specific fix:** Render assigns its own port via the `PORT`
environment variable and requires binding to `0.0.0.0`, not `localhost`.
The original `app.run(debug=True, port=8080)` was changed to:

```python
port = int(os.environ.get("PORT", 8080))
app.run(debug=False, host="0.0.0.0", port=port)
```

`debug=False` in the deployed version, since Flask's debug mode exposes an
interactive code-execution console on unhandled exceptions — unsafe on a
public-facing deployment.

## 4. Database Schema

```sql
CREATE TABLE air_quality_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    region TEXT,
    timestamp TEXT,
    parameter TEXT,
    value REAL,
    source TEXT
);
```

| Column | Notes |
|---|---|
| `region` | Station display name, e.g. `"Model Town, Patiala - PPCB"` |
| `timestamp` | ISO 8601 string, parsed via `pandas.to_datetime(errors='coerce')` to tolerate malformed values |
| `parameter` | One of `pm25`, `pm10`, `no2`, `so2`, `o3`, `co`, plus weather params (`temperature`, `relativehumidity`, `wind_speed`, `wind_direction`, `nox`) |
| `source` | Currently always `"weather_api"`; schema supports `"satellite"` and `"citizen_photo"` for future integration |

No indexes are currently defined — acceptable at ~7.5K rows; would need
an index on `(parameter, timestamp)` before this became a bottleneck.

## 5. Algorithm Design Details

**Forecast confidence is not currently modeled.** The linear regression
returns point predictions only; no confidence interval or R² is surfaced to
the alert generator or the dashboard. This is flagged as a design gap rather
than an oversight — see Roadmap in the Architecture Document.

**Hotspot score is stateless per-request.** Each API call recomputes the
score from scratch rather than reading a cached/precomputed value. This was
an explicit simplicity trade-off for the hackathon timeline; production use
would precompute and cache scores on a schedule (e.g. hourly) rather than
per-request.

## 6. Design Decisions Log

| Date/Phase | Decision | Reason |
|---|---|---|
| Phase 1 | Switch Earth Engine → Copernicus Data Space | Billing hold triggered on card during GCP billing setup |
| Phase 1 | Drop raw satellite pixel array from saved JSON | 115MB+ file exceeded GitHub's 100MB limit |
| Phase 2 | Switch `google-generativeai` → `google-genai` SDK | Legacy SDK deprecated by Google; `gemini-2.0-flash` retired |
| Phase 2 | Switch `gemini-3.5-flash` → `gemini-3.1-flash-lite` for batch work | 5 RPM free-tier cap too restrictive for a 10-image batch |
| Phase 2 | Increase OpenAQ `limit` from 50 → 500 per sensor | 50 returned only ~13 hours of data, insufficient for daily forecasting |
| Phase 3 | Aggregate PM2.5 to daily means before regression | Raw multi-year data produced a near-flat, uninformative trend line |
| Phase 4 | Serve dashboard from Flask instead of a separate `http.server` | Render only supports one start command per service |
| Phase 4 | Add explicit `/docs/<filename>` route | Logo asset outside Flask's configured static folder, 404'd otherwise |
| Phase 4 | Commit `data/air_quality.db` to git (against typical practice) | Render's free-tier filesystem is ephemeral; deployed instance had no data without it |

## 7. Failure Modes & Handling

| Failure | Detection | Current Handling |
|---|---|---|
| Gemini rate limit exceeded | `429 RESOURCE_EXHAUSTED` | Retry with backoff (batch script only); surfaces as `500` in live API |
| Gemini model transiently unavailable | `503 UNAVAILABLE` | Retry with backoff (batch script only) |
| OpenAQ radius parameter exceeds max | `422` validation error | Fixed at design time — capped to 25,000m, multiple query centers used instead |
| Malformed/missing timestamp in stored data | Non-parseable string | `pd.to_datetime(errors='coerce')` + `dropna()` — silently excluded from forecasting |
| Unknown region requested via API | Lookup miss in `REGIONS` dict | Explicit `404` with error message |
| Render cold start | First request after idle | Not currently mitigated — documented as a known demo consideration (start service ~1 min before presenting) |

## 8. Testing Strategy

Testing in this build was **manual, integration-level, and run-to-verify**
rather than automated unit testing, appropriate to the hackathon timeline:

- Each pipeline module (`sh_config`, `vision_classifier`, `weather_client`,
  `forecasting`, `hotspot_scoring`, `alert_generator`) was run standalone via
  its own `if __name__ == "__main__":` block, with printed output manually
  inspected before integration into `app.py`.
- The full API was tested via direct browser/curl requests against
  `/api/hotspots/<region>`, verifying real computed values end-to-end.
- The dashboard was manually tested by toggling between regions and
  confirming the map, score, forecast, and alert all update correctly.

**Not implemented in this version:** automated unit tests, CI pipeline, or
regression tests. Flagged as a gap for any post-hackathon continuation.
