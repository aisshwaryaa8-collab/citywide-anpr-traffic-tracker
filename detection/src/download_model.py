from ultralytics import YOLO

model = YOLO("yolov8n.pt")   # auto-downloads on first run
print("Model downloaded and loaded successfully.")