# Project Build Plan
## Clean Air & Climate Resilience — AI-Powered Pollution Hotspot Detection & Forecasting Platform
### Hackathon: Build with AI — Code for Communities, 2nd Edition (Google Cloud x BRICS)

---

## 0. Project Snapshot

| Field | Detail |
|---|---|
| **Problem Statement** | #02 — Clean Air & Climate Resilience |
| **BRICS Pillar** | Sustainability |
| **Team** | Solo |
| **Timeline** | 5 days (Build: Day 1–4, Buffer + Submission: Day 5) |
| **Core Idea** | Detect hidden/hyper-local pollution hotspots by fusing real satellite data, citizen-submitted photos, and weather data — forecast air quality spikes, and generate alerts. Simulate cross-border ("federated") applicability with a two-region dashboard. |
| **Mandatory Tech** | Google AI (Gemini API, Vertex AI), Google Earth Engine, Cloud Run, Firestore/BigQuery |

**Golden rule for this build:** By the end of **Day 1**, real Earth Engine data must be flowing for your chosen region. If it isn't, stop and pivot — do not let data-sourcing problems bleed into Day 2.

---

## 0.1 Project File Structure

This is the full structure you'll build over the 5 days — not what a scaffolding tool generates, but exactly the files this plan has you create by hand, phase by phase. Use this as your map; each file below is referenced again inside the phase/step that creates it.

```
clean-air-resilience/
│
├── env/                                # Python virtual environment (Phase 1, Step 2) — do not edit manually
│
├── .env                                # Stores GEMINI_API_KEY and other secrets (Phase 2, Step 1) — never commit this
├── .gitignore                          # Ignore env/, .env, data/*.json, __pycache__/
├── requirements.txt                    # Frozen list of installed packages (generate with pip freeze, Phase 1)
├── README.md                           # Project overview + setup instructions for submission (Phase 5, Step 4)
│
├── data/                               # All pulled/generated datasets live here
│   ├── day1_earthengine_sample.json    # First real Earth Engine test pull (Phase 1, Step 7)
│   ├── vision_test_results.json        # Gemini Vision test outputs on sample photos (Phase 2, Step 3)
│   ├── weather_aqi_history.json        # Historical weather/AQI pull (Phase 2, Step 4)
│   └── sample_images/                  # Folder of 8–10 test photos for the vision classifier (Phase 2, Step 3)
│       ├── clear_sky_01.jpg
│       ├── hazy_scene_01.jpg
│       └── ...
│
├── notebooks/                          # Scratch space for testing before moving code into src/
│   ├── earthengine_explore.ipynb       # Used in Phase 1 to test Earth Engine calls before scripting them
│   └── forecast_model_test.ipynb       # Used in Phase 3 to prototype the forecasting model
│
├── src/
│   ├── pipeline/                       # All backend/AI logic lives here
│   │   ├── __init__.py
│   │   ├── earth_engine_client.py      # Wraps the Earth Engine auth + data-pull functions (Phase 1, Steps 5–7)
│   │   ├── vision_classifier.py        # Gemini Vision smog/haze classifier (Phase 2, Step 2)
│   │   ├── weather_client.py           # Weather/AQI API wrapper (Phase 2, Step 4)
│   │   ├── firestore_client.py         # save_reading() and other Firestore read/write functions (Phase 2, Step 5)
│   │   ├── forecasting.py              # train_forecast_model() / forecast_next_days() (Phase 3, Step 1)
│   │   ├── hotspot_scoring.py          # calculate_hotspot_score() fusion logic (Phase 3, Step 2)
│   │   ├── alert_generator.py          # generate_alert() Gemini prompt logic (Phase 3, Step 3)
│   │   └── app.py                      # Flask API exposing /api/hotspots/<region> (Phase 4, Step 1)
│   │
│   └── dashboard/                      # Frontend lives here
│       ├── index.html                  # Main dashboard page — map + alert panel (Phase 4, Step 2)
│       ├── style.css                   # Dashboard styling
│       ├── script.js                   # Map rendering + API calls to Flask backend
│       └── region_b_view.html          # Second region view for the federated mock (Phase 4, Step 3)
│
├── docs/                               # Everything for submission/presentation
│   ├── architecture_diagram.png        # Referenced in pitch deck slide 4 (Phase 5, Step 3)
│   ├── pitch_deck.pdf                  # Final 8–10 slide deck (Phase 5, Step 3)
│   ├── demo_video.mp4                  # Final 3–5 min demo video (Phase 5, Step 2)
│   └── brief_description.md            # Short written project description for submission (Phase 5, Step 4)
│
└── Dockerfile                          # Optional but recommended — used by Cloud Run deploy (Phase 4, Step 4)
```

