# API Documentation

## Clean Air & Climate Resilience

**Version:** 1.0
**Base URL (local):** `http://localhost:8080`
**Base URL (production):** `https://clean-air-resilience.onrender.com`
**Last Updated:** August 2026

---

## Table of Contents

- [1. Overview](#1-overview)
- [2. Authentication](#2-authentication)
- [3. Endpoints](#3-endpoints)
  - [3.1 GET /](#31-get-)
  - [3.2 GET /api/hotspots](#32-get-apihotspots)
  - [3.3 GET /api/hotspots/<region_key>](#33-get-apihotspotsregion_key)
  - [3.4 GET /docs/<filename>](#34-get-docsfilename)
- [4. Data Objects](#4-data-objects)
- [5. Error Handling](#5-error-handling)
- [6. Rate Limits](#6-rate-limits)
- [7. Example Usage](#7-example-usage)
- [8. Changelog](#8-changelog)

---

## 1. Overview

The Clean Air & Climate Resilience API exposes computed pollution hotspot
data — a fused risk score, a 3-day PM2.5 forecast, and an AI-generated
plain-language alert — for supported regions. It also serves the project's
static dashboard from the same process.

All responses are JSON unless otherwise noted. All computation happens
**synchronously per request** — each call re-runs the forecasting model and
calls the Gemini API live; there is no response caching in this version.

## 2. Authentication

**None required for consumers of this API.** All endpoints are public.

Internally, the server authenticates to three upstream services using
environment variables (never exposed to API consumers):

| Variable | Used for |
|---|---|
| `SENTINELHUB_CLIENT_ID` / `SENTINELHUB_CLIENT_SECRET` | Copernicus Data Space OAuth |
| `OPENAQ_API_KEY` | OpenAQ ground-station data |
| `GEMINI_API_KEY` | Gemini Vision (classification) and Gemini Text (alert generation) |

## 3. Endpoints

### 3.1 `GET /`

Serves the dashboard's `index.html`.

**Response:** `200 OK`, `Content-Type: text/html`

---

### 3.2 `GET /api/hotspots`

Returns hotspot data for **all** supported regions in a single call.

**Request:**
```http
GET /api/hotspots HTTP/1.1
Host: clean-air-resilience.onrender.com
```

**Response:** `200 OK`

```json
[
  {
    "region": "Punjab-Haryana Belt",
    "hotspot_score": 0.427,
    "forecast_pm25_next_3_days": [34.5506786660433, 32.5029346267726, 30.455190587502],
    "trend": "declining",
    "alert": "Air Quality Alert: Punjab-Haryana Belt\n\nRisk Level: Moderate..."
  },
  {
    "region": "Delhi-NCR (Federated Region B)",
    "hotspot_score": 0.612,
    "forecast_pm25_next_3_days": [41.2, 43.8, 46.1],
    "trend": "rising",
    "alert": "Air Quality Alert: Delhi-NCR\n\nRisk Level: High..."
  }
]
```

---

### 3.3 `GET /api/hotspots/<region_key>`

Returns hotspot data for a **single** region.

**Path parameters:**

| Parameter | Type | Description |
|---|---|---|
| `region_key` | string | One of: `punjab-haryana`, `delhi-ncr` |

**Request:**
```http
GET /api/hotspots/punjab-haryana HTTP/1.1
Host: clean-air-resilience.onrender.com
```

**Response:** `200 OK`

```json
{
  "region": "Punjab-Haryana Belt",
  "hotspot_score": 0.427,
  "forecast_pm25_next_3_days": [34.5506786660433, 32.5029346267726, 30.455190587502],
  "trend": "declining",
  "alert": "**Air Quality Alert: Punjab-Haryana Belt**\n\n**Risk Level:** Moderate (Score: 0.43)\n**Trend:** Declining\n\nAir quality concerns in the Patiala, Chandigarh, Ludhiana, and Karnal regions remain elevated but are trending downward over the next three days. The current risk is primarily driven by seasonal agricultural residue burning.\n\n**Recommended Action:**\n* **Residents:** Minimize outdoor physical exertion...\n* **Authorities:** Suspend non-essential construction..."
}
```

**Error response** — unknown region: `404 Not Found`

```json
{
  "error": "Unknown region 'invalid-region'"
}
```

---

### 3.4 `GET /docs/<filename>`

Serves static files from the project's `docs/` directory (used for the
dashboard's logo/favicon assets).

**Request:**
```http
GET /docs/website-logo.svg HTTP/1.1
```

**Response:** `200 OK`, `Content-Type: image/svg+xml`

## 4. Data Objects

### HotspotResponse

| Field | Type | Description |
|---|---|---|
| `region` | string | Human-readable region display name |
| `hotspot_score` | float | Fused risk score, range `0.0`–`1.0`. Higher = more urgent |
| `forecast_pm25_next_3_days` | array[float] | Predicted daily mean PM2.5 (µg/m³) for the next 3 days |
| `trend` | string | `"rising"` or `"declining"`, derived from forecast direction |
| `alert` | string | Gemini-generated plain-language alert (Markdown-formatted text) |

### Hotspot Score Composition

The score is a weighted fusion of three normalized signals:

| Signal | Weight | Normalization |
|---|---|---|
| Satellite aerosol index | 0.4 | `(value + 2) / 4`, clamped to `[0, 1]` |
| Citizen photo severity | 0.3 | `severity_score / 4` (1=Low, 2=Moderate, 3=High, 4=Severe) |
| Forecasted PM2.5 | 0.3 | `min(forecast_value / 500, 1)` |

## 5. Error Handling

| Status Code | Meaning | When it occurs |
|---|---|---|
| `200 OK` | Success | Valid request, data returned |
| `404 Not Found` | Unknown region | `region_key` not in the `REGIONS` config |
| `500 Internal Server Error` | Upstream failure | Gemini API rate-limited/unavailable, SQLite query failure, or missing database |

**Example 500 scenario:** If the Gemini free-tier rate limit (5–15 requests/
minute depending on model) is exceeded, alert generation will raise an
exception, surfaced as a 500 response with a traceback in server logs (not
exposed to the client in production).

## 6. Rate Limits

**This API itself has no rate limiting.** However, it is bottlenecked by
upstream free-tier limits:

| Upstream service | Free-tier limit | Impact |
|---|---|---|
| Gemini API (`gemini-3.1-flash-lite`) | ~15 requests/minute | Each `/api/hotspots/<region>` call makes 1 Gemini call for alert generation |
| Render free web service | Spins down after inactivity | First request after idle period may take 30–60s (cold start) |

## 7. Example Usage

**cURL:**
```bash
curl https://clean-air-resilience.onrender.com/api/hotspots/punjab-haryana
```

**JavaScript (fetch):**
```javascript
const resp = await fetch('/api/hotspots/punjab-haryana');
const data = await resp.json();
console.log(data.hotspot_score, data.trend);
```

**Python (requests):**
```python
import requests
resp = requests.get("https://clean-air-resilience.onrender.com/api/hotspots/punjab-haryana")
data = resp.json()
print(data["hotspot_score"], data["trend"])
```

## 8. Changelog

| Version | Date | Changes |
|---|---|---|
| 1.0 | Aug 2026 | Initial API: `/api/hotspots`, `/api/hotspots/<region>`, `/docs/<filename>`, dashboard serving from `/` |
