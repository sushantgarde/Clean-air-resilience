from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def classify_air_quality(image_path):
    """Classifies visible air pollution severity in a photo using Gemini Vision.

    Args:
        image_path (str): Path to the citizen-submitted photo.

    Returns:
        str: Severity rating (Low/Moderate/High/Severe) with brief reasoning.
    """
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            "Analyze this photo for visible air pollution/smog/haze. "
            "Rate severity (Low/Moderate/High/Severe) and briefly explain visual indicators."
        ]
    )
    return response.text