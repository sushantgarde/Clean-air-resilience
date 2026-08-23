# Clean Air & Climate Resilience

**AI-powered early detection of hidden pollution hotspots — built for Punjab-Haryana's stubble-burning season**

[![Live Demo](https://img.shields.io/badge/demo-live-4FD1C5)](https://clean-air-resilience.onrender.com)


Built for **Build with AI — Code for Communities** (Google Cloud x BRICS), Track 2: Clean Air & Climate Resilience.

---

## Table of Contents

- [Clean Air \& Climate Resilience](#clean-air--climate-resilience)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Problem Statement](#problem-statement)
  - [Solution](#solution)
  - [What's Real vs. Simulated](#whats-real-vs-simulated)
  - [Architecture](#architecture)
  - [Tech Stack](#tech-stack)
  - [Project Structure](#project-structure)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Running Locally](#running-locally)
  - [API Reference](#api-reference)
  - [Deployment](#deployment)
  - [Roadmap](#roadmap)
  - [Team](#team)
  - [License](#license)

---

## Overview

Clean Air & Climate Resilience is a platform that detects hidden, hyper-local
air pollution hotspots by fusing three independent real-time data sources —
satellite aerosol data, citizen-submitted photo reports, and ground-station
air quality readings — into a single weighted risk score. That score drives a
short-term pollution forecast and an AI-generated, plain-language alert for
local environmental authorities.

The project targets the **Punjab-Haryana belt** of India's Indo-Gangetic
Plain, where large-scale agricultural stubble burning during October–November
drives severe seasonal smog affecting hundreds of millions of people across
Northern India.

## Problem Statement

- **Seasonal crisis**: Stubble burning in Punjab and Haryana releases massive
  particulate loads each year, worsening air quality across the wider
  Indo-Gangetic Plain, including Delhi-NCR.
- **Sparse monitoring**: Government air quality station networks are thin and
  unevenly distributed, leaving many hyper-local hotspots undetected.
- **Reactive response**: Authorities typically act only after AQI has already
  spiked, rather than forecasting and intervening ahead of a spike.

## Solution

The platform fuses three real, independently-verifiable data streams:

| Signal | Source | What it captures |
|---|---|---|
| Satellite aerosol index | Sentinel-5P via Copernicus Data Space | Regional-scale atmospheric aerosol concentration |
| Citizen photo reports | Gemini Vision | Visible smog/haze severity from ground-level photos |
| Ground-station readings | OpenAQ (9 real stations) | Verified PM2.5, PM10, NO2, SO2, O3, CO measurements |

These are combined into a **weighted hotspot risk score**, which feeds a
**3-day PM2.5 forecast model** and a **Gemini-generated plain-language alert**
covering risk severity, likely cause, and recommended action — surfaced on a
live, interactive dashboard.

A **two-region toggle** (Punjab-Haryana / Delhi-NCR) demonstrates that the
same pipeline generalizes to any region, illustrating cross-border/federated
applicability without requiring raw data sharing between regions.

## What's Real vs. Simulated

Transparency on what's genuinely live versus illustrative:

| Component | Status |
|---|---|
| Satellite data (Sentinel-5P) | ✅ Real, live pull via Copernicus Data Space |
| Citizen photo classification | ✅ Real Gemini Vision inference, tested on sample images |
| Weather / AQI history | ✅ Real — 9 OpenAQ stations, 7,489+ readings |
| Forecast + hotspot score + alert | ✅ Real, computed end-to-end from live data |
| Live citizen photo intake | ⚠️ Simulated — architecture supports it; not wired to a live upload endpoint for this build |
| Cross-border data sharing | ⚠️ Simulated via the two-region dashboard toggle |

## Architecture

```
[Sentinel-5P Satellite] ──┐
[Citizen Photos]         ─┼──> [Fusion / Hotspot Scoring] ──> [Gemini Alert] ──> [Dashboard]
[OpenAQ Ground Stations] ─┘                │
                                            └──> [Forecasting Model]
```

**Data flow:**
1. Satellite aerosol index and OpenAQ station readings are pulled and stored
   in SQLite.
2. Citizen photos are classified for smog/haze severity via Gemini Vision.
3. A linear regression forecasting model predicts 3-day PM2.5 trends from
   recent daily averages.
4. All three signals are combined into a weighted hotspot score.
5. Gemini generates a plain-language alert from the score and forecast trend.
6. A Flask API serves both the computed results and the static dashboard,
   which renders real station data on an interactive Leaflet map.

## Tech Stack

Built entirely on **free-tier infrastructure with zero billing dependency** —
every Google Cloud service that requires a billing account was deliberately
substituted with a free, no-card alternative:

| Category | Used | Avoided (requires billing) |
|---|---|---|
| Satellite data | Copernicus Data Space (`sentinelhub`) | Google Earth Engine |
| AI / LLM | Gemini API via AI Studio | Vertex AI |
| Database | SQLite | Firestore / BigQuery |
| Hosting | Render | Google Cloud Run |
| Backend | Flask | — |
| Ground-station data | OpenAQ | — |
| Frontend | HTML / CSS / JS, Leaflet.js | — |

## Project Structure

```
clean-air-resilience/
├── data/                          # Real data outputs (satellite, vision, weather, SQLite DB)
├── docs/                          # Logos, documentation, presentation assets
├── src/
│   ├── pipeline/                  # Core backend logic
│   │   ├── sh_config.py           # Copernicus/Sentinel Hub auth
│   │   ├── vision_classifier.py   # Gemini Vision smog/haze classifier
│   │   ├── weather_client.py      # OpenAQ data client
│   │   ├── db_client.py           # SQLite storage layer
│   │   ├── forecasting.py         # PM2.5 forecasting model
│   │   ├── hotspot_scoring.py     # Signal fusion logic
│   │   ├── alert_generator.py     # Gemini-based alert generation
│   │   └── app.py                 # Flask API + dashboard server
│   └── dashboard/                 # Frontend (HTML/CSS/JS)
├── requirements.txt
├── runtime.txt
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.11
- Free API keys/accounts: [Copernicus Data Space](https://dataspace.copernicus.eu), [OpenAQ](https://explore.openaq.org), [Gemini API](https://aistudio.google.com)

### Installation

```bash
git clone https://github.com/sushantgarde/Clean-air-resilience.git
cd Clean-air-resilience
python -m venv env
source env/bin/activate      # Windows: env\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
SENTINELHUB_CLIENT_ID=your_client_id
SENTINELHUB_CLIENT_SECRET=your_client_secret
OPENAQ_API_KEY=your_openaq_key
GEMINI_API_KEY=your_gemini_key
```

### Running Locally

```bash
python src/pipeline/app.py
```

Open `http://localhost:8080` — the dashboard and API are served from the
same process.

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Serves the dashboard |
| `/api/hotspots` | GET | Returns hotspot data for all regions |
| `/api/hotspots/<region_key>` | GET | Returns hotspot score, 3-day forecast, and generated alert for one region (`punjab-haryana` or `delhi-ncr`) |

**Example response** (`GET /api/hotspots/punjab-haryana`):

```json
{
  "region": "Punjab-Haryana Belt",
  "hotspot_score": 0.427,
  "forecast_pm25_next_3_days": [34.55, 32.50, 30.46],
  "trend": "declining",
  "alert": "Air quality remains a moderate concern..."
}
```

## Deployment

Deployed on [Render](https://render.com) (free tier):
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `python src/pipeline/app.py`
- Python version pinned via `runtime.txt` for prebuilt-wheel compatibility

Live URL: **https://clean-air-resilience.onrender.com**

## Roadmap

- Live citizen photo upload endpoint (currently simulated via pre-classified sample images)
- Expand ground-station coverage beyond the current 9 stations
- Persistent, non-ephemeral storage for production-scale deployment
- SMS/push-based alert delivery for local authorities

## Team

**Sushant Garde** — B.Tech CSE, Nutan College of Engineering & Research
GitHub: [@sushantgarde](https://github.com/sushantgarde)

## License

This project is submitted for the Build with AI — Code for Communities
hackathon. License terms to be finalized post-submission.