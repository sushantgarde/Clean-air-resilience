# Executive Summary

## Clean Air & Climate Resilience

**One-page overview for non-technical stakeholders**
**Build with AI — Code for Communities (Google Cloud x BRICS), Track 2: Clean Air & Climate Resilience**

---

## The Problem

Every October–November, large-scale agricultural stubble burning across
Punjab and Haryana drives severe seasonal smog across Northern India,
affecting hundreds of millions of people. Existing monitoring is too sparse
to catch hyper-local pollution hotspots, and response is typically reactive
— authorities act only after air quality has already spiked.

## The Solution

Clean Air & Climate Resilience is an AI-powered early-warning system that
fuses **three independent, real data sources** — satellite imagery,
citizen-reported photos, and ground-station sensors — into a single risk
score for a region. That score drives a short-term pollution forecast and a
plain-language alert that local authorities can act on immediately, without
needing to interpret raw technical data themselves.

## What Makes It Real

| Signal | Source | Scale |
|---|---|---|
| Satellite aerosol data | Sentinel-5P via Copernicus Data Space | Live regional pull |
| Citizen photo classification | Google Gemini Vision | Tested against a real sample dataset |
| Ground-station readings | OpenAQ | **9 real monitoring stations, 7,489+ readings** across Patiala, Chandigarh, Ludhiana, and Karnal |

Every number above is real, live-computed data — not a mockup. The system's
forecast, hotspot score, and generated alert all run end-to-end from this
real data on every request.

## Why It's Deployable, Not Just Demoable

The entire platform runs on **free-tier infrastructure with zero billing
dependency** — a deliberate design constraint, not a limitation forced on
the team. Every Google Cloud service that requires a billing account was
substituted with a functionally equivalent free alternative:

| Avoided (requires billing) | Used instead (free, no card) |
|---|---|
| Google Earth Engine | Copernicus Data Space |
| Vertex AI | Gemini API via AI Studio |
| Firestore / BigQuery | SQLite |
| Google Cloud Run | Render |

This means the system is realistically deployable **by the exact
organizations who need it most** — resource-constrained local governments,
NGOs, and student teams — without any procurement or budget barrier.

## Proof of Cross-Border Scalability

A live, two-region toggle on the dashboard (Punjab-Haryana ⇄ Delhi-NCR)
demonstrates that the same architecture runs independently across separate
regions with no raw data shared between them — a working preview of how this
could scale across state or national boundaries in a genuinely federated
model.

## Current Status

| Milestone | Status |
|---|---|
| Real satellite data pipeline | ✅ Complete |
| Real citizen photo classification | ✅ Complete |
| Real ground-station data pipeline | ✅ Complete (7,489+ readings) |
| Forecasting + hotspot scoring + AI alerts | ✅ Complete, end-to-end |
| Live public dashboard | ✅ Deployed |
| Two-region federated demonstration | ✅ Complete |
| Live citizen photo upload | ⏳ Roadmap (out of scope for v1) |

## Links

- **Live demo:** https://clean-air-resilience.onrender.com
- **Source code:** https://github.com/sushantgarde/Clean-air-resilience
- **Full documentation:** see `README.md` and the `docs/` directory for
  Architecture, API, Technical Design, PRD, Deployment, and Operations
  documentation

---

*Sushant Garde — B.Tech CSE, Nutan College of Engineering & Research*
