import argparse
import glob
import json
import os
from datetime import datetime
from difflib import SequenceMatcher


def parse_ts(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def load_detections(input_dir):
    sightings = []
    pattern = os.path.join(input_dir, "detections_*.json")
    files = sorted(glob.glob(pattern))
    for filepath in files:
        with open(filepath, "r") as f:
            data = json.load(f)
        camera_id = data["camera_id"]
        for frame in data.get("frames", []):
            ts = frame["timestamp"]
            for v in frame.get("vehicles", []):
                plate = v.get("plate_text")
                if not plate:
                    continue
                plate = plate.strip().upper().replace(" ", "")
                sightings.append({
                    "plate_text": plate,
                    "camera_id": camera_id,
                    "timestamp": ts,
                    "plate_confidence": v.get("plate_confidence", 0.0),
                })
    return sightings


def cluster(sightings, threshold):
    sightings = sorted(sightings, key=lambda s: parse_ts(s["timestamp"]))
    clusters = []
    for s in sightings:
        matched = None
        for c in clusters:
            ratio = SequenceMatcher(None, c[-1]["plate_text"], s["plate_text"]).ratio()
            if ratio >= threshold:
                matched = c
                break
        if matched is not None:
            matched.append(s)
        else:
            clusters.append([s])
    return clusters


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="detection/sample_output")
    parser.add_argument("--threshold", type=float, default=0.75)
    args = parser.parse_args()

    sightings = load_detections(args.input_dir)
    clusters = cluster(sightings, args.threshold)

    print(f"\n=== threshold={args.threshold} ===")
    print(f"{len(sightings)} sightings -> {len(clusters)} clusters\n")

    for i, c in enumerate(clusters):
        if len(c) < 2:
            continue  # only show clusters where a merge actually happened
        members = [s["plate_text"] for s in c]
        first, last = c[0]["plate_text"], c[-1]["plate_text"]
        drift = SequenceMatcher(None, first, last).ratio()
        flag = "  <-- FIRST/LAST BELOW THRESHOLD (chaining!)" if drift < args.threshold else ""
        print(f"Cluster {i+1}: {members}")
        print(f"   first='{first}' last='{last}' direct_similarity={drift:.3f}{flag}\n")


if __name__ == "__main__":
    main()