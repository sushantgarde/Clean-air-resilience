import json
import sys
from src.pipeline.db_client import init_db, save_reading

print("Initializing database...")
init_db()
print("Database ready: data/air_quality.db\n")

with open("data/weather_aqi_history.json", "r") as f:
    data = json.load(f)

count = 0
for center in data.get("centers", []):
    center_name = center.get("name", "unknown center")
    print(f"Region: {center_name}")

    for station in center.get("stations", []):
        station_name = station.get("name", "unknown")
        sys.stdout.write(f"  Inserting station: {station_name} ")
        sys.stdout.flush()

        station_count = 0
        for sensor in station.get("sensors", []):
            parameter = sensor.get("parameter", "unknown")
            for reading in sensor.get("readings", []):
                # OpenAQ measurement objects typically have 'value' and 'period.datetimeFrom.utc'
                value = reading.get("value")
                period = reading.get("period", {})
                timestamp = period.get("datetimeFrom", {}).get("utc", "unknown")

                if value is not None:
                    save_reading(
                        region=station_name,
                        timestamp=timestamp,
                        parameter=parameter,
                        value=value,
                        source="weather_api"
                    )
                    count += 1
                    station_count += 1

                    # Live progress dots so the terminal isn't silent during
                    # bulk inserts — useful for demo recordings.
                    if station_count % 25 == 0:
                        sys.stdout.write(".")
                        sys.stdout.flush()

        print(f" done ({station_count} readings)")

print(f"\nInsert complete. Loaded {count} total readings into data/air_quality.db")