**Note on what's auto-generated vs. manual:** `env/` (Step 2) and anything Cloud Run generates during `gcloud run deploy` (like build artifacts) are the only auto-created pieces. Every file above it — including `requirements.txt`, which you'll populate yourself as you install packages — is something you create or write by hand across the 5 phases.

---

## 0.2 Documentation Standards

Judges score "Presentation & Clarity" (5%), but sloppy documentation quietly hurts you elsewhere too — a judge who can't quickly understand your architecture from your README will under-credit your actual technical work. Documentation isn't a Day 5 task; it's written **as you build, phase by phase**. Each phase below ends with a "Document as you go" step for exactly this reason — don't skip it.

### A. Docstring convention (use this for every function, no exceptions)
Use **Google-style docstrings** — clean, judge-readable, and standard enough that anyone reviewing your code recognizes it immediately.

```python
def calculate_hotspot_score(satellite_aerosol, citizen_severity_score, forecasted_aqi):
    """Fuses satellite, citizen, and forecast signals into a single hotspot score.

    Args:
        satellite_aerosol (float): Aerosol index from Sentinel-5P, 0-1 normalized.
        citizen_severity_score (int): Gemini Vision severity rating, 1 (Low) to 4 (Severe).
        forecasted_aqi (float): Predicted AQI value from the forecasting model.

    Returns:
        float: Composite hotspot score between 0 and 1, where values above 0.7
            indicate a high-priority alert region.
    """
```

**Rule of thumb:** if a function is more than 3 lines or makes an external API call (Earth Engine, Gemini, weather API, Firestore), it gets a docstring. No exceptions — this is what makes your repo look like an engineered system rather than hackathon scramble code.

### B. Inline comments — what to comment vs. not
- **Do comment:** any non-obvious decision (e.g. *why* you chose a 0.4/0.3/0.3 weighting in hotspot scoring, *why* linear regression over a heavier model, *why* a value is hardcoded for the demo)
- **Don't comment:** obvious code (`# increment counter` above `i += 1` adds noise, not clarity)
- **Always mark simulated/demo-only logic explicitly**, e.g.:
  ```python
  # DEMO NOTE: citizen photo feed is simulated from sample_images/ for this submission.
  # Production version would accept live uploads via a mobile/WhatsApp intake endpoint.
  ```
  This single habit does a lot of work — it shows judges you know exactly what's real vs. simulated, which reads as engineering maturity rather than a gap.

### C. README.md — full template
This is the first thing a judge opens. Build it incrementally across the 5 days, not all at once on Day 5.

```markdown
# Clean Air & Climate Resilience — AI Hotspot Detection & Forecasting Platform
Built for: Build with AI — Code for Communities 2nd Edition (Google Cloud x BRICS)
Problem Statement #02 | BRICS Pillar: Sustainability

## Overview
[2-3 sentence summary of what the platform does and why it matters]

## Problem
[Restate the problem statement in your own words — 3-4 sentences]

## Solution Architecture
[Embed architecture_diagram.png here]
[One paragraph walking through the data flow: satellite + citizen + weather → fusion → forecast → alert]

## Tech Stack
- Google Earth Engine — satellite aerosol/pollution index data
- Gemini API (Vision) — citizen photo smog/haze classification
- Gemini API (Text) — alert generation
- [Weather API name] — historical AQI/weather data
- Firestore — data storage
- Flask — backend API
- Cloud Run — deployment

## What's Real vs. Simulated (read this first)
| Component | Status |
|---|---|
| Satellite data (Sentinel-5P) | Real, live Earth Engine pull |
| Citizen photo classification | Real Gemini Vision, tested on sample images |
| Weather/AQI history | Real, [source name] |
| Citizen photo intake (live upload) | Simulated — architecture supports live intake, not wired for demo |
| Cross-border data sharing | Simulated via two-region mock — see below |

## Setup Instructions
1. Clone the repo: `git clone [your-repo-url]`
2. Create virtual environment: `python -m venv env`
3. Activate: `source env/bin/activate` (Mac/Linux) or `env\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Add your `.env` file with `GEMINI_API_KEY` and weather API key
6. Authenticate Earth Engine: `earthengine authenticate`
7. Run locally: `python src/pipeline/app.py`

