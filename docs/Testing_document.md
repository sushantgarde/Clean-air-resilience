# Testing Documentation

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026

---

## Table of Contents

- [1. Testing Strategy](#1-testing-strategy)
- [2. Test Scope & Coverage Summary](#2-test-scope--coverage-summary)
- [3. Component-Level Test Cases](#3-component-level-test-cases)
- [4. Integration Test Cases](#4-integration-test-cases)
- [5. Manual Test Log (Actual Results)](#5-manual-test-log-actual-results)
- [6. How to Run Verification Locally](#6-how-to-run-verification-locally)
- [7. Known Gaps](#7-known-gaps)
- [8. Recommended Future Test Suite](#8-recommended-future-test-suite)

---

## 1. Testing Strategy

Given the 5-day hackathon timeline, this project used **manual,
run-to-verify integration testing** rather than an automated unit test
suite. Each pipeline module includes a standalone `if __name__ == "__main__":`
block that exercises its core function against real data and prints output
for manual inspection — this doubled as both development testing and a
reusable verification tool.

This is a deliberate, disclosed trade-off (see [PRD](./PRD.md) §3
Non-Goals), not an oversight — automated testing is listed explicitly under
[Known Gaps](#7-known-gaps) and [Recommended Future Test Suite](#8-recommended-future-test-suite).

## 2. Test Scope & Coverage Summary

| Layer | Test Method | Status |
|---|---|---|
| Satellite data acquisition | Manual, standalone script run | ✅ Verified against real Sentinel-5P data |
| Vision classification | Manual, batch script against sample dataset | ✅ Verified — 18+ images classified successfully |
| Ground-station data acquisition | Manual, standalone script run | ✅ Verified — 9 real stations, 7,489+ readings |
| SQLite storage | Manual, load script + row count verification | ✅ Verified |
| Forecasting model | Manual, standalone script run, output sanity-checked | ✅ Verified (with documented limitations — see §7) |
| Hotspot scoring | Manual, standalone script with real example inputs | ✅ Verified |
| Alert generation | Manual, standalone script run | ✅ Verified — output quality manually reviewed |
| API endpoints | Manual, browser + curl requests | ✅ Verified |
| Dashboard (frontend) | Manual, browser testing across both regions | ✅ Verified |
| Deployment (Render) | Manual, live URL health checks post-deploy | ✅ Verified |
| Automated unit tests | None written | ❌ Not implemented |
| CI/CD pipeline | None configured | ❌ Not implemented |
| Load/performance testing | None performed | ❌ Not implemented |

## 3. Component-Level Test Cases

### 3.1 `sh_config.py` / Satellite Data Acquisition

| Test | Steps | Expected Result | Actual Result |
|---|---|---|---|
| Valid CDSE auth | Run `test_sentinel.py` with valid `.env` credentials | Returns real aerosol index array, no HTTP/decode error | ✅ Pass — shape `(19, 22)`, real values returned |
| Missing credentials | Unset `SENTINELHUB_CLIENT_ID` in `.env`, run `sh_config.py` | Raises `ValueError` at import time | ✅ Pass (by design, per code review) |
| Wrong data collection endpoint | Use default `DataCollection.SENTINEL5P` against CDSE credentials | Fails with HTML response instead of TIFF | ✅ Reproduced and fixed via `.define_from()` rebinding |

### 3.2 `vision_classifier.py`

| Test | Steps | Expected Result | Actual Result |
|---|---|---|---|
| Single image classification | Run `classify_air_quality()` on a sample photo | Returns text with severity rating + reasoning | ✅ Pass — correctly distinguished natural fog from industrial smog by color/context reasoning |
| Batch classification under rate limit | Run `test_vision_batch.py` on 10 images with `gemini-3.1-flash-lite` | All images classified without unrecoverable errors | ✅ Pass, after model switch from `gemini-3.5-flash` |
| Rate limit handling | Trigger `429` by exceeding RPM | Retries with backoff, eventually succeeds or logs failure | ✅ Pass — retry logic confirmed functioning |

### 3.3 `weather_client.py`

| Test | Steps | Expected Result | Actual Result |
|---|---|---|---|
| Station discovery | Run `get_stations()` for Punjab-Haryana center points | Returns real station list | ✅ Pass — 9 stations found across 4 centers |
| Radius over API max | Set `radius=50000` (exceeds OpenAQ's 25,000m cap) | Returns `422` validation error | ✅ Reproduced and fixed by capping radius |
| Deep measurement pull | Set `limit=500` per sensor | Returns multi-day reading history, not just latest hours | ✅ Pass, after increasing from initial `limit=50` |

### 3.4 `db_client.py`

| Test | Steps | Expected Result | Actual Result |
|---|---|---|---|
| Table creation | Run `init_db()` on a fresh path | Creates `air_quality_readings` table | ✅ Pass |
| Insert + count | Run `load_to_sqlite.py` against `weather_aqi_history.json` | Row count matches source reading count | ✅ Pass — 7,489 readings loaded |

### 3.5 `forecasting.py`

| Test | Steps | Expected Result | Actual Result |
|---|---|---|---|
| Full-history regression (pre-fix) | Fit on entire 2016–2025 dataset | Produces near-flat trend, low predictive value | ⚠️ Confirmed as a failure mode, prompted redesign |
| Daily-aggregated, recency-windowed regression (post-fix) | Fit on last 90 days, daily means | Produces a plausible short-term trend | ✅ Pass — forecast values (34.5→32.5→30.5 µg/m³) judged directionally sound |
| Insufficient data guard | Run against a series with <2 distinct days | Should print a graceful message, not crash | ✅ Pass (explicit check added: `if len(df) < 2`) |

### 3.6 `hotspot_scoring.py`

| Test | Steps | Expected Result | Actual Result |
|---|---|---|---|
| Real example inputs | `calculate_hotspot_score(-0.18, 3, 34.5)` | Returns a score in `[0, 1]` | ✅ Pass — returned `0.428` |
| Normalization bounds | Pass extreme satellite values (e.g. -5, +5) | Score component clamps to `[0, 1]`, doesn't go negative/over 1 | ✅ Pass (clamping confirmed in code) |

### 3.7 `alert_generator.py`

| Test | Steps | Expected Result | Actual Result |
|---|---|---|---|
| Real inputs, live Gemini call | `generate_alert()` with real score/trend | Returns structured alert text under ~100 words, covering risk/cause/action | ✅ Pass — manually reviewed output judged clear and appropriately structured |

## 4. Integration Test Cases

| Test | Steps | Expected Result | Actual Result |
|---|---|---|---|
| Full pipeline, single request | `GET /api/hotspots/punjab-haryana` | Returns populated JSON with real score, forecast, and alert, no manual steps required | ✅ Pass |
| Unknown region | `GET /api/hotspots/nonexistent` | Returns `404` with a clear error message | ✅ Pass |
| Dashboard renders live data | Load `index.html`, observe panels | Score, forecast, and alert populate from the live API without manual refresh | ✅ Pass |
| Region toggle | Click "Delhi-NCR" button on dashboard | Map re-centers, markers update, panels refresh with Delhi-NCR data | ✅ Pass |
| Logo/favicon asset serving | Load dashboard, inspect header and browser tab | Logo renders correctly, not broken | ✅ Pass, after adding explicit `/docs/<filename>` route (see [TDD](./TECHNICAL_DESIGN_DOCUMENT.md) §3.8) |
| Deployed instance has real data | `curl` the live Render `/api/hotspots/punjab-haryana` | Returns real data, not a `500`/"no such table" error | ✅ Pass, after committing `data/air_quality.db` to the repo |

## 5. Manual Test Log (Actual Results)

Selected real outputs captured during development, used as regression
references:

**Satellite pull (Phase 1):**
```
Region: Punjab-Haryana Belt (Indo-Gangetic Plain)
Grid shape: (19, 22)
Mean AER_AI: -0.1844
```

**Vision classification (Phase 2):**
```
Severity Rating: Severe (visibility reduction/haze)
Color and Context Note: uniform, clean white/grey appearance ... suggests
natural mountain fog or heavy mist rather than industrial smog
```

**Ground-station pull (Phase 2):**
```
Found 9 total stations across 4 centers
Loaded 7489 readings into data/air_quality.db
```

**Forecast (Phase 3, post-fix):**
```
Loaded 6 daily PM2.5 averages spanning 2025-10-03 to 2025-10-08
Forecasted daily mean PM2.5 for next 3 days: [34.55, 32.50, 30.46]
```

**Hotspot score (Phase 3):**
```
Example hotspot score: 0.428
```

**Live API response (Phase 4, deployed):**
```json
{
  "hotspot_score": 0.427,
  "trend": "declining",
  "forecast_pm25_next_3_days": [34.5506786660433, 32.5029346267726, 30.455190587502]
}
```

## 6. How to Run Verification Locally

```bash
# Verify each component standalone
python src/pipeline/sh_config.py            # (via test_sentinel.py) satellite auth + pull
python src/pipeline/vision_classifier.py    # single-image classification (adjust path in script)
python src/pipeline/weather_client.py       # station discovery + measurement pull
python src/pipeline/forecasting.py          # forecast against current DB state
python src/pipeline/hotspot_scoring.py      # scoring with example inputs
python src/pipeline/alert_generator.py      # live Gemini alert generation

# Verify integration
python src/pipeline/app.py
# then in a separate terminal:
curl http://localhost:8080/api/hotspots/punjab-haryana
curl http://localhost:8080/api/hotspots/delhi-ncr
curl http://localhost:8080/api/hotspots/invalid-region   # expect 404
```

## 7. Known Gaps

- No automated assertions — all "pass" results above were verified by
  manually reading printed output, not by scripted comparison against
  expected values
- No regression test suite — a future code change could silently break a
  previously-working component without detection
- Forecast model tested against only ~6 distinct days of aggregated data at
  time of writing — statistically thin, disclosed in [TDD](./TECHNICAL_DESIGN_DOCUMENT.md) §3.5
- No load/concurrency testing — behavior under multiple simultaneous
  requests (particularly Gemini rate-limit contention) is untested
- No cross-browser testing performed beyond the primary development browser

## 8. Recommended Future Test Suite

If continued past the hackathon, prioritize in this order:

1. **Unit tests for pure functions** — `calculate_hotspot_score()` and the
   normalization functions are pure and trivially testable with `pytest`,
   no mocking required
2. **Mocked integration tests** for `weather_client.py` and
   `vision_classifier.py` — mock the HTTP/Gemini calls to test parsing logic
   without consuming real API quota
3. **API contract tests** — assert response shape/types for
   `/api/hotspots/<region>` using `pytest` + Flask's test client
4. **CI pipeline** (GitHub Actions) — run the above on every push, block
   merges on failure
5. **Load testing** — simulate concurrent requests to understand behavior
   under Gemini rate-limit pressure before any real production use
