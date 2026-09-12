import time
import cv2
import torch
from ultralytics import YOLO

# 1. Kiểm tra và chọn thiết bị tính toán (ưu tiên GPU RTX 3060)
device = 0 if torch.cuda.is_available() else "cpu"
print(f"Khởi chạy trên thiết bị: {torch.cuda.get_device_name(0) if device == 0 else 'CPU'}")

# 2. Tải mô hình YOLO (tự động tải pre-trained weights nếu chưa có)
# yolo11n.pt (siêu nhẹ ~100+ FPS), yolo11m.pt (cân bằng), yolo11x.pt (chính xác cao nhất)
model = YOLO("yolo11m.pt")

# 3. Khởi tạo USB Camera (thay đổi index 0, 1 hoặc 2 tùy cổng cắm USB)
camera_index = 0
cap = cv2.VideoCapture(camera_index)

# Cấu hình độ phân giải và định dạng khung hình (tùy thông số hỗ trợ của USB camera)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))

if not cap.isOpened():
    print(f"Lỗi: Không thể kết nối tới USB camera ở cổng {camera_index}.")
    exit()

print("Camera đã sẵn sàng. Nhấn 'q' trên cửa sổ hình ảnh để thoát.")

prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Mất tín hiệu từ camera!")
        break

    # 4. Dự đoán bằng YOLO trên GPU
    # conf=0.4: Ngưỡng lọc độ tin cậy; imgsz=640: Kích thước chuẩn hóa đầu vào mạng
    results = model.predict(source=frame, device=device, conf=0.4, imgsz=640, verbose=False)

    # 5. Vẽ bounding box và label mặc định của Ultralytics
    annotated_frame = results[0].plot()

    # 6. Trích xuất dữ liệu tọa độ & nhãn (phục vụ lấy dữ liệu xử lý tiếp)
    for box in results[0].boxes:
        cls_id = int(box.cls[0].item())
        cls_name = model.names[cls_id]
        confidence = float(box.conf[0].item())
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        # print(f"Phát hiện: {cls_name} ({confidence:.2f}) tại [{x1}, {y1}, {x2}, {y2}]")

    # 7. Tính toán và hiển thị FPS thực tế
    current_time = time.time()
    fps = 1.0 / (current_time - prev_time)
    prev_time = current_time

    cv2.putText(
        annotated_frame,
        f"FPS: {fps:.1f} | Device: GPU 3060" if device == 0 else f"FPS: {fps:.1f} | Device: CPU",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    # 8. Hiển thị cửa sổ kết quả
    cv2.imshow("USB Camera - YOLO Object Detection", annotated_frame)

    # Thoát vòng lặp khi bấm phím 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()