from ultralytics import YOLO
import cv2

model = YOLO("detection/models/yolov8n.pt")
cap = cv2.VideoCapture("data/cam_01.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    results = model(frame, classes=[2, 3, 5, 7])  # car, motorcycle, bus, truck
    annotated = results[0].plot()
    cv2.imshow("Detection Test", annotated)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()