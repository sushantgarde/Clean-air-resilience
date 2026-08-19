import json

with open("data/weather_aqi_history.json", "r") as f:
    data = json.load(f)

summary = {"region": data.get("region"), "centers": []}

for center in data.get("centers", []):
    center_summary = {"name": center.get("name"), "stations": []}

    for station in center.get("stations", []):
        station_summary = {"id": station.get("id"), "name": station.get("name"), "sensors": []}

        for sensor in station.get("sensors", []):
            readings = sensor.get("readings", [])
            sample = readings[:3]  # keep a few real sample readings as evidence

            station_summary["sensors"].append({
                "parameter": sensor.get("parameter"),
                "reading_count": len(readings),
                "sample_readings": sample
            })

        center_summary["stations"].append(station_summary)

    summary["centers"].append(center_summary)

with open("data/weather_aqi_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("Created data/weather_aqi_summary.json — a small evidence file with real sample readings and counts.")
print("The full data/weather_aqi_history.json stays local only (regenerable via weather_client.py).")