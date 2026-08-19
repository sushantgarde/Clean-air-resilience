from google import genai
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_alert(region, hotspot_score, forecast_trend):
    """Generates a plain-language pollution alert for a local authority
    using Gemini, based on the fused hotspot score and forecast direction.

    Args:
        region (str): Name of the affected region.
        hotspot_score (float): 0-1 fused risk score from hotspot_scoring.py.
        forecast_trend (str): Short description of the forecast direction,
            e.g. "declining", "rising", "stable".

    Returns:
        str: Generated alert text.
    """
    prompt = f"""
    Region: {region}
    Hotspot Score: {hotspot_score:.2f} (0-1 scale, higher = more urgent)
    Forecast Trend: {forecast_trend}

    Write a concise, plain-language alert for a local environmental authority,
    explaining the risk level, likely cause, and recommended immediate action.
    Keep it under 100 words.
    """
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt
    )
    return response.text


if __name__ == "__main__":
    alert = generate_alert(
        region="Punjab-Haryana Belt (Patiala, Chandigarh, Ludhiana, Karnal)",
        hotspot_score=0.428,
        forecast_trend="mildly declining over the next 3 days, but citizen reports indicate high visible haze"
    )
    print(alert)