import cv2
import easyocr

reader = easyocr.Reader(['en'])

# change this to any crop image filename you see in the debug_crops_closeup folder
image_path = "debug_plate_boxes/plate_6.jpg"

image = cv2.imread(image_path)
print(f"Image shape: {image.shape}")

# Test 1: raw crop, no preprocessing
result_raw = reader.readtext(image)
print(f"Raw OCR result: {result_raw}")

# Test 2: with your preprocessing (grayscale + upscale)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
result_processed = reader.readtext(resized)
print(f"Preprocessed OCR result: {result_processed}")