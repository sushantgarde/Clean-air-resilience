# Configuration Guide

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Environment Variables](#2-environment-variables)
- [3. Configuration Files](#3-configuration-files)
- [4. Region Configuration](#4-region-configuration)
- [5. Model & Threshold Configuration](#5-model--threshold-configuration)
- [6. Secrets Management](#6-secrets-management)
- [7. Environment-Specific Configuration](#7-environment-specific-configuration)
- [8. Configuration Checklist](#8-configuration-checklist)

---

## 1. Overview

This document describes every configurable value in Clean Air & Climate
Resilience — environment variables, hardcoded parameters worth knowing about,
and how configuration differs between local development and the deployed
Render environment.

## 2. Environment Variables

All environment variables are loaded via `python-dotenv` from a `.env` file
locally, and via Render's **Environment** tab in production. None have
default fallback values except `PORT`.

| Variable | Required | Used in | Description |
|---|---|---|---|
| `SENTINELHUB_CLIENT_ID` | Yes | `sh_config.py` | OAuth client ID for Copernicus Data Space |
| `SENTINELHUB_CLIENT_SECRET` | Yes | `sh_config.py` | OAuth client secret for Copernicus Data Space |
| `OPENAQ_API_KEY` | Yes | `weather_client.py` | API key for OpenAQ v3 endpoints |
| `GEMINI_API_KEY` | Yes | `vision_classifier.py`, `alert_generator.py`, `app.py` | API key for Gemini (Vision + Text) via AI Studio |
| `PORT` | No (defaults to `8080`) | `app.py` | Set automatically by Render; do not set manually in `.env` |

**Validation:** `sh_config.py` raises a `ValueError` at import time if either
Sentinel Hub credential is missing — the app will fail fast rather than
silently proceeding with an invalid config.

## 3. Configuration Files

| File | Purpose |
|---|---|
| `.env` | Local secrets (never committed) |
| `.gitignore` | Controls which files are excluded from version control |
| `requirements.txt` | Pinned Python dependency versions |
| `runtime.txt` | Pins the Python version for Render (`python-3.11.9`) |

### 3.1 `.gitignore` — current exclusions

```
env/
.env
__pycache__/
*.pyc
*.pyo
data/weather_aqi_history.json
data/sample_images/*
!data/sample_images/.gitkeep
MYPROJECT.zip
image.png
Demo Video.mp4
Demo Video.zip
.DS_Store
Thumbs.db
.vscode/
.idea/
```

**Deliberately NOT excluded:** `data/air_quality.db` — included despite
being a binary/generated file, because Render's free-tier filesystem is
ephemeral and the deployed app needs this data present at startup. See
[Deployment Guide](./DEPLOYMENT_GUIDE.md) §9 for the reasoning.

## 4. Region Configuration

Regions are defined in `app.py` as a static dictionary — adding a new region
requires no other code changes:

```python
REGIONS = {
    "punjab-haryana": {
        "display_name": "Punjab-Haryana Belt",
        "satellite_aerosol": -0.18,   # from data/day1_sentinel_sample.json
        "citizen_severity_score": 3,  # High, from Gemini Vision test results
    },
    "delhi-ncr": {
        "display_name": "Delhi-NCR (Federated Region B)",
        "satellite_aerosol": 0.35,
        "citizen_severity_score": 4,  # Severe
    },
}
```

| Field | Type | Description |
|---|---|---|
| `display_name` | string | Human-readable name shown in the alert and dashboard |
| `satellite_aerosol` | float | Static aerosol index value for the region (from a Sentinel-5P pull; not re-fetched per request) |
| `citizen_severity_score` | int (1–4) | Static citizen photo severity rating for the region |

**To add a new region:**
1. Add an entry to `REGIONS` with a unique key
2. Add matching station coordinates to `REGION_STATIONS` in `script.js`
3. Add a map center/zoom entry to `REGION_CENTERS` in `script.js`
4. Add a corresponding toggle button in `index.html`

## 5. Model & Threshold Configuration

### 5.1 Hotspot scoring weights (`hotspot_scoring.py`)

```python
weights = {"satellite": 0.4, "citizen": 0.3, "forecast": 0.3}
```

Adjustable directly in code; no environment variable exposed for this
currently. Changing these requires re-deploying.

### 5.2 Forecasting window (`forecasting.py`)

```python
def load_pm25_daily_series(region=None, recent_days=90):
```

`recent_days` controls how far back the daily-aggregation window looks.
Default is 90 days; effectively bounded by how much history the underlying
station data actually contains (see [TDD](./TECHNICAL_DESIGN_DOCUMENT.md) §3.5).

### 5.3 Gemini model selection

| Module | Model used | Reason |
|---|---|---|
| `vision_classifier.py` (batch) | `gemini-3.1-flash-lite` | Higher free-tier RPM quota, needed for batch image classification |
| `alert_generator.py` | `gemini-3.1-flash-lite` | Consistency with the rest of the pipeline's free-tier usage |

To change models, edit the `model=` argument in the relevant
`client.models.generate_content()` call. Confirm the target model is
current — Google has retired models mid-project before (`gemini-2.0-flash`
was retired during this build).

### 5.4 Satellite query parameters (`day1_checkpoint.py`)

```python
BBOX_COORDS = [75.5, 29.5, 77.5, 31.5]        # Punjab-Haryana belt
TIME_INTERVAL = ("2025-10-15", "2025-11-15")  # stubble-burning season
```

Resolution is set to 1000m in the `bbox_to_dimensions()` call.

### 5.5 OpenAQ query parameters (`weather_client.py`)

```python
CANDIDATE_CENTERS = [
    {"name": "Patiala area", "lat": 30.5, "lon": 76.5},
    {"name": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    {"name": "Ludhiana", "lat": 30.9010, "lon": 75.8573},
    {"name": "Karnal", "lat": 29.6857, "lon": 76.9905},
]
```

`radius` is capped at OpenAQ's server-side maximum of 25,000m; cannot be
increased. `limit` per sensor is set to 500 (increased from an initial 50
— see [TDD](./TECHNICAL_DESIGN_DOCUMENT.md) §3.3 for why).

## 6. Secrets Management

**Local:** stored in `.env`, loaded via `python-dotenv`, never committed
(verified via `git check-ignore -v .env`).

**Production (Render):** stored in Render's **Environment** tab, encrypted
at rest by Render, injected as process environment variables at runtime —
never present in the git repository or build logs.

**Rotation:** if a key is ever exposed (e.g. accidentally committed), rotate
it immediately at the source:
- Sentinel Hub: regenerate the OAuth client in the CDSE dashboard
- OpenAQ: regenerate the API key in account settings
- Gemini: revoke and create a new key in AI Studio

Then update both the local `.env` and Render's environment variables with
the new value.

## 7. Environment-Specific Configuration

| Setting | Local | Render (production) |
|---|---|---|
| `debug` (Flask) | Can be `True` for local dev | `False` — debug mode exposes a code-execution console on unhandled errors, unsafe publicly |
| `host` | `localhost` implicit | Must be `0.0.0.0` to be reachable externally |
| `port` | `8080` (hardcoded default) | Read from `PORT` env var, set automatically by Render |
| Python version | Whatever's installed locally (tested on 3.11) | Pinned via `runtime.txt` / `PYTHON_VERSION` to avoid slow source builds on newer versions |

## 8. Configuration Checklist

Before deploying or handing off this project, confirm:

- [ ] `.env` exists locally with all four required variables set
- [ ] `.env` is confirmed gitignored (`git check-ignore -v .env`)
- [ ] `requirements.txt` reflects the actual installed package set (`pip freeze`)
- [ ] `runtime.txt` present and matches a Python version with prebuilt wheel support
- [ ] All four environment variables are set in Render's dashboard, matching local values
- [ ] `data/air_quality.db` is committed and up to date
- [ ] `REGIONS` dict in `app.py` matches any region toggle buttons in `index.html`
