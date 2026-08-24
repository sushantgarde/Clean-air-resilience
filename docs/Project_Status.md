# Project Status Report

## Clean Air & Climate Resilience

**Report Date:** August 2026 (Day 5 — Submission)
**Reporting Period:** Full 5-day build cycle
**Prepared by:** Sushant Garde
**Status:** ✅ On track — submitted

---

## Table of Contents

- [1. Summary](#1-summary)
- [2. Phase-by-Phase Status](#2-phase-by-phase-status)
- [3. What's Done](#3-whats-done)
- [4. What's Not Done / Deferred](#4-whats-not-done--deferred)
- [5. Risks & Issues Encountered](#5-risks--issues-encountered)
- [6. Metrics](#6-metrics)
- [7. Roadmap (Post-Submission)](#7-roadmap-post-submission)
- [8. Overall Assessment](#8-overall-assessment)

---

## 1. Summary

Clean Air & Climate Resilience was built over a 5-day hackathon timeline
for **Build with AI — Code for Communities** (Track 2: Clean Air & Climate
Resilience). The project is **complete and submitted**: all core pipeline
components run end-to-end on real data, the system is publicly deployed on
Render, and a full documentation set has been produced.

The single largest deviation from the original plan was the **complete
substitution of the Google Cloud stack** (Earth Engine, Vertex AI,
Firestore/BigQuery, Cloud Run) with free-tier alternatives, triggered by a
billing verification hold encountered early on Day 1. This turned out to be
a net-positive constraint — it forced the architecture toward genuinely
zero-cost deployability, which became a core part of the project's value
proposition rather than a workaround.

## 2. Phase-by-Phase Status

| Phase | Planned Deliverable | Status | Notes |
|---|---|---|---|
| **Phase 1** — Day 1 | Environment setup, free-tier accounts, first real satellite pull | ✅ Complete | Google Cloud stack replaced with Copernicus/Gemini/SQLite/Render early in this phase |
| **Phase 2** — Day 2 | Vision classifier tested, real weather/AQI data in SQLite | ✅ Complete | 7,489+ real readings loaded from 9 OpenAQ stations |
| **Phase 3** — Day 3 | Forecast → hotspot score → AI alert, end-to-end | ✅ Complete | Forecasting model redesigned mid-phase after initial approach produced a flat trend |
| **Phase 4** — Day 4 | Live dashboard, federated mock, free-tier deployment | ✅ Complete | Deployed to Render; several deployment-specific bugs resolved (see §5) |
| **Phase 5** — Day 5 | Bug fixes, demo video, pitch deck, documentation, submission | ✅ Complete | Full documentation suite (this report included) produced |

## 3. What's Done

- ✅ Real, live Sentinel-5P satellite data pipeline for Punjab-Haryana
- ✅ Gemini Vision citizen photo classifier, tested against a real sample dataset
- ✅ Real OpenAQ ground-station data pipeline — 9 stations, 7,489+ readings, across Patiala, Chandigarh, Ludhiana, and Karnal
- ✅ SQLite storage layer
- ✅ PM2.5 forecasting model (daily-aggregated linear regression)
- ✅ Weighted hotspot scoring algorithm fusing all three signals
- ✅ Gemini-generated plain-language alerts
- ✅ Public API (`/api/hotspots`, `/api/hotspots/<region>`)
- ✅ Live, interactive dashboard with map visualization
- ✅ Two-region federated demonstration (Punjab-Haryana / Delhi-NCR)
- ✅ Public deployment on Render (free tier, zero billing)
- ✅ Full documentation set: README, Architecture, API docs, Technical Design Document, PRD, Deployment Guide, Configuration Guide, Runbook, Testing Documentation, Contributing Guide, Changelog, Security doc, Privacy Policy, Executive Summary, User Guide, and this Status Report
- ✅ Pitch deck (PPTX/PDF)
- ✅ Demo video with chapter timestamps
- ✅ Project logo (header wordmark + favicon icon)

## 4. What's Not Done / Deferred

Explicitly out of scope for this submission (documented in the
[PRD](./PRD.md) §3 Non-Goals), not overlooked:

| Item | Reason for deferral |
|---|---|
| Live citizen photo upload endpoint | Would require auth/rate-limiting design not achievable in the timeline; classification was validated against a sample dataset instead |
| SMS/push alert delivery | Out of scope for a web-dashboard-first MVP |
| Automated test suite / CI pipeline | Manual, run-to-verify testing used throughout instead, appropriate to timeline (see [Testing Documentation](./TESTING_DOCUMENTATION.md)) |
| Non-ephemeral production database | SQLite committed directly to the repo as a workaround for Render's free-tier ephemeral filesystem; a managed Postgres instance would be the production-grade fix |
| Regions beyond Punjab-Haryana / Delhi-NCR | Two regions were sufficient to demonstrate the federated architecture concept |

## 5. Risks & Issues Encountered

All items below were resolved during the build; retained here for a
transparent record (full detail in [CHANGELOG](./CHANGELOG.md)):

| Issue | Impact | Resolution |
|---|---|---|
| Google Cloud billing verification hold on Day 1 | Would have blocked Earth Engine/Vertex AI/Firestore/Cloud Run usage entirely | Replaced entire stack with free alternatives before Phase 1 was complete |
| Sentinel Hub returning HTML instead of satellite data | Blocked all satellite data acquisition | Diagnosed as a CDSE endpoint-binding issue; fixed via explicit `DataCollection.define_from()` |
| `gemini-2.0-flash` retired mid-project | Broke the vision classifier | Migrated to current `google-genai` SDK and `gemini-3.1-flash-lite` |
| Gemini free-tier rate limits (5 RPM) during batch classification | Batch script failed on most images | Switched to `gemini-3.1-flash-lite` (~15 RPM) and added retry/backoff |
| OpenAQ 25,000m radius cap | Limited single-query coverage | Queried 4 separate center points instead of one large radius |
| Forecasting model producing a flat, uninformative trend | Undermined the core "forecast" value proposition | Redesigned to daily-aggregated, 90-day-windowed regression |
| 115MB+ generated JSON file rejected by GitHub | Blocked all pushes to the repository | Stripped raw arrays from committed JSON files; kept summary evidence files only |
| Render defaulting to Python 3.14, causing slow from-source builds | Deploy times ballooning toward 15–20+ minutes | Pinned Python 3.11.9 via `runtime.txt` / `PYTHON_VERSION` env var |
| Deployed instance missing the SQLite database entirely | Live API returned `500` errors on every request | Reversed the `.gitignore` exclusion and committed `data/air_quality.db` directly, given Render's ephemeral filesystem |
| Logo/favicon not rendering on deployed dashboard | Cosmetic, but affected polish | Added a dedicated Flask route for the `docs/` directory; switched to absolute asset paths |

## 6. Metrics

| Metric | Value |
|---|---|
| Real ground-station readings collected | 7,489+ |
| Real monitoring stations integrated | 9 |
| Sub-regions covered (station discovery) | 4 (Patiala, Chandigarh, Ludhiana, Karnal) |
| Regions demonstrated end-to-end | 2 (Punjab-Haryana, Delhi-NCR) |
| Core pipeline modules | 8 (`sh_config`, `vision_classifier`, `weather_client`, `db_client`, `forecasting`, `hotspot_scoring`, `alert_generator`, `app`) |
| Documentation files produced | 16 |
| External paid services used | 0 |
| Build timeline | 5 days |

## 7. Roadmap (Post-Submission)

If continued beyond the hackathon, prioritized as follows (full detail in
[Architecture Document](./ARCHITECTURE.md) §11):

1. Live citizen photo upload endpoint with async Gemini classification
2. Migrate SQLite to a managed Postgres instance for durability
3. Automated test suite (`pytest`), starting with `hotspot_scoring.py`'s pure functions
4. CI pipeline (GitHub Actions)
5. Response caching for Gemini-generated alerts to reduce latency and API usage
6. Expand region coverage beyond the current two

## 8. Overall Assessment

The project achieved its core objective: a genuinely working, end-to-end
pollution hotspot detection and alerting system built on real data, deployed
publicly, entirely on free-tier infrastructure. The main technical risk
(Google Cloud billing dependency) was identified and resolved early enough
that it strengthened rather than compromised the final submission. Remaining
gaps (live photo upload, automated testing, production-grade database) are
clearly scoped, documented, and sequenced for any future continuation rather
than left as unexamined technical debt.
