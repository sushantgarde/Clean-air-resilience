import os
import time
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

SAMPLE_DIR = "data/sample_images"
OUTPUT_PATH = "data/vision_test_results.json"
MODEL = "gemini-3.1-flash-lite"  # higher free-tier quota (15 RPM) than gemini-3.5-flash (5 RPM)
DELAY_BETWEEN_CALLS = 5  # seconds — safe spacing for 15 RPM

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
        model=MODEL,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            "Analyze this photo for visible air pollution/smog/haze. "
            "Rate severity (Low/Moderate/High/Severe) and briefly explain visual indicators."
        ]
    )
    return response.text

results = []
files = [f for f in sorted(os.listdir(SAMPLE_DIR)) if f.lower().endswith((".jpg", ".jpeg", ".png"))]

print(f"Found {len(files)} images to classify.\n")

for filename in files:
    path = os.path.join(SAMPLE_DIR, filename)
    print(f"Classifying: {filename}...")

    retries = 3
    for attempt in range(retries):
        try:
            classification = classify_air_quality(path)
            results.append({"filename": filename, "classification": classification})
            break
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait = 30
                print(f"  Rate limited, waiting {wait}s before retry ({attempt + 1}/{retries})...")
                time.sleep(wait)
            elif "503" in error_str or "UNAVAILABLE" in error_str:
                wait = 15
                print(f"  Model busy, waiting {wait}s before retry ({attempt + 1}/{retries})...")
                time.sleep(wait)
            else:
                print(f"  Failed on {filename}: {e}")
                break
    else:
        print(f"  Gave up on {filename} after {retries} attempts.")

    time.sleep(DELAY_BETWEEN_CALLS)

with open(OUTPUT_PATH, "w") as f:
    json.dump(results, f, indent=2)

print(f"\nDone. {len(results)} of {len(files)} images classified successfully.")
print(f"Saved to {OUTPUT_PATH}")