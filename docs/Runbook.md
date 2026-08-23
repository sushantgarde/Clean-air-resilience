# Runbook / Operations Manual

## Clean Air & Climate Resilience

**Version:** 1.0
**Last Updated:** August 2026
**Service:** Flask app on Render (free tier)
**Live URL:** https://clean-air-resilience.onrender.com

---

## Table of Contents

- [1. Purpose](#1-purpose)
- [2. Service Summary](#2-service-summary)
- [3. Starting the Service](#3-starting-the-service)
- [4. Stopping the Service](#4-stopping-the-service)
- [5. Health Checks](#5-health-checks)
- [6. Monitoring](#6-monitoring)
- [7. Common Operational Tasks](#7-common-operational-tasks)
- [8. Incident Response](#8-incident-response)
- [9. Data Refresh Procedure](#9-data-refresh-procedure)
- [10. Escalation](#10-escalation)
- [11. Maintenance Windows](#11-maintenance-windows)

---

## 1. Purpose

This runbook describes how to operate, monitor, and troubleshoot Clean Air &
Climate Resilience once deployed. It is written for whoever is on point to
keep the demo/service running — for a hackathon context, that's the project
owner, but the structure mirrors what a real on-call runbook would cover.

## 2. Service Summary

| Property | Value |
|---|---|
| Hosting | Render (free web service tier) |
| Process | Single Flask process serving both API and static dashboard |
| Start command | `python src/pipeline/app.py` |
| Port | Render-assigned via `$PORT` env var |
| Data store | SQLite (`data/air_quality.db`), committed to the repo |
| External dependencies | Copernicus Data Space, OpenAQ, Gemini API (all free tier) |
| Uptime model | **Not guaranteed** — free tier spins down after inactivity |

## 3. Starting the Service

### 3.1 Local

```bash
cd Clean-air-resilience
source env/bin/activate      # Windows: env\Scripts\activate
python src/pipeline/app.py
```
Service available at `http://localhost:8080`.

### 3.2 Production (Render)

The service starts automatically:
- On every push to the connected branch (`main`)
- On manual trigger: Render dashboard → **Manual Deploy → Deploy latest commit**
- On incoming request, if the service had spun down due to inactivity (cold start, ~30–60s)

**Before a live demo or presentation:** manually visit the live URL
**at least 1 minute beforehand** to force a cold start ahead of time, so the
audience doesn't wait through it.

## 4. Stopping the Service

Render free-tier services cannot be manually "stopped" in the traditional
sense — they spin down automatically after a period of inactivity (typically
~15 minutes without a request) and restart on the next incoming request.

To fully suspend a service: Render dashboard → **Settings → Suspend Service**.

## 5. Health Checks

### 5.1 Manual health check

```bash
curl -o /dev/null -s -w "%{http_code}\n" https://clean-air-resilience.onrender.com/
```
Expected: `200`

### 5.2 API functional check

```bash
curl https://clean-air-resilience.onrender.com/api/hotspots/punjab-haryana
```
Expected: JSON response with populated `hotspot_score`, `forecast_pm25_next_3_days`,
`trend`, and `alert` fields — not an error object.

### 5.3 Dashboard visual check

Open the live URL in a browser and confirm:
- [ ] Logo renders in the header (not broken image)
- [ ] Map loads with station markers visible
- [ ] Hotspot score, forecast, and alert panels populate (not stuck on "Loading...")
- [ ] Region toggle buttons switch data correctly

## 6. Monitoring

**Current state: no automated monitoring/alerting is configured** — this is
a hackathon-scale deployment. Available observability:

| Tool | What it shows |
|---|---|
| Render Dashboard → Logs | Live application logs, including Flask request logs and unhandled exception tracebacks |
| Render Dashboard → Metrics | CPU/memory usage over time (free tier has limited retention) |
| Render Dashboard → Events | Deploy history, restarts, spin-down events |

**Manual monitoring routine (recommended before any demo):**
1. Check Render dashboard shows "Live" status (not "Failed" or "Suspended")
2. Run the health checks in Section 5
3. Check the **Logs** tab for any recent `500` errors or unhandled exceptions

## 7. Common Operational Tasks

### 7.1 Redeploy after a code change

```bash
git add .
git commit -m "<description>"
git push
```
Render auto-deploys from the connected branch. Watch the **Deploys** tab for
build progress.

### 7.2 Update an environment variable / secret

1. Render dashboard → service → **Environment**
2. Edit the value
3. Save — this triggers an automatic redeploy

### 7.3 Force a clean rebuild (clear cache)

Render dashboard → **Manual Deploy → Clear build cache & deploy**

Use this when:
- A dependency version change doesn't seem to be taking effect
- Suspecting a stale/corrupted build cache after a Python version change

### 7.4 Refresh underlying pollution data

See [Section 9](#9-data-refresh-procedure).

## 8. Incident Response

| Symptom | Likely Cause | Response |
|---|---|---|
| Dashboard shows "Error loading data" | API returning non-200 or unreachable | Check Render logs for traceback; verify `data/air_quality.db` exists in the deployed instance (see Deployment Guide §9) |
| `/api/hotspots/<region>` returns `500` | Gemini API rate-limited, or SQLite query failure | Check Render logs for the specific exception; if Gemini `429`, wait ~1 minute and retry (free-tier RPM window resets) |
| Site loads but map is blank | Leaflet CDN unreachable, or station coordinates malformed | Check browser console for JS errors; verify CDN links in `index.html` are reachable |
| Site doesn't load at all (Render shows "Failed") | Build failure — check the specific error in build logs | Common causes: missing `runtime.txt` (slow/failed source build), missing env var, or a dependency version conflict |
| First request after idle takes 30–60s | Render free-tier cold start | Expected behavior, not an incident — no action needed beyond waiting |

**If an incident occurs during a live demo:** have `http://localhost:8080`
running as a fallback on the presenter's machine, since local execution has
no cold-start or rate-limit surprises tied to a public deploy.

## 9. Data Refresh Procedure

The committed `data/air_quality.db` is a point-in-time snapshot. To refresh
it with newer OpenAQ readings:

```bash
python src/pipeline/weather_client.py   # re-pull latest station data
python load_to_sqlite.py                # reload into SQLite
```

Then commit the updated database:
```bash
git add data/air_quality.db
git commit -m "Refresh air quality data"
git push
```

Render will redeploy with the updated dataset. **Note:** this re-triggers
OpenAQ API calls across all 4 configured center points — be mindful this is
subject to OpenAQ's own rate limits if run repeatedly in a short window.

## 10. Escalation

For a solo hackathon project, there is no formal on-call chain. If a
critical failure occurs close to a submission deadline:

1. Fall back to the local (`localhost:8080`) instance for any live
   demonstration
2. If the deployed URL is required for submission and is down, check Render
   status directly at [render.com](https://render.com) for a platform-wide
   outage before assuming the issue is project-specific
3. Worst case: submit with the GitHub repo and a recorded demo video as the
   primary evidence, noting the live URL's temporary status in the
   submission notes

## 11. Maintenance Windows

No scheduled maintenance windows are defined for this project. Render may
perform its own platform maintenance without prior notice on the free tier
(no SLA is provided at this tier).