## Live Demo
- Deployed link: [your Cloud Run URL]
- Demo video: [link]

## Cross-Border Applicability
[2-3 sentences on the federated model story — this directly targets the 20% judging criterion, don't skip it]

## Team
[Your name / solo]
```

### D. Architecture diagram (docs/architecture_diagram.png)
Doesn't need to be fancy — a simple boxes-and-arrows diagram is enough, made in draw.io, Excalidraw, or even Google Slides:

```
[Satellite Data] ─┐
[Citizen Photos] ─┼──> [Fusion Logic] ──> [Hotspot Score] ──> [Gemini Alert Generator] ──> [Dashboard]
[Weather/AQI]    ─┘                              │
                                                  └──> [Forecasting Model]
```

Build this on Day 2 or 3 once your pipeline shape is confirmed, not Day 5 under time pressure — it's also useful for you as a build reference, not just for the judges.

### E. brief_description.md (submission requirement)
Keep this to 150–250 words — a condensed version of the README's Overview + Problem + Solution sections, written for someone who won't read your full repo.

---

## PHASE 1 — Day 1: Environment Setup & Data Access

**Goal for the day:** A working dev environment, a Google Cloud project with the right APIs enabled, and — most importantly — real Earth Engine data pulled for one confirmed region.

### Step 1: Create the project folder structure
Set up a clean structure now so you're not reorganizing mid-build later.

```
cmd:
mkdir clean-air-resilience
cd clean-air-resilience
mkdir data notebooks src src/pipeline src/dashboard docs
```

**Why:** `data/` holds pulled datasets, `notebooks/` is for quick experiments (Earth Engine calls, prompt testing), `src/pipeline` holds your actual backend logic, `src/dashboard` holds the frontend, `docs/` holds your pitch deck and README.

---

### Step 2: Create a Python virtual environment
Keeps your dependencies isolated so nothing conflicts with other projects on your machine.

```
cmd:
python -m venv env
```

**Activate it:**

```
cmd (Windows):
env\Scripts\activate

cmd (Mac/Linux):
source env/bin/activate
```

**Verify it's active** — your terminal prompt should now show `(env)` at the start of the line.

---

### Step 3: Install core dependencies
Install everything you'll need across the whole 5 days now, so you're not stopping to `pip install` mid-flow later.

```
cmd:
pip install earthengine-api google-cloud-firestore google-cloud-bigquery google-generativeai flask python-dotenv pandas numpy scikit-learn requests
```

**What each does:**
- `earthengine-api` → pulls satellite imagery/indices
- `google-cloud-firestore` / `google-cloud-bigquery` → data storage
- `google-generativeai` → Gemini API calls (vision + text)
- `flask` → lightweight backend for your dashboard API
- `pandas`, `numpy`, `scikit-learn` → forecasting/data processing
- `python-dotenv` → manage API keys safely
- `requests` → weather API calls

---

### Step 4: Set up a Google Cloud project
1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a new project (e.g. `clean-air-resilience`)
2. Enable billing (Google Cloud free tier / hackathon credits should cover a 5-day build)
3. Enable the following APIs from the console:
   - Earth Engine API
   - Vertex AI API
   - Generative Language API (Gemini)
   - Cloud Firestore API
   - BigQuery API
   - Cloud Run API

**Why this matters:** APIs can take a few minutes to fully activate — do this early on Day 1, not when you're mid-build and blocked.

---

### Step 5: Authenticate Earth Engine
Earth Engine requires its own registration + auth, separate from general Cloud APIs.

1. Register for Earth Engine access at [signup.earthengine.google.com](https://signup.earthengine.google.com) (use your Cloud project — approval is usually near-instant for existing Cloud projects)
2. Authenticate locally:

```
cmd:
earthengine authenticate
```

3. Test the connection in a Python shell:

```python
import ee
ee.Initialize(project='your-project-id')
print(ee.Image("COPERNICUS/S5P/OFFL/L3_AER_AI").getInfo())
```

If this returns image metadata without error, you're connected.

---

### Step 6: Lock in your target region
Pick **one specific, well-documented pollution region** — don't leave this open-ended, it will eat your day.

**Recommended:** a district in the Indo-Gangetic Plain (e.g. around Punjab/Haryana) during/near stubble-burning season — it's a real, well-documented, BRICS-relevant story (cross-border smog drift affecting multiple regions), and satellite aerosol data for it is reliably available.

Write down:
- Region name + approximate lat/long bounding box
- Date range you'll pull data for (pick a real historical window with known pollution events — easier to find and more convincing than "today")

---

### Step 7: Pull your first real dataset (checkpoint for the day)
Use Sentinel-5P aerosol index (pollution-relevant) as your first real pull.

```python
import ee
ee.Initialize(project='your-project-id')

region = ee.Geometry.Rectangle([75.5, 29.5, 77.5, 31.5])  # replace with your region
collection = ee.ImageCollection("COPERNICUS/S5P/OFFL/L3_AER_AI") \
    .filterDate('2024-10-15', '2024-11-15') \
    .filterBounds(region)

image = collection.mean()
print(image.getInfo())
```

**End-of-Day-1 checkpoint:** you should have real aerosol/pollution index values printed for your region. Save this as `data/day1_earthengine_sample.json`.

> ⚠️ **Decision point:** If this isn't working cleanly by tonight, pivot to Problem Statement #01 (Digital Infrastructure & Governance) rather than losing Day 2 to the same struggle.

### Step 8: Document as you go
- Start `README.md` using the template in Section 0.2 — fill in Overview, Problem, and the Tech Stack table now while it's fresh
- Run `pip freeze > requirements.txt` so it's accurate from Day 1 onward, not reconstructed later
- Add a docstring to any function you wrote today (Section 0.2-A convention)

---

## PHASE 2 — Day 2: Vision Pipeline & Weather/AQI Data

**Goal for the day:** Citizen photo → pollution severity classification working via Gemini Vision, plus real historical weather/AQI data pulled and stored.

### Step 1: Set up your Gemini API key
```
cmd:
echo GEMINI_API_KEY=your-key-here >> .env
```
Get your key from [aistudio.google.com](https://aistudio.google.com).

### Step 2: Build the Gemini Vision smog/haze classifier
Create `src/pipeline/vision_classifier.py`:

```python
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def classify_air_quality(image_path):
    img = genai.upload_file(image_path)
    response = model.generate_content([
        img,
        "Analyze this photo for visible air pollution/smog/haze. "
        "Rate severity (Low/Moderate/High/Severe) and briefly explain visual indicators."
    ])
    return response.text
```

**Explanation:** This takes a citizen-submitted photo and returns a structured severity rating with reasoning — this is your "citizen-sourced data" input stream from the problem statement.

### Step 3: Test with sample images
Gather 8–10 test images (mix of clear sky and hazy/smoggy scenes — search royalty-free sources or use your own photos) and run them through the classifier. Save outputs to `data/vision_test_results.json` — you'll want these for your demo video later.

### Step 4: Pull historical weather + AQI data
Use a free weather/AQI API (e.g. OpenWeatherMap Air Pollution API or a public government AQI dataset).

```python
import requests

def get_aqi_data(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution/history"
    params = {"lat": lat, "lon": lon, "start": start_ts, "end": end_ts, "appid": api_key}
    return requests.get(url, params=params).json()
```

### Step 5: Store data in Firestore
```python
from google.cloud import firestore

db = firestore.Client()

def save_reading(region, timestamp, aqi_value, source):
    db.collection("air_quality_readings").add({
        "region": region,
        "timestamp": timestamp,
        "aqi_value": aqi_value,
        "source": source  # "satellite" / "citizen_photo" / "weather_api"
    })
```

**End-of-Day-2 checkpoint:** Vision classifier working on test images + real weather/AQI history stored in Firestore for your region.

### Step 6: Document as you go
- Docstring `vision_classifier.py` and `weather_client.py` functions (Section 0.2-A)
- Update README's "What's Real vs. Simulated" table — mark vision classification and weather data as real now that they're confirmed working
- Sketch a first draft of `architecture_diagram.png` (Section 0.2-D) — your pipeline shape is confirmed enough now to diagram it

---

## PHASE 3 — Day 3: Forecasting & Hotspot Detection Logic

**Goal for the day:** A forecasting model that predicts AQI spikes, and logic that fuses satellite + citizen + weather signals into a single hotspot score, plus AI-generated alerts.

### Step 1: Build a simple forecasting model
Don't over-engineer this — a clear, working model beats a fancy but fragile one.

```python
from sklearn.linear_model import LinearRegression
import pandas as pd
import numpy as np

def train_forecast_model(df):
    # df columns: day_index, aqi_value
    X = df[['day_index']]
    y = df['aqi_value']
    model = LinearRegression()
    model.fit(X, y)
    return model

def forecast_next_days(model, last_day_index, days_ahead=3):
    future_days = np.array([[last_day_index + i] for i in range(1, days_ahead + 1)])
    return model.predict(future_days)
```

**Why linear regression is fine here:** judges are scoring whether you have a *working, explainable* forecasting layer feeding into a real decision (alerting) — not competing on model sophistication. If time allows on Day 5, you can upgrade this.

### Step 2: Build hotspot scoring logic
Fuse the three signal types into one score per region:

```python
def calculate_hotspot_score(satellite_aerosol, citizen_severity_score, forecasted_aqi):
    # weights can be tuned/justified in your pitch
    weights = {"satellite": 0.4, "citizen": 0.3, "forecast": 0.3}
    normalized_citizen = citizen_severity_score / 4  # Low=1 ... Severe=4
    return (
        weights["satellite"] * satellite_aerosol +
        weights["citizen"] * normalized_citizen +
        weights["forecast"] * (forecasted_aqi / 500)  # normalize against AQI scale
    )
```

### Step 3: Generate the alert using Gemini
This is your "reasoning" moment — turn raw numbers into a policymaker-readable alert.

```python
def generate_alert(region, hotspot_score, forecast_trend):
    prompt = f"""
    Region: {region}
    Hotspot Score: {hotspot_score:.2f} (0-1 scale)
    Forecast Trend: {forecast_trend}

    Write a concise, plain-language alert for a local environmental authority,
    explaining the risk level, likely cause, and recommended immediate action.
    """
    response = model.generate_content(prompt)
    return response.text
```

**End-of-Day-3 checkpoint:** Given a region's data, your pipeline should output a forecast, a hotspot score, and a generated alert end-to-end.

### Step 4: Document as you go
- Docstring `forecasting.py`, `hotspot_scoring.py`, and `alert_generator.py` (Section 0.2-A)
- Comment your weighting decision in `calculate_hotspot_score()` — explain *why* 0.4/0.3/0.3, even briefly (Section 0.2-B)
- Finalize `architecture_diagram.png` now that the forecasting + alert layer is confirmed working

---

## PHASE 4 — Day 4: Dashboard, Federated Mock, and Deployment

**Goal for the day:** A working dashboard, a two-region "federated" mock to sell cross-border applicability, and a live deployment — plus start capturing demo footage.

### Step 1: Build a minimal Flask API layer
```
cmd:
touch src/pipeline/app.py
```

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/hotspots/<region>")
def get_hotspots(region):
    # call your Phase 3 functions here, return JSON
    return jsonify({"region": region, "hotspot_score": 0.72, "alert": "..."})

if __name__ == "__main__":
    app.run(debug=True, port=8080)
```

### Step 2: Build a simple frontend dashboard
Keep this intentionally simple — a clean map/chart view beats an over-built UI you didn't have time to polish. A single HTML page with a map (Google Maps JS API or Leaflet) plotting hotspot markers, plus a side panel showing the AI-generated alert, is enough.

### Step 3: Build the two-region "federated" mock
This is what sells the "Cross-Border Applicability" judging criterion (20% of your score).

- Duplicate your pipeline logic to run against **two regions** (e.g., your Indian region + a second nearby region)
- Show both dashboards querying the **same underlying model/logic**, side by side
- In your pitch, explicitly state: *"This demonstrates the interoperable architecture — the same predictive model can serve multiple national dashboards without requiring raw data to cross borders, only the model outputs."*

### Step 4: Deploy to Cloud Run
```
cmd:
gcloud run deploy clean-air-resilience \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated
```

### Step 5: Start recording demo footage now
Don't leave all recording to Day 5 — capture screen recordings of each working piece today (Earth Engine pull, vision classification, alert generation, dashboard) as insurance against last-day time pressure.

**End-of-Day-4 checkpoint:** Live deployed link working, two-region mock visible, raw demo footage captured for at least 3 of the 4 pipeline stages.

### Step 6: Document as you go
- Mark every simulated component clearly with a `# DEMO NOTE:` comment (Section 0.2-B) — do this pass across the whole `src/` folder today, not Day 5
- Fill in README's "Setup Instructions" and "Live Demo" sections with your actual deployed link
- Write the "Cross-Border Applicability" paragraph in README while the two-region mock is fresh in your head

---

## PHASE 5 — Day 5: Buffer, Demo Video, Pitch Deck, Submission

**Goal for the day:** Everything finalized, tested, and submitted early — not at the deadline.

### Step 1: Run a full bug-fixing pass
Checklist:
- [ ] Deployed link loads without errors
- [ ] Both region dashboards return valid data
- [ ] Vision classifier handles a new, untested image correctly
- [ ] Forecast + alert generation runs end-to-end without manual intervention
- [ ] No hardcoded values that would break if re-run

### Step 2: Record the final demo video (3–5 minutes)
Structure it to narrate the AI pipeline explicitly — this directly targets the 25% "AI Technical Execution" criterion:
1. Problem framing (15 sec)
2. Show a citizen photo submitted → Gemini Vision classifies it live (30 sec)
3. Show real satellite data for the region (30 sec)
4. Show the forecast + hotspot score being calculated (30 sec)
5. Show the generated policymaker alert (30 sec)
6. Show the two-region federated dashboard (45 sec)
7. Close with the cross-border scalability pitch (30 sec)

### Step 3: Build the pitch deck (8–10 slides)
Suggested structure:
1. Title + team
2. The problem (with the "macro-monitoring misses hyper-local/cross-border events" framing)
3. The solution overview
4. Architecture diagram (satellite + citizen + weather → fusion → forecast → alert)
5. AI/tech stack used (be explicit about Gemini, Earth Engine, Vertex AI)
6. Demo screenshots
7. Cross-border applicability / federated model story
8. Impact potential
9. What's simulated vs. real (be upfront — judges respect honesty)
10. Roadmap / what's next

### Step 4: Finalize documentation and submission materials
Since you've been documenting incrementally (Section 0.2, plus the "Document as you go" step at the end of each phase), this is a **review pass, not a from-scratch write-up**:
- [ ] README.md — read it top to bottom as if you're a judge seeing the project cold; fill any gaps
- [ ] "What's Real vs. Simulated" table — confirm it's accurate and complete (this table matters more than people expect — it signals engineering honesty)
- [ ] Every function in `src/pipeline/` has a docstring (Section 0.2-A) — spot check `hotspot_scoring.py` and `alert_generator.py` especially, they're your core logic
- [ ] `architecture_diagram.png` matches what you actually built (not the Day 1 plan)
- [ ] Write `docs/brief_description.md` (150-250 words, Section 0.2-E) — this is the one piece of documentation you haven't touched yet
- [ ] Public GitHub repo — confirm it's actually public/accessible, and `.env` is in `.gitignore` (never commit API keys)
- [ ] Deployed working link — test it fresh, not from memory
- [ ] Demo video — uploaded, link tested
- [ ] Pitch deck — PDF export, matches the architecture diagram and real-vs-simulated framing in README

### Step 5: Submit early
Submit several hours before the deadline, not at the last minute — leaves buffer for upload issues or last-minute link/access problems.

---

## Quick Reference: Daily Checkpoints

| Day | Checkpoint |
|---|---|
| 1 | Real Earth Engine data pulled for your region — **hard go/no-go decision point** |
| 2 | Vision classifier working + real weather/AQI data stored |
| 3 | Forecast → hotspot score → AI-generated alert working end-to-end |
| 4 | Live deployed link + two-region federated mock + demo footage captured |
| 5 | Bug fixes done, video + deck finalized, submitted early |
