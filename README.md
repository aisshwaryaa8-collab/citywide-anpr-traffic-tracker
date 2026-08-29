# SIH26127 — City-Wide AI Engine for Multi-Camera ANPR Trajectory Tracking & Urban Traffic Analytics

An end-to-end, AI-powered intelligent traffic management system designed to track vehicle trajectories across multiple simulated camera feeds using Automatic Number-Plate Recognition (ANPR) and provide real-time urban traffic analytics on a live web dashboard
---

## 📂 Repository Structure

```text
sih26127/
├── detection/                    
│   ├── src/                        # Inference & OCR script files
│   ├── models/                     # Weights directory
│   ├── sample_output/              # Mock detections_sample.json
│   └── requirements.txt
├── trajectory_engine/              
│   ├── src/                        # Trajectory-stitching algorithms
│   ├── sample_output/              # Mock trajectories_sample.json
│   └── requirements.txt
├── backend_frontend/              
│   ├── backend/                    # FastAPI web server
│   ├── frontend/                   # UI Application (HTML/Leaflet Map)
│   └── requirements.txt
├── shared/
│   └── schema/                     # Central Integration Contracts (Do not edit alone!)
│       ├── camera_locations.json   # Static Lat/Long mapping for cameras
│       ├── detections.json         
│       └── trajectories.json       
├── data/
│   └── sample_videos/              # Small test video clips
├── docs/                           # Presentation slides & system documentation
└── README.md
```

---

## 🤝 Interface Contracts

The system uses standardized internal JSON schemas to enable independent parallel development.

### 📡 1. Detection Contract (`detections.json`)
Produced by Stage 1 and consumed by Stage 2. Plate text is strictly normalized (uppercase, spaces stripped).
```json
{
  "camera_id": "cam_01",
  "frames": [
    {
      "timestamp": "2026-09-01T10:15:32Z",
      "frame_no": 452,
      "vehicles": [
        {
          "track_id": 17,
          "bbox":,
          "plate_text": "TN22AB1234",
          "plate_confidence": 0.91,
          "vehicle_type": "car"
        }
      ]
    }
  ]
}
```

### 🗺️ 2. Trajectory Contract (`trajectories.json`)
Produced by Stage 2 and consumed by Stage 3. The path array is sorted chronologically.
```json
{
  "vehicle": {
    "plate_text": "TN22AB1234",
    "vehicle_type": "car"
  },
  "path": [
    { "camera_id": "cam_01", "timestamp": "2026-09-01T10:15:32Z" },
    { "camera_id": "cam_03", "timestamp": "2026-09-01T10:19:07Z" },
    { "camera_id": "cam_02", "timestamp": "2026-09-01T10:24:51Z" }
  ],
  "confidence": 0.87
}
```

