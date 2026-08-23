# Changelog

## Clean Air & Climate Resilience

All notable changes to this project are documented here. Format loosely
follows [Keep a Changelog](https://keepachangelog.com/), organized by build
phase rather than semantic version, reflecting this project's hackathon
development timeline.

---

## [Unreleased]

### Planned
- Live citizen photo upload endpoint
- Persistent (non-ephemeral) database via Render's managed Postgres
- Automated test suite (`pytest`) starting with `hotspot_scoring.py`
- CI pipeline (GitHub Actions)

---

## Phase 5 — Documentation & Submission

### Added
- `README.md` — full project documentation
- `ARCHITECTURE.md` — system design and component breakdown
- `API_DOCUMENTATION.md` — endpoint reference
- `TECHNICAL_DESIGN_DOCUMENT.md` — implementation-level design detail
- `PRD.md` — product requirements
- `DEPLOYMENT_GUIDE.md` — install and deploy instructions
- `CONFIGURATION_GUIDE.md` — environment variable and config reference
- `RUNBOOK.md` — operations manual
- `TESTING_DOCUMENTATION.md` — test strategy and case log
- `CONTRIBUTING.md` — contribution guidelines
- Pitch deck (`.pptx`/`.pdf`) covering problem, solution, architecture, tech stack, live demo, transparency, and impact
- `website-logo.svg` (header wordmark) and `website-logo-title.svg` (favicon icon mark)
- Demo video with YouTube chapter timestamps

### Fixed
- Broken logo/favicon references — added a dedicated `/docs/<filename>` Flask route since `docs/` sat outside the configured static folder; switched `index.html` to absolute asset paths

---

## Phase 4 — Dashboard, Federated Mock, Deployment

### Added
- `app.py` — Flask API exposing `/api/hotspots` and `/api/hotspots/<region>`
- `src/dashboard/` — dashboard frontend (`index.html`, `style.css`, `script.js`) with Leaflet.js interactive map
- Two-region federated mock — `delhi-ncr` added to `REGIONS`, with a region-toggle UI and independent map re-centering
- `runtime.txt` — pinned Python 3.11.9 for Render build compatibility
- `gunicorn` added to `requirements.txt` for production WSGI serving

### Changed
- Flask now serves the dashboard as static files from the same process as the API (previously required two separate local servers) — necessary for Render's one-service-one-start-command model
- `script.js` API base URL changed from hardcoded `http://localhost:8080` to a relative path, so it works both locally and once deployed
- `app.run()` updated to read Render's `$PORT` environment variable, bind `0.0.0.0`, and disable `debug` mode for production safety

### Fixed
- `ModuleNotFoundError: No module named 'src'` in `app.py` — `sys.path` fix only climbed two directory levels instead of the required three
- Deployed instance returning `no such table: air_quality_readings` — `data/air_quality.db` was excluded via `.gitignore`; Render's ephemeral filesystem meant it never existed in production. Reversed the exclusion and committed the database directly
- Render build defaulting to Python 3.14 despite `runtime.txt`, causing a slow from-source `numpy`/`pandas` compile — resolved by setting `PYTHON_VERSION` directly as a Render environment variable and clearing the build cache
- `git push` rejected due to a 115MB+ `data/weather_aqi_history.json` exceeding GitHub's 100MB file limit — stripped the raw pixel/measurement payload, excluded the full file via `.gitignore`, and added a small `weather_aqi_summary.json` as a real-data evidence file instead

---

## Phase 3 — Forecasting, Hotspot Scoring, Alert Generation

### Added
- `forecasting.py` — PM2.5 forecasting via `LinearRegression`
- `hotspot_scoring.py` — weighted fusion of satellite, citizen, and forecast signals into a 0–1 score
- `alert_generator.py` — Gemini-based plain-language alert generation

### Changed
- Forecasting redesigned from raw-reading regression (spanning the full 2016–2025 dataset) to daily-aggregated, 90-day-windowed regression — the original approach produced a near-flat, uninformative trend line
- Hotspot scoring's satellite input normalization corrected — the raw `AER_AI` index (roughly -2 to +2 range) was initially fed unnormalized into the weighted sum; added `(value + 2) / 4` clamped normalization

---

## Phase 2 — Vision Pipeline & Weather/AQI Data

### Added
- `vision_classifier.py` — Gemini Vision smog/haze severity classifier
- `weather_client.py` — OpenAQ station discovery, sensor enumeration, and measurement pull
- `db_client.py` — SQLite schema and read/write functions
- `load_to_sqlite.py` — loader from OpenAQ JSON into SQLite, with live per-station progress output
- Sample image dataset sourced from a public Kaggle air pollution dataset (India/Nepal)

### Changed
- Migrated from the deprecated `google-generativeai` SDK to the current `google-genai` SDK after `gemini-2.0-flash` was retired mid-project
- Switched from `gemini-3.5-flash` (5 RPM free-tier limit) to `gemini-3.1-flash-lite` (~15 RPM) for batch image classification
- OpenAQ measurement pull depth increased from `limit=50` to `limit=500` per sensor — the original limit returned only ~13 hours of clustered readings, insufficient for forecasting
- OpenAQ query radius capped at 25,000m (API-enforced maximum); broadened regional coverage instead by querying four separate center points (Patiala, Chandigarh, Ludhiana, Karnal) rather than one large-radius query

### Fixed
- Batch classification script failing outright on `429`/`503` errors — added retry logic with exponential-style backoff and inter-request pacing

---

## Phase 1 — Environment Setup & Data Access

### Added
- Project scaffolding (`data/`, `notebooks/`, `src/pipeline/`, `src/dashboard/`, `docs/`)
- `requirements.txt` — pinned dependency versions
- `sh_config.py` — Copernicus Data Space (CDSE) OAuth configuration
- `day1_checkpoint.py` — first real Sentinel-5P satellite data pull for the locked Punjab-Haryana region
- `.gitignore` — excludes `.env`, `env/`, `__pycache__/`, and other non-source artifacts

### Changed
- Replaced the original plan's Google Cloud stack (Earth Engine, Vertex AI, Firestore/BigQuery, Cloud Run) with free, no-billing alternatives (Copernicus Data Space, Gemini via AI Studio, SQLite, Render) after a Google Cloud billing verification hold was triggered
- Dropped the full raw satellite pixel array from `day1_sentinel_sample.json`, keeping only summary statistics — the raw array had inflated the file to a size that caused git/GitHub issues later in the build

### Fixed
- Sentinel Hub requests returning an HTML error (`header=b'<!do'`) instead of TIFF data — `DataCollection.SENTINEL5P` defaulted to the legacy Sinergise endpoint; fixed by explicitly rebinding via `.define_from()` to the CDSE service URL
