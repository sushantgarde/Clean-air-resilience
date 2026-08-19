from sentinelhub import (
    SentinelHubRequest,
    DataCollection,
    MimeType,
    BBox,
    CRS,
    bbox_to_dimensions,
)
from src.pipeline.sh_config import config

# CDSE requires Sentinel-5P to be explicitly bound to the CDSE service URL —
# the default DataCollection.SENTINEL5P points at the old sinergise endpoint,
# which returns an HTML error page instead of a TIFF for CDSE credentials.
s5p_cdse = DataCollection.SENTINEL5P.define_from(
    "s5p_cdse", service_url="https://sh.dataspace.copernicus.eu"
)

# Bounding box — swap for your target city (this example: Pune)
bbox = BBox(bbox=[73.74, 18.45, 73.95, 18.62], crs=CRS.WGS84)
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
            time_interval=("2026-08-01", "2026-08-14"),
        )
    ],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=bbox,
    size=size,
    config=config,
)

data = request.get_data()
print("Shape:", data[0].shape)
print("Sample values:", data[0][:3, :3])