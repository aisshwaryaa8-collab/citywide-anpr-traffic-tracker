import os
import cv2
import easyocr
import xml.etree.ElementTree as ET

reader = easyocr.Reader(['en'])

image_folder = "data/plate_dataset/images"
annotation_folder = "data/plate_dataset/annotations"

xml_files = [f for f in os.listdir(annotation_folder) if f.endswith(".xml")]
print(f"Found {len(xml_files)} annotation files. Testing OCR on the first 10...")

for xml_file in xml_files[:10]:
    tree = ET.parse(os.path.join(annotation_folder, xml_file))
    root = tree.getroot()

    filename = root.find("filename").text
    image_path = os.path.join(image_folder, filename)
    image = cv2.imread(image_path)

    if image is None:
        print(f"{filename}: could not load image, skipping")
        continue

    obj = root.find("object")
    if obj is None:
        print(f"{filename}: no annotation found")
        continue

    bbox = obj.find("bndbox")
    xmin = int(bbox.find("xmin").text)
    ymin = int(bbox.find("ymin").text)
    xmax = int(bbox.find("xmax").text)
    ymax = int(bbox.find("ymax").text)

    plate_crop = image[ymin:ymax, xmin:xmax]

    result = reader.readtext(plate_crop)
    if result:
        text = result[0][1].upper().replace(" ", "")
        conf = result[0][2]

        if conf < 0.5:
            print(f"{filename}: low-confidence read '{text}' ({conf:.2f}) — discarding")
            continue

        print(f"{filename}: OCR read '{text}' (confidence {conf:.2f})")
    else:
        print(f"{filename}: OCR found nothing readable")
