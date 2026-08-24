"""
Live data refresh script — run on a schedule (via GitHub Actions) to keep
the deployed dashboard's underlying data current, rather than static from
a one-time Day 1/Day 2 pull.

Refreshes:
1. Satellite aerosol index — rolling recent window (last 14 days) instead
   of the fixed historical stubble-burning window used for the original
   Day 1 checkpoint (that file is left untouched as an evidence artifact).
2. OpenAQ ground-station readings — same station/center logic as
   weather_client.py, re-pulled fresh.
3. SQLite database — fully rebuilt from the fresh pull (not appended),
   so re-running this repeatedly doesn't accumulate duplicate rows.

Output:
- data/live_satellite_sample.json  (rolling satellite summary)
- data/weather_aqi_history.json    (fresh OpenAQ pull, local-only, gitignored)
- data/air_quality.db              (rebuilt from fresh data)
"""

import json
import os
from datetime import datetime, timedelta

import numpy as np
from sentinelhub import (
    SentinelHubRequest, DataCollection, MimeType, BBox, CRS, bbox_to_dimensions,
)

from src.pipeline.sh_config import config
from src.pipeline.weather_client import get_stations, get_station_sensors, get_sensor_measurements
from src.pipeline.db_client import init_db, save_reading, DB_PATH


# ---------------------------------------------------------------------------
# 1. Satellite refresh — rolling window
# ---------------------------------------------------------------------------

REGION_NAME = "Punjab-Haryana Belt (Indo-Gangetic Plain)"
BBOX_COORDS = [75.5, 29.5, 77.5, 31.5]
ROLLING_WINDOW_DAYS = 14


def refresh_satellite():
    print("=== Refreshing satellite data (rolling window) ===")

    s5p_cdse = DataCollection.SENTINEL5P.define_from(
        "s5p_cdse", service_url="https://sh.dataspace.copernicus.eu"
    )

    today = datetime.utcnow().date()
    start = today - timedelta(days=ROLLING_WINDOW_DAYS)
    time_interval = (start.isoformat(), today.isoformat())

    bbox = BBox(bbox=BBOX_COORDS, crs=CRS.WGS84)
    size = bbox_to_dimensions(bbox, resolution=1000)

    evalscript = """
    //VERSION=3
    function setup() {
      return {
        input: ["AER_AI_340_380"],
        output: { bands: 1, sampleType: "FLOAT32" }
      };
    }
    function evaluatePixel(sample) {
      return [sample.AER_AI_340_380];
    }
    """

    request = SentinelHubRequest(
        evalscript=evalscript,
        input_data=[SentinelHubRequest.input_data(
            data_collection=s5p_cdse, time_interval=time_interval,
        )],
        responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
        bbox=bbox, size=size, config=config,
    )

    data = request.get_data()
    array = data[0]

    result = {
        "region_name": REGION_NAME,
        "bbox": BBOX_COORDS,
        "time_interval": time_interval,
        "refreshed_at": datetime.utcnow().isoformat() + "Z",
        "grid_shape": list(array.shape),
        "mean_aerosol_index": float(np.mean(array)),
        "min_aerosol_index": float(np.min(array)),
        "max_aerosol_index": float(np.max(array)),
    }

    with open("data/live_satellite_sample.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"Satellite refreshed: mean AER_AI = {result['mean_aerosol_index']:.4f} "
          f"(window {time_interval[0]} to {time_interval[1]})")
    return result


# ---------------------------------------------------------------------------
# 2 & 3. OpenAQ refresh + full SQLite rebuild
# ---------------------------------------------------------------------------

CANDIDATE_CENTERS = [
    {"name": "Patiala area", "lat": 30.5, "lon": 76.5},
    {"name": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    {"name": "Ludhiana", "lat": 30.9010, "lon": 75.8573},
    {"name": "Karnal", "lat": 29.6857, "lon": 76.9905},
]


def refresh_ground_stations_and_db():
    print("\n=== Refreshing OpenAQ ground-station data ===")

    full_data = {"region": "Punjab-Haryana Belt", "centers": []}

    for center in CANDIDATE_CENTERS:
        LAT, LON, NAME = center["lat"], center["lon"], center["name"]
        print(f"Checking near {NAME} ({LAT}, {LON})...")

        stations = get_stations(LAT, LON, radius=25000)
        station_list = stations.get("results", [])
        print(f"  Found {len(station_list)} stations")

        center_entry = {"name": NAME, "lat": LAT, "lon": LON, "stations": []}

        for station in station_list:
            loc_id = station.get("id")
            name = station.get("name", "unknown")
            sensors = get_station_sensors(loc_id)
            sensor_list = sensors.get("results", [])

            station_entry = {"id": loc_id, "name": name, "sensors": []}
            for sensor in sensor_list:
                sensor_id = sensor.get("id")
                parameter = sensor.get("parameter", {}).get("name", "unknown")
                measurements = get_sensor_measurements(sensor_id, limit=500)
                readings = measurements.get("results", [])
                station_entry["sensors"].append({
                    "sensor_id": sensor_id, "parameter": parameter, "readings": readings
                })

            center_entry["stations"].append(station_entry)

        full_data["centers"].append(center_entry)

    with open("data/weather_aqi_history.json", "w") as f:
        json.dump(full_data, f, indent=2)

    total_stations = sum(len(c["stations"]) for c in full_data["centers"])
    print(f"Pulled {total_stations} stations total.")

    # --- Rebuild SQLite from scratch so refreshes don't accumulate duplicates ---
    print("\n=== Rebuilding SQLite database ===")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

    count = 0
    for center in full_data["centers"]:
        for station in center["stations"]:
            station_name = station.get("name", "unknown")
            for sensor in station.get("sensors", []):
                parameter = sensor.get("parameter", "unknown")
                for reading in sensor.get("readings", []):
                    value = reading.get("value")
                    period = reading.get("period", {})
                    timestamp = period.get("datetimeFrom", {}).get("utc", "unknown")
                    if value is not None:
                        save_reading(station_name, timestamp, parameter, value, "weather_api")
                        count += 1

    print(f"Rebuilt database with {count} fresh readings.")
    return count


if __name__ == "__main__":
    print(f"Live data refresh started at {datetime.utcnow().isoformat()}Z\n")
    refresh_satellite()
    refresh_ground_stations_and_db()
    print("\nRefresh complete.")
