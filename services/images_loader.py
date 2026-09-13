import cv2
import numpy as np
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage

from services.config_loader import load_camera_config, load_process_config
from services.color_classifier import classify_dominant_color
from services.output_color import PLC_COLOR_CODES
from services.yolo_images_processing import YoloProcessor


class CameraStreamThread(QThread):
    frame_received = Signal(QImage, dict)

    def __init__(self, camera_index=None, mode="Color Classifier", cam_config_path="configs/config.xml", proc_config_path="configs/config_process.xml"):
        super().__init__()
        
        self.cam_config = load_camera_config(cam_config_path)
        self.proc_config = load_process_config(proc_config_path)

        self.camera_index = camera_index if camera_index is not None else self.cam_config["camera_index"]
        self.width = self.cam_config.get("width", 1280)
        self.height = self.cam_config.get("height", 720)
        self.fps = self.cam_config.get("fps", 30)
        self.backend = self.cam_config.get("backend", "DSHOW").upper()
        
        self.mode = mode
        self.is_running = False

        # Lazy loading YOLO: khởi tạo sẵn để dùng
        self.yolo_processor = None

    def set_mode(self, mode_name):
        """Thay đổi mode trực tiếp từ GUI khi camera đang chạy"""
        self.mode = mode_name

    def run(self):
        cv_backend = cv2.CAP_DSHOW if self.backend == "DSHOW" else cv2.CAP_ANY
        cap = cv2.VideoCapture(self.camera_index, cv_backend)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        cap.set(cv2.CAP_PROP_FPS, self.fps)

        if not cap.isOpened():
            print(f"[CameraStreamThread] Không thể mở camera index {self.camera_index}")
            return

        # Cấu hình Color Classifier
        classifier_cfg = self.proc_config["classifier"]
        roi_cfg = self.proc_config["roi"]
        use_stability = classifier_cfg.get("stability_filter", False)
        max_count = classifier_cfg.get("max_count", 6)
        min_pixel_ratio = classifier_cfg.get("min_pixel_ratio", 0.5)

        current_candidate = "Unknown"
        frame_counter = 0
        ratio_history = []
        confirmed_color = "Unknown"
        confirmed_code = 0
        confirmed_ratio = 0.0

        self.is_running = True

        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                continue

            result_info = {"mode": self.mode}
            display_frame = frame

            # --- CHẾ ĐỘ 1: YOLO ---
            if self.mode == "YOLOv11":
                if self.yolo_processor is None:
                    # Model đường dẫn models/yolo11m.pt
                    self.yolo_processor = YoloProcessor("models/yolo11m.pt")
                
                display_frame, detections = self.yolo_processor.process_frame(frame)
                result_info["detections"] = detections

            # --- CHẾ ĐỘ 2: COLOR CLASSIFIER ---
            else:
                x1 = roi_cfg["x"]
                y1 = roi_cfg["y"]
                x2 = x1 + roi_cfg["width"]
                y2 = y1 + roi_cfg["height"]

                roi = frame[y1:y2, x1:x2]
                color_name, confidence = classify_dominant_color(roi, min_pixel_ratio=min_pixel_ratio)

                if use_stability:
                    if color_name == current_candidate and confidence != 0:
                        frame_counter += 1
                        ratio_history.append(confidence)
                    else:
                        current_candidate = color_name
                        frame_counter = 1 if color_name != "Unknown" else 0
                        ratio_history = [confidence] if color_name != "Unknown" else []

                    if frame_counter >= max_count:
                        confirmed_color = current_candidate
                        confirmed_code = PLC_COLOR_CODES.get(confirmed_color, 0)
                        confirmed_ratio = round(sum(ratio_history) / len(ratio_history), 2)
                    elif color_name == "Unknown" and frame_counter == 0 and confirmed_color != "Unknown":
                        confirmed_color = "Unknown"
                        confirmed_code = 0
                        confirmed_ratio = 0.0

                    d_color, d_ratio, d_code = confirmed_color, confirmed_ratio, confirmed_code
                else:
                    d_color, d_ratio, d_code = color_name, confidence, PLC_COLOR_CODES.get(color_name, 0)

                display_frame = frame.copy()
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    display_frame,
                    f"{d_color} ({d_ratio}%) PLC: {d_code}",
                    (x1, max(y1 - 10, 25)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )
                result_info.update({"color": d_color, "confidence": d_ratio, "plc_code": d_code})

            # Chuyển đổi sang QImage
            rgb_image = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            qt_image = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888).copy()

            self.frame_received.emit(qt_image, result_info)

        cap.release()

    def stop(self):
        self.is_running = False
        self.wait()