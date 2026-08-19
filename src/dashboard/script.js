// Relative path — works locally (Flask serves both dashboard and API on the
// same port now) and once deployed (same-origin, no hardcoded localhost URL).
const API_BASE = "/api/hotspots";

// Station coordinates per region — Region A from Phase 2's real OpenAQ pull;
// Region B (Delhi-NCR) uses illustrative station points for the federated mock.
const REGION_STATIONS = {
  "punjab-haryana": [
    { name: "Model Town, Patiala", lat: 30.34, lon: 76.38 },
    { name: "RIMT University, Mandi Gobindgarh", lat: 30.67, lon: 76.29 },
    { name: "Sector-6, Panchkula", lat: 30.69, lon: 76.85 },
    { name: "Sector-25, Chandigarh", lat: 30.72, lon: 76.78 },
    { name: "Sector 22, Chandigarh", lat: 30.73, lon: 76.78 },
    { name: "Sector-53, Chandigarh", lat: 30.70, lon: 76.82 },
    { name: "Punjab Agricultural University, Ludhiana", lat: 30.90, lon: 75.81 },
    { name: "Sector-12, Karnal", lat: 29.69, lon: 76.99 },
  ],
  "delhi-ncr": [
    { name: "Anand Vihar, Delhi", lat: 28.6469, lon: 77.3157 },
    { name: "RK Puram, Delhi", lat: 28.5638, lon: 77.1855 },
    { name: "Sector 62, Noida", lat: 28.6280, lon: 77.3649 },
    { name: "Sector 51, Gurugram", lat: 28.4322, lon: 77.0700 },
  ],
};

const REGION_CENTERS = {
  "punjab-haryana": { center: [30.5, 76.5], zoom: 8, label: "Punjab-Haryana Belt — Stubble-Burning Season" },
  "delhi-ncr": { center: [28.6, 77.2], zoom: 9, label: "Delhi-NCR — Federated Region B (Demo)" },
};

let currentRegion = "punjab-haryana";
let currentMarkers = [];

const map = L.map("map", { zoomControl: true }).setView(REGION_CENTERS[currentRegion].center, REGION_CENTERS[currentRegion].zoom);

L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
  attribution: "&copy; OpenStreetMap &copy; CARTO",
}).addTo(map);

function scoreColor(score) {
  if (score < 0.3) return "#48bb78";
  if (score < 0.6) return "#ecc94b";
  return "#f56565";
}

function clearStations() {
  currentMarkers.forEach((m) => map.removeLayer(m));
  currentMarkers = [];
}

function renderStations(score) {
  clearStations();
  const color = scoreColor(score);
  REGION_STATIONS[currentRegion].forEach((s) => {
    const marker = L.circleMarker([s.lat, s.lon], {
      radius: 8,
      color: color,
      fillColor: color,
      fillOpacity: 0.6,
      weight: 2,
    })
      .addTo(map)
      .bindPopup(`<strong>${s.name}</strong><br>Hotspot score: ${score}`);
    currentMarkers.push(marker);
  });
}

async function loadHotspotData(regionKey) {
  currentRegion = regionKey;

  const regionInfo = REGION_CENTERS[regionKey];
  map.setView(regionInfo.center, regionInfo.zoom);
  document.getElementById("region-label").textContent = regionInfo.label;

  document.getElementById("trend-value").textContent = "Loading...";
  document.getElementById("alert-text").textContent = "Loading alert...";

  try {
    const resp = await fetch(`${API_BASE}/${regionKey}`);
    const data = await resp.json();

    document.getElementById("score-value").textContent = data.hotspot_score;
    document.getElementById("trend-value").textContent =
      `Trend: ${data.trend}`;

    const forecastList = data.forecast_pm25_next_3_days
      .map((v, i) => `Day ${i + 1}: ${v.toFixed(1)} µg/m³`)
      .join("<br>");
    document.getElementById("forecast-values").innerHTML = forecastList;

    document.getElementById("alert-text").textContent = data.alert;

    renderStations(data.hotspot_score);
  } catch (err) {
    document.getElementById("trend-value").textContent = "Error loading data";
    document.getElementById("alert-text").textContent =
      "Could not reach the API. Is app.py running on port 8080?";
    console.error(err);
  }
}

document.querySelectorAll(".region-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".region-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    loadHotspotData(btn.dataset.region);
  });
});

document.getElementById("refresh-btn").addEventListener("click", () => loadHotspotData(currentRegion));

loadHotspotData(currentRegion);