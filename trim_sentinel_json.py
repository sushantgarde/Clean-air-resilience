import json

with open("data/day1_sentinel_sample.json", "r") as f:
    data = json.load(f)

# Drop the full raw pixel grid — it's regenerable by rerunning day1_checkpoint.py,
# and isn't needed in the repo. Keep only summary stats and metadata.
data.pop("raw_values", None)

with open("data/day1_sentinel_sample.json", "w") as f:
    json.dump(data, f, indent=2)

print("Trimmed. File now contains only summary stats and metadata.")