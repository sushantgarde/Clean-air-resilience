# Product Requirements Document (PRD)

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026
**Author:** Sushant Garde
**Hackathon:** Build with AI — Code for Communities (Google Cloud x BRICS), Track 2: Clean Air & Climate Resilience

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Problem Statement](#2-problem-statement)
- [3. Goals & Non-Goals](#3-goals--non-goals)
- [4. Target Users](#4-target-users)
- [5. User Stories](#5-user-stories)
- [6. Functional Requirements](#6-functional-requirements)
- [7. Non-Functional Requirements](#7-non-functional-requirements)
- [8. Scope: In / Out](#8-scope-in--out)
- [9. Success Metrics](#9-success-metrics)
- [10. Constraints & Assumptions](#10-constraints--assumptions)
- [11. Risks](#11-risks)
- [12. Milestones](#12-milestones)

---

## 1. Executive Summary

Clean Air & Climate Resilience is an AI-powered early-warning platform that
detects hidden, hyper-local pollution hotspots by fusing satellite data,
citizen-reported photos, and ground-station air quality readings — then
forecasts near-term AQI trends and generates plain-language alerts for local
environmental authorities. It targets the Punjab-Haryana belt during
stubble-burning season and is built entirely on free-tier infrastructure to
remain deployable by resource-constrained governments and NGOs.

## 2. Problem Statement

Every October–November, large-scale stubble burning in Punjab and Haryana
drives severe seasonal smog across Northern India, affecting hundreds of
millions of people, most acutely in Delhi-NCR. Three structural gaps prevent
effective response:

1. **Sparse ground monitoring** — official AQI station networks are thin and
   unevenly distributed, leaving many hyper-local hotspots undetected
   between stations.
2. **No fused, hyper-local signal** — satellite data, citizen observation,
   and station readings currently exist as separate, unconnected data
   sources; no system combines them into a single actionable score.
3. **Reactive rather than predictive response** — authorities typically act
   only after AQI has already spiked, rather than forecasting and
   intervening ahead of a spike.

## 3. Goals & Non-Goals

### Goals
- Fuse three independent, verifiable real data sources into a single
  hotspot risk score
- Forecast near-term (3-day) PM2.5 trends from real historical readings
- Generate clear, non-technical alerts that a local authority can act on
  without needing to interpret raw data
- Demonstrate the architecture generalizes across regions (federated/
  cross-border applicability) without sharing raw data between regions
- Build and deploy entirely on free-tier infrastructure, with zero billing
  dependency, so the system is realistically deployable by
  resource-constrained teams

### Non-Goals (for this version)
- Building a production-grade, high-availability service handling real
  public traffic at scale
- Building a live citizen photo submission pipeline (a live upload endpoint
  is out of scope for this version; classification is demonstrated against
  a sample dataset)
- Building a mobile app or SMS-based alert delivery channel
- Achieving state-of-the-art forecasting accuracy (a simple, explainable
  model is intentionally preferred — see [TDD](./TECHNICAL_DESIGN_DOCUMENT.md))

## 4. Target Users

| User | Need |
|---|---|
| **Local environmental authorities** (e.g. state pollution control boards) | A plain-language, actionable alert they can use to trigger a response, without needing to interpret raw satellite/sensor data themselves |
| **NGOs / civic tech teams** | A deployable, zero-cost reference architecture for pollution monitoring they can adapt to other regions |
| **Citizens in affected regions** | (Future) a channel to report visible smog and see regional risk status |
| **Hackathon judges / evaluators** | A working, real (not mocked) system that demonstrates genuine technical execution under real-world constraints |

## 5. User Stories

- *As a local pollution control officer*, I want to see a single risk score
  for my region so that I don't have to manually cross-reference satellite
  data, citizen reports, and station readings myself.
- *As a local authority*, I want a plain-language alert explaining likely
  cause and recommended action, so I can act quickly without needing
  technical interpretation.
- *As an NGO deploying this in a new region*, I want the architecture to
  generalize to any bounding box and station set, so I can adapt it without
  rebuilding the pipeline from scratch.
- *As a judge evaluating this hackathon submission*, I want to clearly see
  which parts of the system use real, live data versus simulated/
  illustrative data, so I can accurately assess technical execution.

## 6. Functional Requirements

| ID | Requirement | Status |
|---|---|---|
| FR-1 | System shall pull real Sentinel-5P aerosol index data for a defined region and time window | ✅ Implemented |
| FR-2 | System shall classify citizen-submitted photos for smog/haze severity via Gemini Vision | ✅ Implemented (sample dataset) |
| FR-3 | System shall pull real ground-station AQI/pollutant readings from OpenAQ | ✅ Implemented (9 stations, 7,489+ readings) |
| FR-4 | System shall store readings in a persistent, queryable data store | ✅ Implemented (SQLite) |
| FR-5 | System shall fuse satellite, citizen, and forecast signals into a single weighted hotspot score | ✅ Implemented |
| FR-6 | System shall forecast 3-day PM2.5 trends from historical readings | ✅ Implemented |
| FR-7 | System shall generate a plain-language alert (risk, cause, action) via Gemini | ✅ Implemented |
| FR-8 | System shall expose computed results via a public API | ✅ Implemented |
| FR-9 | System shall render results on an interactive, map-based dashboard | ✅ Implemented |
| FR-10 | System shall support switching between at least two independently-computed regions | ✅ Implemented (Punjab-Haryana, Delhi-NCR) |
| FR-11 | System shall accept live citizen photo uploads via a public endpoint | ⛔ Out of scope (v1) |
| FR-12 | System shall deliver alerts via SMS/push notification | ⛔ Out of scope (v1) |

## 7. Non-Functional Requirements

| ID | Requirement | Notes |
|---|---|---|
| NFR-1 | Zero billing/card dependency across the entire stack | Directly shaped every major tech choice — see [Architecture Document](./ARCHITECTURE.md) §7 |
| NFR-2 | Deployable on a single free-tier hosting service | Flask serves both API and dashboard from one process to satisfy Render's one-service-one-start-command model |
| NFR-3 | System should return real (non-mocked) data end-to-end for its core pipeline | Verified manually at each phase — see [TDD](./TECHNICAL_DESIGN_DOCUMENT.md) §8 |
| NFR-4 | Alerts should be interpretable by a non-technical reader | Enforced via prompt design in `alert_generator.py` (structure + word cap) |
| NFR-5 | Documentation should transparently disclose real vs. simulated components | See "What's Real vs. Simulated" table in README |

## 8. Scope: In / Out

**In scope for this version:**
- Punjab-Haryana belt (real, live pipeline) and Delhi-NCR (federated demo,
  illustrative satellite/citizen values — clearly disclosed)
- 3-day PM2.5 forecasting
- Weighted hotspot scoring
- Gemini-based alert generation
- Web dashboard with interactive map

**Out of scope for this version:**
- Live citizen photo submission endpoint
- SMS/push alert delivery
- Multi-user authentication or role-based access
- Historical trend visualization beyond the 3-day forecast window
- Automated testing/CI pipeline
- Support for regions beyond the two demonstrated

## 9. Success Metrics

For a hackathon submission, success is defined qualitatively rather than by
live production KPIs:

| Metric | Target |
|---|---|
| Real data sources integrated | 3 of 3 (satellite, citizen, ground-station) |
| Real ground-station readings collected | 7,489+ (achieved) |
| End-to-end pipeline functioning without manual intervention | Yes (achieved — forecast → score → alert runs automatically per API request) |
| Deployed, publicly accessible live demo | Yes (Render) |
| Zero billing/card required anywhere in the stack | Yes (achieved) |
| Documentation completeness (README, architecture, API, TDD, PRD) | Complete set produced |

## 10. Constraints & Assumptions

**Constraints:**
- 5-day build timeline
- No budget for paid cloud services
- Solo development
- Free-tier API rate limits (Gemini: ~5–15 RPM depending on model; OpenAQ:
  25,000m radius cap per query)

**Assumptions:**
- Judges will value a genuinely working system with real data over a
  polished but partially mocked one
- OpenAQ station coverage in the target region is sufficient to demonstrate
  the concept, even if sparse in absolute terms (this assumption held: 9
  stations across 4 sub-regions were found)
- A simple, explainable forecasting model is preferable to a more complex
  one at this stage, given data volume and timeline

## 11. Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Free-tier rate limits block live demo mid-presentation | Medium | Use `gemini-3.1-flash-lite` (higher quota); pace batch requests; avoid re-triggering multiple Gemini calls in quick succession during a live demo |
| Render free-tier cold start delays first request | High (by design of free tier) | Start the service ~1 minute before presenting/recording |
| Thin historical data limits forecast robustness | Realized | Disclosed openly in TDD as a known limitation rather than hidden |
| Judges may not distinguish "free-tier constrained" from "less capable" | Medium | Explicit tech-stack comparison slide/table showing avoided vs. used services, framed as a deliberate accessibility decision |

## 12. Milestones

| Phase | Day | Deliverable |
|---|---|---|
| Phase 1 | Day 1 | Environment setup, free-tier accounts, first real satellite data pull |
| Phase 2 | Day 2 | Vision classifier tested, real weather/AQI data stored in SQLite |
| Phase 3 | Day 3 | Forecast → hotspot score → AI-generated alert, end-to-end |
| Phase 4 | Day 4 | Live dashboard, two-region federated mock, free-tier deployment |
| Phase 5 | Day 5 | Bug fixes, demo video, pitch deck, documentation, submission |
