import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.openaq.org/v3"

def get_stations(lat, lon, radius=50000, limit=100):
    """Fetches nearby air quality monitoring stations from OpenAQ.

    Args:
        lat (float): Latitude of the target region center.
        lon (float): Longitude of the target region center.
        radius (int): Search radius in meters.
        limit (int): Max number of station results.

    Returns:
        dict: Raw OpenAQ API response listing stations.
    """
    headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}
    params = {"coordinates": f"{lat},{lon}", "radius": radius, "limit": limit}
    resp = requests.get(f"{BASE_URL}/locations", params=params, headers=headers)

    if resp.status_code != 200:
        print(f"  [ERROR] Status {resp.status_code}: {resp.text[:300]}")
        return {"results": []}

    data = resp.json()
    if not isinstance(data, dict):
        print(f"  [ERROR] Unexpected response type: {type(data)} — {str(data)[:300]}")
        return {"results": []}

    return data

def get_station_sensors(location_id):
    """Fetches the list of sensors (pollutant parameters) available at a station.

    Args:
        location_id (int): OpenAQ location ID.

    Returns:
        dict: Raw OpenAQ API response listing sensors for the station.
    """
    headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}
    resp = requests.get(f"{BASE_URL}/locations/{location_id}/sensors", headers=headers)

    if resp.status_code != 200:
        print(f"    [ERROR] Status {resp.status_code}: {resp.text[:300]}")
        return {"results": []}

    data = resp.json()
    if not isinstance(data, dict):
        print(f"    [ERROR] Unexpected response type: {type(data)} — {str(data)[:300]}")
        return {"results": []}

    return data

def get_sensor_measurements(sensor_id, limit=100):
    """Fetches recent measurement readings for a specific sensor.

    Args:
        sensor_id (int): OpenAQ sensor ID.
        limit (int): Max number of readings to fetch.

    Returns:
        dict: Raw OpenAQ API response with measurement values and timestamps.
    """
    headers = {"X-API-Key": os.getenv("OPENAQ_API_KEY")}
    params = {"limit": limit}
    resp = requests.get(f"{BASE_URL}/sensors/{sensor_id}/measurements", params=params, headers=headers)

    if resp.status_code != 200:
        print(f"      [ERROR] Status {resp.status_code}: {resp.text[:300]}")
        return {"results": []}

    data = resp.json()
    if not isinstance(data, dict):
        print(f"      [ERROR] Unexpected response type: {type(data)} — {str(data)[:300]}")
        return {"results": []}

    return data

if __name__ == "__main__":
    # Punjab/Haryana belt — try a few candidate centers since station density is uneven.
    # OpenAQ caps radius at 25000m, so we widen coverage by checking multiple points
    # across the region instead of one large radius.
    CANDIDATE_CENTERS = [
        {"name": "Patiala area", "lat": 30.5, "lon": 76.5},
        {"name": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
        {"name": "Ludhiana", "lat": 30.9010, "lon": 75.8573},
        {"name": "Karnal", "lat": 29.6857, "lon": 76.9905},
    ]

    full_data = {"region": "Punjab-Haryana Belt", "centers": []}

    for center in CANDIDATE_CENTERS:
        LAT, LON, NAME = center["lat"], center["lon"], center["name"]
        print(f"\nChecking near {NAME} ({LAT}, {LON})...")

        stations = get_stations(LAT, LON, radius=25000)
        station_list = stations.get("results", [])
        print(f"  Found {len(station_list)} monitoring stations")

        center_entry = {"name": NAME, "lat": LAT, "lon": LON, "stations": []}

        for station in station_list:
            loc_id = station.get("id")
            name = station.get("name", "unknown")
            print(f"  Fetching sensors for station: {name} (id={loc_id})")

            sensors = get_station_sensors(loc_id)
            sensor_list = sensors.get("results", [])

            station_entry = {"id": loc_id, "name": name, "sensors": []}

            for sensor in sensor_list:
                sensor_id = sensor.get("id")
                parameter = sensor.get("parameter", {}).get("name", "unknown")
                print(f"    Fetching measurements for parameter: {parameter} (sensor_id={sensor_id})")

                measurements = get_sensor_measurements(sensor_id, limit=500)
                readings = measurements.get("results", [])

                station_entry["sensors"].append({
                    "sensor_id": sensor_id,
                    "parameter": parameter,
                    "readings": readings
                })

            center_entry["stations"].append(station_entry)

        full_data["centers"].append(center_entry)

    with open("data/weather_aqi_history.json", "w") as f:
        json.dump(full_data, f, indent=2)

    total_stations = sum(len(c["stations"]) for c in full_data["centers"])
    print(f"\nSaved {total_stations} total stations across {len(CANDIDATE_CENTERS)} centers to data/weather_aqi_history.json")