"""
Day 1 checkpoint script — pulls real Sentinel-5P aerosol index data for the
Punjab/Haryana belt (Indo-Gangetic Plain) during stubble-burning season,
and saves the result to data/day1_sentinel_sample.json.

Region: Punjab/Haryana belt, India
Date range: 2025-10-15 to 2025-11-15 (stubble-burning season — reliable,
well-documented pollution signal)
"""

import json
import numpy as np
from sentinelhub import (
    SentinelHubRequest,
    DataCollection,
    MimeType,
    BBox,
    CRS,
    bbox_to_dimensions,
)
from src.pipeline.sh_config import config

# CDSE requires Sentinel-5P bound explicitly to the CDSE service URL
s5p_cdse = DataCollection.SENTINEL5P.define_from(
    "s5p_cdse", service_url="https://sh.dataspace.copernicus.eu"
)

# Locked region: Punjab/Haryana belt
REGION_NAME = "Punjab-Haryana Belt (Indo-Gangetic Plain)"
BBOX_COORDS = [75.5, 29.5, 77.5, 31.5]  # [min_lon, min_lat, max_lon, max_lat]
TIME_INTERVAL = ("2025-10-15", "2025-11-15")  # stubble-burning season

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
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=s5p_cdse,
            time_interval=TIME_INTERVAL,
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

data = request.get_data()
array = data[0]

result = {
    "region_name": REGION_NAME,
    "bbox": BBOX_COORDS,
    "time_interval": TIME_INTERVAL,
    "grid_shape": list(array.shape),
    "mean_aerosol_index": float(np.mean(array)),
    "min_aerosol_index": float(np.min(array)),
    "max_aerosol_index": float(np.max(array)),
    # NOTE: raw pixel grid intentionally omitted — it can be multiple MB
    # for this region/resolution and isn't needed beyond summary stats.
    # Rerun this script if the full array is needed for analysis.
}

with open("data/day1_sentinel_sample.json", "w") as f:
    json.dump(result, f, indent=2)

print(f"Region: {REGION_NAME}")
print(f"Grid shape: {array.shape}")
print(f"Mean AER_AI: {result['mean_aerosol_index']:.4f}")
print(f"Min / Max: {result['min_aerosol_index']:.4f} / {result['max_aerosol_index']:.4f}")
print("Saved to data/day1_sentinel_sample.json")