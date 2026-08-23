# Architecture Document

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026
**Author:** Sushant Garde

---

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. System Overview](#2-system-overview)
- [3. Architecture Diagram](#3-architecture-diagram)
- [4. Component Breakdown](#4-component-breakdown)
- [5. Data Flow](#5-data-flow)
- [6. Data Model](#6-data-model)
- [7. Technology Choices & Rationale](#7-technology-choices--rationale)
- [8. Deployment Architecture](#8-deployment-architecture)
- [9. Scalability Considerations](#9-scalability-considerations)
- [10. Known Limitations](#10-known-limitations)
- [11. Future Architecture Evolution](#11-future-architecture-evolution)

---

## 1. Purpose

This document describes the technical architecture of Clean Air & Climate
Resilience — the system components, how data moves between them, the
reasoning behind each technology choice, and the constraints under which the
system was designed (specifically: zero billing dependency, hackathon
timeline, free-tier infrastructure only).

It is intended for engineers evaluating, extending, or deploying the system.

## 2. System Overview

The system is a **three-signal fusion pipeline**: it ingests satellite,
citizen-reported, and ground-station data independently, normalizes and
combines them into a single hotspot risk score, forecasts near-term trends,
and surfaces the result through a generated natural-language alert and a live
map-based dashboard.

The system is composed of five logical layers:

1. **Data Acquisition Layer** — pulls raw data from three external sources
2. **Storage Layer** — persists processed readings for querying
3. **Intelligence Layer** — classification, forecasting, scoring, alert generation
4. **API Layer** — exposes computed results over HTTP
5. **Presentation Layer** — renders results on an interactive dashboard

## 3. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      DATA ACQUISITION LAYER                      │
│                                                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐ │
│  │  Sentinel-5P    │  │  Citizen Photos │  │  OpenAQ Ground     │ │
│  │  (Copernicus    │  │  (sample/live   │  │  Stations (9 real  │ │
│  │   Data Space)   │  │   images)       │  │  stations)         │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬───────────┘ │
└───────────┼────────────────────┼────────────────────┼─────────────┘
            │                    │                    │
            ▼                    ▼                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       INTELLIGENCE LAYER                         │
│                                                                    │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐ │
│  │  Aerosol Index  │  │  Gemini Vision  │  │  Forecasting Model │ │
│  │  Extraction     │  │  Classifier     │  │  (Linear Regression│ │
│  │                 │  │  (severity)     │  │   on daily means)  │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬───────────┘ │
│           └────────────────────┼────────────────────┘             │
│                                 ▼                                  │
│                    ┌──────────────────────┐                       │
│                    │  Hotspot Scoring     │                       │
│                    │  (weighted fusion)   │                       │
│                    └──────────┬───────────┘                       │
│                                 ▼                                  │
│                    ┌──────────────────────┐                       │
│                    │  Gemini Alert         │                      │
│                    │  Generator            │                      │
│                    └──────────┬───────────┘                       │
└─────────────────────────────────┼──────────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                          STORAGE LAYER                            │
│                     SQLite (air_quality.db)                       │
└─────────────────────────────────┬───────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                            API LAYER                              │
│                    Flask (/api/hotspots/<region>)                 │
└─────────────────────────────────┬───────────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────┐
│                       PRESENTATION LAYER                          │
│         Dashboard (HTML/CSS/JS + Leaflet.js interactive map)      │
│         Two-region toggle: Punjab-Haryana ⇄ Delhi-NCR              │
└─────────────────────────────────────────────────────────────────┘
```

## 4. Component Breakdown

### 4.1 Data Acquisition Layer

| Module | Responsibility |
|---|---|
| `sh_config.py` | Authenticates against Copernicus Data Space via OAuth (CDSE-specific token/base URLs) |
| `test_sentinel.py` / `day1_checkpoint.py` | Queries Sentinel-5P `AER_AI_340_380` band for a bounding box and time interval |
| `weather_client.py` | Queries OpenAQ v3 API: locations → sensors → measurements, per station |

### 4.2 Intelligence Layer

| Module | Responsibility |
|---|---|
| `vision_classifier.py` | Sends citizen photos to Gemini Vision (`gemini-3.1-flash-lite`), returns severity classification + reasoning |
| `forecasting.py` | Aggregates PM2.5 readings to daily means, fits a linear regression, projects 3-day forward values |
| `hotspot_scoring.py` | Normalizes and weights satellite (40%), citizen (30%), and forecast (30%) signals into a 0–1 score |
| `alert_generator.py` | Prompts Gemini with region, score, and trend to produce a plain-language authority-facing alert |

### 4.3 Storage Layer

| Module | Responsibility |
|---|---|
| `db_client.py` | SQLite schema definition, insert, and query functions for `air_quality_readings` |

### 4.4 API Layer

| Module | Responsibility |
|---|---|
| `app.py` | Flask app; orchestrates the intelligence layer per request; serves both API and static dashboard from one process |

### 4.5 Presentation Layer

| File | Responsibility |
|---|---|
| `index.html` | Dashboard shell, region toggle UI |
| `script.js` | Fetches `/api/hotspots/<region>`, renders Leaflet map markers, updates score/forecast/alert panels |
| `style.css` | Dark-theme styling matching the satellite/data-monitoring aesthetic |

## 5. Data Flow

**Request-time flow** (`GET /api/hotspots/<region>`):

1. Client requests a region's hotspot data
2. `app.py` calls `load_pm25_daily_series()` → queries SQLite, aggregates to daily means
3. `train_forecast_model()` + `forecast_next_days()` → produces a 3-day PM2.5 forecast
4. `calculate_hotspot_score()` → fuses satellite aerosol value (static, from Phase 1 pull), citizen severity score (static, from Phase 2 classification), and the live forecast mean
5. `generate_alert()` → calls Gemini with the score and trend, returns generated text
6. Response JSON is returned to the client
7. `script.js` renders the score, forecast, and alert into the dashboard panels, and colors map markers by score

**Batch/offline flow** (run manually, not per-request):
- `day1_checkpoint.py` — pulls and stores a satellite data sample
- `test_vision_batch.py` — classifies a batch of sample citizen photos
- `weather_client.py` + `load_to_sqlite.py` — pulls OpenAQ data and loads it into SQLite

## 6. Data Model

**Table: `air_quality_readings`**

| Column | Type | Description |
|---|---|---|
| `id` | INTEGER (PK, autoincrement) | Row identifier |
| `region` | TEXT | Station or region name |
| `timestamp` | TEXT (ISO 8601) | Reading timestamp |
| `parameter` | TEXT | Pollutant type (`pm25`, `pm10`, `no2`, `so2`, `o3`, `co`) |
| `value` | REAL | Measured value |
| `source` | TEXT | Data origin (`weather_api`, `satellite`, `citizen_photo`) |

Current volume: **7,489+ rows**, sourced from 9 real OpenAQ stations across
Patiala, Chandigarh/Panchkula, Ludhiana, and Karnal.

## 7. Technology Choices & Rationale

| Decision | Rationale |
|---|---|
| **Copernicus Data Space over Google Earth Engine** | Earth Engine's Contributor tier requires a linked billing account for verification, even at $0 usage. Copernicus's Community Tier requires no billing at all and serves the same underlying Sentinel data. |
| **Gemini API (AI Studio) over Vertex AI** | Vertex AI requires an active Cloud project with billing. A Gemini API key from AI Studio has a genuinely free tier with no card required. |
| **SQLite over Firestore/BigQuery** | Both require a billed Cloud project. SQLite needs zero setup, is bundled with Python, and is sufficient at this data volume (~7K rows). |
| **Render over Google Cloud Run** | Cloud Run requires billing to be enabled on the project. Render's free web-service tier requires no card for this scale of app. |
| **Linear regression over a more complex forecasting model** | At hackathon timescale, a simple, explainable model that visibly works end-to-end is more valuable than a marginally more accurate black-box model. The architecture doesn't preclude swapping in a stronger model later (see Roadmap). |
| **Flask serving both API and static dashboard** | Simplifies deployment to a single process/single start command — required by Render's one-service-one-command model, and removes the need for CORS or a second hosting target. |

## 8. Deployment Architecture

```
GitHub repo (source of truth)
        │
        ▼
Render (free web service)
  ├── Build: pip install -r requirements.txt
  ├── Runtime: Python 3.11.9 (pinned via runtime.txt)
  ├── Start: python src/pipeline/app.py
  └── Serves: Flask app on Render-assigned $PORT, binds 0.0.0.0
```

**Important constraint:** Render's free tier filesystem is **ephemeral** —
it resets on every redeploy/restart. Because of this, `data/air_quality.db`
is committed directly to the repository (it's a small, ~6MB compact SQLite
file) rather than generated at runtime, ensuring the deployed instance always
has real data available without needing to re-run the OpenAQ ingestion
pipeline on every cold start.

## 9. Scalability Considerations

- **Current design is single-instance, single-region-at-a-time per request.**
  Each API call recomputes the forecast and re-calls Gemini live — acceptable
  at demo scale, but would need response caching for production traffic.
- **The two-region model is intentionally not shared-state** — each region's
  pipeline runs independently against its own static metadata (satellite
  value, citizen severity) and the same SQLite time-series table, filtered by
  station. This mirrors how a real federated/cross-border deployment would
  work: no raw data crosses jurisdictional lines, only computed outputs.
- **Adding a new region** requires only: (1) a bounding box for satellite
  pulls, (2) nearby OpenAQ station coverage, (3) an entry in the `REGIONS`
  dict in `app.py`. No architectural changes needed.

## 10. Known Limitations

- Gemini calls happen synchronously per API request — under concurrent load,
  this would need to move to an async task queue with cached/pre-computed
  results.
- The citizen photo pipeline is **not wired to a live upload endpoint** in
  this build — classification was validated via a Kaggle sample dataset,
  not real-time citizen submissions.
- Forecasting uses a simple linear trend on recent daily means; it will not
  capture non-linear pollution dynamics (e.g. sudden wind-driven clearing).
- The `delhi-ncr` region's satellite/citizen values are illustrative
  constants for the federated-mock demonstration, not a live Sentinel-5P pull
  for that specific region (documented in code as a `# DEMO NOTE`).

## 11. Future Architecture Evolution

- Replace linear regression with a time-series model (e.g. Prophet, ARIMA) once more historical station depth is available
- Add a live photo upload endpoint with Gemini Vision called asynchronously
- Move from SQLite to a managed Postgres instance (e.g. Render's free Postgres tier) for durability beyond Render's ephemeral disk
- Cache Gemini alert generations with a TTL to reduce redundant API calls and latency
- Extend the region model to a fully data-driven config (bounding boxes + station IDs) rather than hardcoded dict entries
