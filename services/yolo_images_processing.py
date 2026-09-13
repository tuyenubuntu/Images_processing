import time
import cv2
import torch
from ultralytics import YOLO

class YoloProcessor:
    def __init__(self, model_path="models/yolo11m.pt", conf=0.4, imgsz=640):
        # 1. Chọn GPU nếu khả dụng
        self.device = 0 if torch.cuda.is_available() else "cpu"
        self.device_name = "GPU" if self.device == 0 else "CPU"
        
        # 2. Tải model YOLO
        self.model = YOLO(model_path)
        self.conf = conf
        self.imgsz = imgsz
        self.prev_time = time.time()

    def process_frame(self, frame):
        """
        Nhận frame BGR gốc, chạy dự đoán và trả về (annotated_frame, detections)
        """
        # Dự đoán
        results = self.model.predict(
            source=frame,
            device=self.device,
            conf=self.conf,
            imgsz=self.imgsz,
            verbose=False
        )

        # Vẽ bounding box mặc định
        annotated_frame = results[0].plot()

        detections = []
        for box in results[0].boxes:
            cls_id = int(box.cls[0].item())
            cls_name = self.model.names[cls_id]
            conf_val = float(box.conf[0].item())
            xyxy = list(map(int, box.xyxy[0].tolist()))
            detections.append({
                "class_id": cls_id,
                "name": cls_name,
                "confidence": round(conf_val, 2),
                "box": xyxy
            })

        # Tính toán và vẽ FPS
        now = time.time()
        fps = 1.0 / (now - self.prev_time) if (now - self.prev_time) > 0 else 30.0
        self.prev_time = now

        cv2.putText(
            annotated_frame,
            f"FPS: {fps:.1f} | {self.device_name}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        return annotated_frame, detections