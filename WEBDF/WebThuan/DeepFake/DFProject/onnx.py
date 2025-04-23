import torch

# Tải mô hình YOLOv5
model = torch.hub.load('ultralytics/yolo11x', 'yolo11x')  # Thay 'yolov5s' bằng phiên bản bạn cần

# Chuyển đổi mô hình sang định dạng ONNX
model.export(format='onnx')
