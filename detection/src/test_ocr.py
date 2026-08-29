from ultralytics import YOLO
import cv2
import easyocr

model = YOLO("detection/models/yolov8n.pt")
reader = easyocr.Reader(['en'])
cap = cv2.VideoCapture("data/cam_01.mp4")

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    # only run OCR every 10 frames to keep it fast — OCR is slow, no need to run every single frame
    if frame_count % 10 != 0:
        continue

    results = model.track(frame, persist=True, classes=[2, 3, 5, 7], verbose=False)

    if results[0].boxes.id is not None:
        for box, tid in zip(results[0].boxes.xyxy, results[0].boxes.id):
            x1, y1, x2, y2 = map(int, box.tolist())
            h = y2 - y1
            # crop bottom third of the vehicle box, where plates usually are
            plate_region = frame[y1 + int(h*0.6):y2, x1:x2]

            if plate_region.size == 0:
                continue

            ocr_result = reader.readtext(plate_region)
            if ocr_result:
                text = ocr_result[0][1].upper().replace(" ", "")
                conf = ocr_result[0][2]
                print(f"Track ID {int(tid)}: '{text}' (confidence {conf:.2f})")

cap.release()
print("Done.")