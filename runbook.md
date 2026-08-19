# Demo Run Order — Clean Air & Climate Resilience
### Full pipeline walkthrough, Phase 1 → Phase 5, for recording the demo video

> Run each block in order. Where a step starts a server, open a **new terminal**
> for the next step rather than closing the running one.

---

## Phase 1 — Satellite data (Sentinel-5P via Copernicus)

```
cmd:
cd D:\Clean-air-resilience
env\Scripts\activate
python day1_checkpoint.py
```
**Shows:** real Sentinel-5P aerosol index pulled for Punjab/Haryana, saved to
`data/day1_sentinel_sample.json`.

---

## Phase 2 — Citizen photo vision classifier + weather/AQI data

```
cmd:
python test_vision_batch.py
```
**Shows:** Gemini Vision classifying real sample photos (smog/haze severity),
saved to `data/vision_test_results.json`.

```
cmd:
python src\pipeline\weather_client.py
```
**Shows:** real OpenAQ station + pollutant measurement data pulled across
Patiala, Chandigarh, Ludhiana, Karnal, saved to `data/weather_aqi_history.json`.

```
cmd:
python load_to_sqlite.py
```
**Shows:** all readings loaded into `data/air_quality.db` (SQLite).

---

## Phase 3 — Forecasting, hotspot scoring, AI-generated alert

```
cmd:
python src\pipeline\forecasting.py
```
**Shows:** daily-aggregated PM2.5 history + a real 3-day forecast.

```
cmd:
python src\pipeline\hotspot_scoring.py
```
**Shows:** the fused hotspot score (satellite + citizen + forecast).

```
cmd:
python src\pipeline\alert_generator.py
```
**Shows:** a live Gemini-generated plain-language alert for authorities.

---

## Phase 4 — Live dashboard (API + frontend + federated mock)

**Terminal 1 — start the Flask API:**
```
cmd:
python src\pipeline\app.py
```
Leave this running. Confirm it's live by visiting:
`http://localhost:8080/api/hotspots/punjab-haryana`

**Terminal 2 — serve the dashboard:**
```
cmd:
cd src\dashboard
python -m http.server 5500
```
Open `http://localhost:5500` in your browser.

**On camera:** show the map with real station markers, the live hotspot score,
3-day forecast, and generated alert. Click between the **Punjab-Haryana** and
**Delhi-NCR** buttons to show the federated two-region mock.

---

## Phase 5 — Wrap-up for the video

- Briefly show the repo structure (`src/pipeline/`, `src/dashboard/`, `data/`)
- Show `README.md`'s "What's Real vs. Simulated" table on screen
- If deployed, show the live Railway URL instead of localhost for the final cut
- Close on the two-region dashboard as the final shot — it's your strongest visual

---

## Quick full-sequence version (copy-paste block)

```
cmd:
cd D:\Clean-air-resilience
env\Scripts\activate
python day1_checkpoint.py
python test_vision_batch.py
python src\pipeline\weather_client.py
python load_to_sqlite.py
python src\pipeline\forecasting.py
python src\pipeline\hotspot_scoring.py
python src\pipeline\alert_generator.py
python src\pipeline\app.py
```
(Run the dashboard's `http.server` command in a second terminal after `app.py`
is up, since `app.py` blocks the terminal it runs in.)