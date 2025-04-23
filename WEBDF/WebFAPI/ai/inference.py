from ultralytics import YOLO
import torch
import cv2
import numpy as np

# Load model
model = YOLO("/media/sinemu/Lexar/WEBDF/WebFAPI/models/yolo11n.pt")  # đổi path nếu khác
print(f"Model is running on: {model.device}")
# Hàm xử lý 1 frame
def process_frame(frame):
    # BGR → RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Inference
    results = model(rgb_frame)

    # Lấy kết quả (vẽ bounding boxes lên ảnh gốc)
    annotated_frame = results[0].plot()

    return annotated_frame
