def calculate_hotspot_score(satellite_aerosol, citizen_severity_score, forecasted_aqi):
    """Fuses satellite, citizen-photo, and forecasted AQI signals into a
    single 0-1 hotspot risk score.

    Args:
        satellite_aerosol (float): Sentinel-5P aerosol index value, expected
            roughly in a -2 to 2 range; normalized internally to 0-1.
        citizen_severity_score (float): 1-4 scale (Low=1, Moderate=2,
            High=3, Severe=4) from Gemini Vision classification.
        forecasted_aqi (float): Forecasted PM2.5 (or AQI) value, normalized
            against a 500 max (India's AQI severe threshold ceiling).

    Returns:
        float: Hotspot score between 0 and 1, higher = more urgent.
    """
    weights = {"satellite": 0.4, "citizen": 0.3, "forecast": 0.3}

    # Normalize aerosol index (-2 to 2 typical range) to 0-1
    normalized_satellite = (satellite_aerosol + 2) / 4
    normalized_satellite = max(0, min(1, normalized_satellite))

    normalized_citizen = citizen_severity_score / 4
    normalized_forecast = min(forecasted_aqi / 500, 1)

    score = (
        weights["satellite"] * normalized_satellite +
        weights["citizen"] * normalized_citizen +
        weights["forecast"] * normalized_forecast
    )
    return round(score, 3)


if __name__ == "__main__":
    # Example using your real Day 1 satellite mean + a "High" citizen rating
    # + your Phase 3 forecast
    example_score = calculate_hotspot_score(
        satellite_aerosol=-0.18,   # from data/day1_sentinel_sample.json mean
        citizen_severity_score=3,  # High
        forecasted_aqi=34.5        # from forecasting.py
    )
    print(f"Example hotspot score: {example_score}")