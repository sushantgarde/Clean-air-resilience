# Installation & Deployment Guide

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Prerequisites](#2-prerequisites)
- [3. Local Installation](#3-local-installation)
- [4. Obtaining Free API Credentials](#4-obtaining-free-api-credentials)
- [5. Environment Configuration](#5-environment-configuration)
- [6. Running the Pipeline Locally](#6-running-the-pipeline-locally)
- [7. Deploying to Render](#7-deploying-to-render)
- [8. Post-Deployment Verification](#8-post-deployment-verification)
- [9. Troubleshooting](#9-troubleshooting)
- [10. Rollback Procedure](#10-rollback-procedure)

---

## 1. Overview

This guide covers setting up Clean Air & Climate Resilience from scratch —
locally for development, and on Render for a live public deployment. The
entire stack uses free-tier services with no billing/card required anywhere.

## 2. Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.11 | Pinned via `runtime.txt`; newer versions (3.14+) lack prebuilt wheels for `numpy`/`pandas`, causing very slow source builds |
| Git | For version control and deployment via GitHub |
| GitHub account | Free; required for Render's GitHub-based deploy |
| Free accounts (no card needed) | Copernicus Data Space, OpenAQ, Google AI Studio (Gemini), Render |

## 3. Local Installation

```bash
git clone https://github.com/sushantgarde/Clean-air-resilience.git
cd Clean-air-resilience

python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate

pip install -r requirements.txt
```

**requirements.txt** (pinned versions):
```
sentinelhub==3.11.5
google-genai==2.18.0
flask==3.1.0
python-dotenv==1.0.1
pandas==2.2.3
numpy==2.1.3
scikit-learn==1.5.2
requests==2.32.3
gunicorn==23.0.0
```

## 4. Obtaining Free API Credentials

### 4.1 Copernicus Data Space (Sentinel Hub)
1. Register at [dataspace.copernicus.eu](https://dataspace.copernicus.eu) — email + password, no card
2. Go to the **Sentinel Hub Dashboard** ([shapps.dataspace.copernicus.eu/dashboard](https://shapps.dataspace.copernicus.eu/dashboard))
3. **User Settings → OAuth clients → + Create new OAuth client**
4. Save the generated **Client ID** and **Client Secret**

### 4.2 OpenAQ
1. Register at [explore.openaq.org](https://explore.openaq.org)
2. Go to your **Account** page → generate an **API key**

### 4.3 Gemini API
1. Go to [aistudio.google.com](https://aistudio.google.com)
2. **Get API key → Create API key** (choose "Create in new project" — this does not require billing on the free tier)

## 5. Environment Configuration

Create a `.env` file in the project root:

```
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret
OPENAQ_API_KEY=your_openaq_key
GEMINI_API_KEY=your_gemini_key
```

**Never commit this file.** Confirm it's excluded:
```bash
git check-ignore -v .env
```
Expected output: `.gitignore:<line>:.env    .env`

## 6. Running the Pipeline Locally

### 6.1 Full pipeline (first-time setup)

```bash
# Phase 1 — satellite data
python day1_checkpoint.py

# Phase 2 — vision classification + ground-station data
python test_vision_batch.py
python src/pipeline/weather_client.py
python load_to_sqlite.py

# Phase 3 — forecast, score, alert (verification only, no persistence needed)
python src/pipeline/forecasting.py
python src/pipeline/hotspot_scoring.py
python src/pipeline/alert_generator.py
```

### 6.2 Running the app

```bash
python src/pipeline/app.py
```

Open `http://localhost:8080` — the dashboard and API are served from the
same Flask process.

## 7. Deploying to Render

### 7.1 Push to GitHub

```bash
git add .
git commit -m "Deploy-ready commit"
git push -u origin main
```

**Before pushing, verify:**
- `.env` and `env/` are gitignored (never pushed)
- `data/air_quality.db` **is** committed (Render's filesystem is ephemeral —
  the app needs this pre-built database bundled in the repo, not generated
  at runtime)
- Large/regenerable files (`data/weather_aqi_history.json`,
  `data/sample_images/`) are excluded per `.gitignore`

### 7.2 Create the Render service

1. Go to [render.com](https://render.com), sign up (GitHub login recommended)
2. **New + → Web Service**
3. Connect your GitHub repository
4. Configure:

| Field | Value |
|---|---|
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python src/pipeline/app.py` |
| Instance Type | Free |
| Branch | `main` |

5. Add environment variables under **Environment**:
   `SENTINELHUB_CLIENT_ID`, `SENTINELHUB_CLIENT_SECRET`, `OPENAQ_API_KEY`, `GEMINI_API_KEY`
6. Click **Create Web Service**

### 7.3 Pin the Python runtime

Add `runtime.txt` to the project root:
```
python-3.11.9
```

If Render doesn't pick this up automatically (observed behavior on some
service configurations), set it explicitly as an environment variable
instead:
```
Key: PYTHON_VERSION
Value: 3.11.9
```
Then **Manual Deploy → Clear build cache & deploy**.

**Why this matters:** without pinning, Render may default to a very recent
Python version (e.g. 3.14) that lacks prebuilt wheels for `numpy`/`pandas`,
forcing a slow from-source compile (15–20+ minutes vs. 3–5 minutes with a
pinned, wheel-supported version).

## 8. Post-Deployment Verification

1. **Check the build log** — confirm dependencies install via `.whl` files,
   not `.tar.gz` source builds
2. **Visit the root URL** — dashboard should load with the logo, map, and
   panels rendering
3. **Test the API directly:**
   ```bash
   curl https://your-app.onrender.com/api/hotspots/punjab-haryana
   ```
   Should return real JSON with `hotspot_score`, `forecast_pm25_next_3_days`,
   and `alert` fields populated — not an error.
4. **Toggle regions** on the dashboard — confirm the map re-centers and data
   updates for both Punjab-Haryana and Delhi-NCR

## 9. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `no such table: air_quality_readings` | `data/air_quality.db` wasn't committed to git | Remove `data/*.db` from `.gitignore`, `git add data/air_quality.db`, commit, push |
| Build stuck on `Preparing metadata (pyproject.toml)` for a long time | Python version has no prebuilt wheels for `numpy`/`pandas` | Pin Python via `runtime.txt` or `PYTHON_VERSION` env var (3.11.x recommended) |
| Logo/favicon shows broken image | Asset lives outside Flask's configured `static_folder` | Add an explicit route (e.g. `/docs/<filename>`) serving that directory; use absolute paths (`/docs/file.svg`) in HTML, not relative paths |
| `429 RESOURCE_EXHAUSTED` from Gemini | Free-tier rate limit exceeded | Switch to a model with higher free quota (e.g. `gemini-3.1-flash-lite`); add retry/backoff for batch operations |
| Push rejected: `File ... exceeds GitHub's file size limit` | A generated data file grew too large (e.g. full raw satellite pixel array, or deep OpenAQ pull with full metadata) | Strip to summary stats before committing; exclude the full file via `.gitignore`, keep a small evidence summary instead |
| `git push` rejected: `fetch first` | Remote has commits not present locally | If remote content isn't needed, `git push --force` (only safe on a fresh/solo repo); otherwise `git pull --allow-unrelated-histories` first |
| First request after idle is very slow | Render free-tier cold start | Expected behavior; not a bug — start the service ~1 minute before a live demo |

## 10. Rollback Procedure

Render keeps a history of deploys under the **Deploys** tab:
1. Go to the service → **Deploys**
2. Find the last known-good deploy
3. Click **Redeploy** on that specific commit

For a git-level rollback:
```bash
git log --oneline          # find the last good commit hash
git revert <bad-commit-hash>
git push
```
Render will auto-redeploy from the reverted commit.
