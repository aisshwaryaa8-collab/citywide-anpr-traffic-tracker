"""
Person C — Backend API
-----------------------
Serves the JSON files produced by Person A (detections) and Person B
(trajectories) to the dashboard frontend.

HOW TO RUN:
    pip install -r requirements.txt
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000/docs to see (and test) all the endpoints
in your browser automatically -- FastAPI builds that page for you for free.

HOW TO SWITCH FROM SAMPLE DATA TO REAL DATA (at integration time):
    Just change TRAJECTORIES_FILE and CAMERAS_FILE below to point at the
    real files Person B produces (e.g. "../trajectory_engine/trajectories.json").
    Nothing else in this file needs to change -- that's the whole point of
    the contract everyone agreed on.
"""

from datetime import datetime
from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# ---------------------------------------------------------------------------
# 1. CONFIG -- change these two lines at integration time, nothing else
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent
TRAJECTORIES_FILE = BASE_DIR / "sample_data" / "trajectories_sample.json"
CAMERAS_FILE = BASE_DIR / "sample_data" / "camera_locations.json"

# ---------------------------------------------------------------------------
# 2. APP SETUP
# ---------------------------------------------------------------------------
app = FastAPI(title="City-Wide ANPR Traffic Analytics API")

# Allows the frontend (running on a different port/file) to call this API.
# For a hackathon prototype, allowing everything is fine.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_json(path: Path):
    """Read a JSON file fresh every time -- no database needed for a
    hackathon prototype. If the file is missing, fail with a clear message
    instead of a confusing crash."""
    if not path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Data file not found: {path}. Check TRAJECTORIES_FILE/CAMERAS_FILE in main.py.",
        )
    with open(path, "r") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# 3. ENDPOINTS
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "message": "ANPR Traffic Analytics API is running"}


@app.get("/trajectories")
def get_all_trajectories():
    """Every vehicle's full path across cameras."""
    return load_json(TRAJECTORIES_FILE)


@app.get("/trajectories/{plate}")
def get_trajectory_by_plate(plate: str):
    """One vehicle's path, looked up by plate number (case-insensitive)."""
    data = load_json(TRAJECTORIES_FILE)
    plate = plate.upper().replace(" ", "")
    for entry in data:
        if entry["vehicle"]["plate_text"] == plate:
            return entry
    raise HTTPException(status_code=404, detail=f"No trajectory found for plate '{plate}'")


@app.get("/cameras")
def get_camera_locations():
    """Static camera_id -> lat/lng map, used to draw markers on the map."""
    return load_json(CAMERAS_FILE)


@app.get("/analytics")
def get_analytics():
    """
    Aggregate stats for the dashboard's charts:
    - vehicle count seen per camera
    - average confidence per vehicle type
    Computed on the fly from trajectories.json so it always matches
    whatever data file is currently configured above.
    """
    data = load_json(TRAJECTORIES_FILE)

    camera_counts: dict[str, int] = {}
    type_confidences: dict[str, list[float]] = {}

    for entry in data:
        vtype = entry["vehicle"].get("vehicle_type", "unknown")
        type_confidences.setdefault(vtype, []).append(entry.get("confidence", 0))
        for stop in entry["path"]:
            cam = stop["camera_id"]
            camera_counts[cam] = camera_counts.get(cam, 0) + 1

    avg_confidence_by_type = {
        vtype: round(sum(vals) / len(vals), 2) for vtype, vals in type_confidences.items()
    }

    return {
        "vehicle_count_per_camera": camera_counts,
        "total_vehicles_tracked": len(data),
        "avg_confidence_by_type": avg_confidence_by_type,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
