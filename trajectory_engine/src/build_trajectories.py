import argparse
import glob
import json
import os
# NOTE: sample_output/detections_demo_staged*.json are manually staged entries
# for demo purposes only — real cam_01/02/03 footage has 0% plate reads so far.
# See PR #5 discussion. Remove before using real multi-camera footage.
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from statistics import mean


def parse_ts(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def load_detections(input_dir):
    sightings = []
    pattern = os.path.join(input_dir, "detections_*.json")
    files = sorted(glob.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No detections_*.json files found in '{input_dir}'.")

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
                    "vehicle_type": v.get("vehicle_type", "unknown"),
                    "camera_id": camera_id,
                    "timestamp": ts,
                    "plate_confidence": v.get("plate_confidence", 0.0),
                })
    return sightings


def plates_similar(p1, p2, threshold=0.8):
    """Returns True if two plate strings are similar enough to be the same vehicle."""
    return SequenceMatcher(None, p1, p2).ratio() >= threshold


def build_trajectories(sightings):
    sightings.sort(key=lambda s: parse_ts(s["timestamp"]))

    clusters = []
    for s in sightings:
        matched_cluster = None
        for cluster in clusters:
            if plates_similar(cluster[-1]["plate_text"], s["plate_text"]):
                matched_cluster = cluster
                break
        if matched_cluster is not None:
            matched_cluster.append(s)
        else:
            clusters.append([s])

    trajectories = []
    for cluster in clusters:
        best = max(cluster, key=lambda s: s["plate_confidence"])
        canonical_plate = best["plate_text"]

        path = []
        for s in cluster:
            if path and path[-1]["camera_id"] == s["camera_id"]:
                continue
            path.append({"camera_id": s["camera_id"], "timestamp": s["timestamp"]})

        confidence = round(mean(s["plate_confidence"] for s in cluster), 4)

        trajectories.append({
            "vehicle": {"plate_text": canonical_plate, "vehicle_type": cluster[0]["vehicle_type"]},
            "path": path,
            "confidence": confidence,
        })
    return trajectories


def build_analytics(trajectories):
    travel_times = defaultdict(list)
    latest_camera_of = {}

    for traj in trajectories:
        path = traj["path"]
        plate = traj["vehicle"]["plate_text"]

        for i in range(len(path) - 1):
            t1 = parse_ts(path[i]["timestamp"])
            t2 = parse_ts(path[i + 1]["timestamp"])
            pair = (path[i]["camera_id"], path[i + 1]["camera_id"])
            travel_times[pair].append((t2 - t1).total_seconds())

        if path:
            last_ts = parse_ts(path[-1]["timestamp"])
            latest_camera_of[plate] = (path[-1]["camera_id"], last_ts)

    avg_travel_time_seconds = {
        f"{a}->{b}": round(mean(times), 1) for (a, b), times in travel_times.items()
    }

    vehicle_count_per_camera = defaultdict(int)
    for camera_id, _ts in latest_camera_of.values():
        vehicle_count_per_camera[camera_id] += 1

    return {
        "avg_travel_time_seconds": avg_travel_time_seconds,
        "vehicle_count_per_camera": dict(vehicle_count_per_camera),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="sample_output")
    parser.add_argument("--output_dir", default="sample_output")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    sightings = load_detections(args.input_dir)
    trajectories = build_trajectories(sightings)
    analytics = build_analytics(trajectories)

    with open(os.path.join(args.output_dir, "trajectories.json"), "w") as f:
        json.dump(trajectories, f, indent=2)

    with open(os.path.join(args.output_dir, "analytics.json"), "w") as f:
        json.dump(analytics, f, indent=2)

    print(f"Loaded {len(sightings)} sightings.")
    print(f"Built {len(trajectories)} trajectories.")


if __name__ == "__main__":
    main()