from ultralytics import YOLO
import cv2
import os

model = YOLO("detection/models/plate_detector.pt")

cap = cv2.VideoCapture("data/cam_closeup.mp4")
os.makedirs("debug_plate_boxes", exist_ok=True)

frame_count = 0
saved = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    if frame_count % 10 != 0:
        continue

    results = model.predict(frame, conf=0.25, verbose=False)
    boxes = results[0].boxes

    if boxes is not None and len(boxes) > 0:
        for box in boxes.xyxy:
            x1, y1, x2, y2 = map(int, box.tolist())
            plate_crop = frame[y1:y2, x1:x2]
            if plate_crop.size > 0 and saved < 15:
                cv2.imwrite(f"debug_plate_boxes/plate_{saved}.jpg", plate_crop)
                saved += 1
                print(f"Frame {frame_count}: found plate box, saved crop {saved}")
    else:
        print(f"Frame {frame_count}: no plate detected")

cap.release()
print(f"Done. Saved {saved} plate crops.")