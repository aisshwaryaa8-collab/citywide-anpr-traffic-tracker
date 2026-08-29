from huggingface_hub import hf_hub_download
import shutil

downloaded_path = hf_hub_download(
    repo_id="morsetechlab/yolov11-license-plate-detection",
    filename="license-plate-finetune-v1n.pt"
)

print(f"Downloaded to: {downloaded_path}")
shutil.copy(downloaded_path, "detection/models/plate_detector.pt")
print("Copied to detection/models/plate_detector.pt")