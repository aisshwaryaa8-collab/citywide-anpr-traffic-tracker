import json

files = [
    "detection/sample_output/detections_cam01.json",
    "detection/sample_output/detections_cam02.json",
    "detection/sample_output/detections_cam03.json",
    "detection/sample_output/detections_closeup.json",
]

for filepath in files:
    with open(filepath) as f:
        data = json.load(f)

    total_vehicles = 0
    plates_found = 0
    plate_list = []

    for frame in data["frames"]:
        for v in frame["vehicles"]:
            total_vehicles += 1
            if v["plate_text"]:
                plates_found += 1
                plate_list.append((v["plate_text"], round(v["plate_confidence"], 2)))

    print(f"\n=== {filepath} ===")
    print(f"Total vehicle entries: {total_vehicles}")
    print(f"Plates found: {plates_found}")
    print("Sample reads:")
    for text, conf in plate_list[:20]:
        print(f"  '{text}' (confidence {conf})")