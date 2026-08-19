from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.pipeline.forecasting import load_pm25_daily_series, train_forecast_model, forecast_next_days
from src.pipeline.hotspot_scoring import calculate_hotspot_score
from src.pipeline.alert_generator import generate_alert

# Path to the dashboard's static files (src/dashboard/), relative to this file
DASHBOARD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "dashboard")

# Path to the docs folder (project root/docs/) — holds website-logo.svg
DOCS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs")

app = Flask(__name__, static_folder=DASHBOARD_DIR, static_url_path="")
CORS(app)  # harmless to keep even though the dashboard is now same-origin

# Static region metadata — extend this dict to add more regions to the mock
# DEMO NOTE: delhi-ncr uses illustrative satellite/citizen values, not a live
# pull — this demonstrates the pipeline generalizes to a second region without
# code changes. Swap in a real Sentinel-5P pull + Gemini Vision test for NCR
# if time allows before submission.
REGIONS = {
    "punjab-haryana": {
        "display_name": "Punjab-Haryana Belt",
        "satellite_aerosol": -0.18,   # from data/day1_sentinel_sample.json
        "citizen_severity_score": 3,  # High, from Gemini Vision test results
    },
    "delhi-ncr": {
        "display_name": "Delhi-NCR (Downwind Region)",
        "satellite_aerosol": 0.35,    # illustrative — downwind smoke accumulation tends to read higher
        "citizen_severity_score": 4,  # Severe — NCR typically sees compounded urban + drifted smoke
    }
}


def compute_region_status(region_key):
    """Runs the full pipeline (forecast -> score -> alert) for one region.

    Args:
        region_key (str): Key into the REGIONS dict.

    Returns:
        dict: Hotspot score, forecast, and generated alert for the region.
    """
    region = REGIONS[region_key]

    df = load_pm25_daily_series(recent_days=90)
    model = train_forecast_model(df)
    last_day = df["day_index"].max()
    forecast = forecast_next_days(model, last_day, days_ahead=3)
    forecast_mean = float(forecast.mean())

    score = calculate_hotspot_score(
        satellite_aerosol=region["satellite_aerosol"],
        citizen_severity_score=region["citizen_severity_score"],
        forecasted_aqi=forecast_mean
    )

    trend = "rising" if forecast[-1] > forecast[0] else "declining"
    alert_text = generate_alert(
        region=region["display_name"],
        hotspot_score=score,
        forecast_trend=f"{trend} over the next 3 days"
    )

    return {
        "region": region["display_name"],
        "hotspot_score": score,
        "forecast_pm25_next_3_days": forecast.tolist(),
        "trend": trend,
        "alert": alert_text
    }


@app.route("/")
def serve_dashboard():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/docs/<path:filename>")
def serve_docs(filename):
    return send_from_directory(DOCS_DIR, filename)


@app.route("/api/hotspots/<region_key>")
def get_hotspot(region_key):
    if region_key not in REGIONS:
        return jsonify({"error": f"Unknown region '{region_key}'"}), 404
    return jsonify(compute_region_status(region_key))


@app.route("/api/hotspots")
def get_all_hotspots():
    return jsonify([compute_region_status(k) for k in REGIONS])


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)