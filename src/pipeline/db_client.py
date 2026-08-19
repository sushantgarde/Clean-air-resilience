import sqlite3

DB_PATH = "data/air_quality.db"

def init_db():
    """Creates the air_quality_readings table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS air_quality_readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            region TEXT,
            timestamp TEXT,
            parameter TEXT,
            value REAL,
            source TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_reading(region, timestamp, parameter, value, source):
    """Saves a single air quality reading to SQLite.

    Args:
        region (str): Region or station name.
        timestamp (str): ISO timestamp of the reading.
        parameter (str): Pollutant/measurement type (e.g. "pm25", "no2").
        value (float): The measured value.
        source (str): "satellite" / "citizen_photo" / "weather_api".
    """
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO air_quality_readings (region, timestamp, parameter, value, source) VALUES (?, ?, ?, ?, ?)",
        (region, timestamp, parameter, value, source)
    )
    conn.commit()
    conn.close()

def get_readings(region=None, parameter=None):
    """Retrieves stored readings, optionally filtered by region and/or parameter.

    Args:
        region (str, optional): Filter to a specific region/station name.
        parameter (str, optional): Filter to a specific pollutant parameter.

    Returns:
        list[tuple]: Matching rows from air_quality_readings.
    """
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM air_quality_readings WHERE 1=1"
    params = []
    if region:
        query += " AND region = ?"
        params.append(region)
    if parameter:
        query += " AND parameter = ?"
        params.append(parameter)
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return rows