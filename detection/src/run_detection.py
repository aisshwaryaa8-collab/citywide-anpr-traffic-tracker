import cv2
import json
import os
import easyocr
from datetime import datetime, timedelta
from ultralytics import YOLO

# ---------- Setup ----------
vehicle_model = YOLO("detection/models/yolov8n.pt")
plate_model = YOLO("detection/models/plate_detector.pt")
reader = easyocr.Reader(['en'])

CONFIDENCE_THRESHOLD = 0.3
VEHICLE_CLASSES = [2, 3, 5, 7]
OCR_EVERY_N_FRAMES = 10


def preprocess_plate(plate_crop):
    gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    return resized


def read_plate(frame, bbox):
    """Use the dedicated plate detector to find the plate within the vehicle box, then OCR it."""
    x1, y1, x2, y2 = map(int, bbox)
    vehicle_crop = frame[y1:y2, x1:x2]

    if vehicle_crop.size == 0:
        return None, 0.0

    plate_results = plate_model.predict(vehicle_crop, conf=0.25, verbose=False)
    plate_boxes = plate_results[0].boxes

    if plate_boxes is None or len(plate_boxes) == 0:
        return None, 0.0

    # take the first/most confident plate box found within this vehicle
    px1, py1, px2, py2 = map(int, plate_boxes.xyxy[0].tolist())
    plate_region = vehicle_crop[py1:py2, px1:px2]

    if plate_region.size == 0:
        return None, 0.0

    processed = preprocess_plate(plate_region)
    result = reader.readtext(processed)

    if not result:
        return None, 0.0

    text = result[0][1].upper().replace(" ", "")
    conf = result[0][2]
    return text, conf


def process_video(video_path, camera_id, output_path):
    print(f"\nProcessing {video_path} as {camera_id}...")

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = 25

    frame_no = 0
    frames_data = []
    start_time = datetime.utcnow()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        results = vehicle_model.track(frame, persist=True, classes=VEHICLE_CLASSES, verbose=False)

        vehicles = []
        if results[0].boxes.id is not None:
            for box, tid in zip(results[0].boxes.xyxy, results[0].boxes.id):
                bbox = box.tolist()

                plate_text, conf = None, 0.0
                if frame_no % OCR_EVERY_N_FRAMES == 0:
                    plate_text, conf = read_plate(frame, bbox)
                    if not (plate_text and conf >= CONFIDENCE_THRESHOLD):
                        plate_text, conf = None, 0.0

                vehicles.append({
                    "track_id": int(tid),
                    "bbox": bbox,
                    "plate_text": plate_text,
                    "plate_confidence": float(conf),
                    "vehicle_type": "car"
                })

        if vehicles:
            timestamp = (start_time + timedelta(seconds=frame_no / fps)).isoformat() + "Z"
            frames_data.append({
                "timestamp": timestamp,
                "frame_no": frame_no,
                "vehicles": vehicles
            })
            print(f"  Frame {frame_no}: {len(vehicles)} vehicle(s), plates found: {sum(1 for v in vehicles if v['plate_text'])}")

        frame_no += 1

    cap.release()

    output = {"camera_id": camera_id, "frames": frames_data}
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"Done. Saved {len(frames_data)} frames with detections to {output_path}")


if __name__ == "__main__":
    cameras = [
        ("data/cam_01.mp4", "cam_01", "detection/sample_output/detections_cam01.json"),
        ("data/cam_02.mp4", "cam_02", "detection/sample_output/detections_cam02.json"),
        ("data/cam_03.mp4", "cam_03", "detection/sample_output/detections_cam03.json"),
        ("data/cam_closeup.mp4", "cam_closeup", "detection/sample_output/detections_closeup.json"),
    ]

    for video_path, camera_id, output_path in cameras:
        process_video(video_path, camera_id, output_path)

    print("\nAll cameras processed.")