import cv2
from services.config_loader import load_camera_config
from services.config_loader import load_process_config
from services.color_classifier import classify_dominant_color
from services.output_color import PLC_COLOR_CODES

def main():
    # 1. Đọc cấu hình từ file XML trong folder configs
    try:
        config = load_camera_config("configs/config.xml")
        config_process = load_process_config("configs/config_process.xml")
        print("Đã tải cấu hình thành công:")
        for k, v in config.items():
            print(f" - {k}: {v}")
        print("Đã tải cấu hình quá trình thành công:")
        for k, v in config_process.items():
            print(f" - {k}: {v}")
    except Exception as e:
        print(f"Lỗi khi đọc file cấu hình: {e}")
        return

    cam_idx = config["camera_index"]
    backend_str = config.get("backend", "DEFAULT").upper()
    max_count = config_process["classifier"].get("max_count", 10)

    # Biến trạng thái để lọc ổn định (Debounce / Stability filter)
    current_candidate = "Unknown"  # Màu đang theo dõi
    frame_counter = 0              # Đếm số frame liên tiếp của candidate
    ratio_history = []             # Lưu tỷ lệ các frame để tính trung bình khi đủ count

    # Kết quả đã được xác nhận (Confirmed) gửi cho PLC
    confirmed_color = "Unknown"
    confirmed_code = 0
    confirmed_ratio = 0.0

    # 2. Chọn backend tương ứng (DSHOW trên Windows giúp khởi động USB cam rất nhanh)
    backend = cv2.CAP_DSHOW
    if backend_str == "DSHOW":
        backend = cv2.CAP_DSHOW

    # 3. Khởi tạo camera
    cap = cv2.VideoCapture(cam_idx, backend)
    
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print(f"\n[LỖI] Không thể mở camera ở cổng {cam_idx}!")
        print("Gợi ý: Mở 'configs/config.xml' và thử đổi <Index>0</Index> thành 1 hoặc 2.")
        return

    # Thiết lập độ phân giải và FPS theo cấu hình XML
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config["width"])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config["height"])
    cap.set(cv2.CAP_PROP_FPS, config["fps"])

    # Lấy thông số thực tế sau khi set (vì một số cam chỉ hỗ trợ các mức cố định)
    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"\nĐang mở camera: {actual_w}x{actual_h} @ {actual_fps}FPS")
    print("Nhấn phím 'q' trên cửa sổ video để thoát.")

    window_title = config.get("window_title", "Camera Live")

    # 4. Vòng lặp hiển thị khung hình
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[Cảnh báo] Mất tín hiệu từ camera.")
            break


        # Tạo vùng quan sát (ROI) kích thước 150x150 tại tâm màn hình
        width_box_size = config_process["roi"]["width"]
        height_box_size = config_process["roi"]["height"]

        x1 = config_process["roi"]["x"]
        y1 = config_process["roi"]["y"]
        x2 = x1 + width_box_size
        y2 = y1 + height_box_size

        # Cắt lấy vùng ảnh ROI
        roi = frame[y1:y2, x1:x2]

        # Gọi hàm phân loại màu
        color_name, confidence = classify_dominant_color(roi, min_pixel_ratio=config_process["classifier"]["min_pixel_ratio"])

        if config_process["classifier"]["stability_filter"]:
            print ("Test mode: Stability filter ON")
            if color_name == current_candidate and confidence != 0:
                # Nếu frame này vẫn là màu frame trước đó -> Tăng đếm
                frame_counter += 1
                ratio_history.append(confidence)
            else:
                # Nếu đổi màu khác hoặc mất màu -> Reset lại từ đầu
                current_candidate = color_name
                frame_counter = 1 if color_name != "Unknown" else 0
                ratio_history = [confidence] if color_name != "Unknown" else []

            # 3. Khi đạt đủ số khung hình quy định -> Tính toán và chốt giá trị
            if frame_counter == max_count:
                confirmed_color = current_candidate
                confirmed_code = PLC_COLOR_CODES.get(confirmed_color, 0)
                
                # Tính tỷ lệ trung bình chính xác của chuỗi khung hình vừa qua
                confirmed_ratio = round(sum(ratio_history) / len(ratio_history), 2)

            elif color_name == "Unknown" and frame_counter == 0 and confirmed_color != "Unknown":
                # Nếu không có vật thể trong khung -> Reset trạng thái đã chốt về 0
                confirmed_color = "Unknown"
                confirmed_code = 0
                confirmed_ratio = 0.0

            # Vẽ khung ROI và hiển thị kết quả lên màn hình
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            plc_code = PLC_COLOR_CODES.get(confirmed_color, 0)
            label = f"{confirmed_color} ({confirmed_ratio}%) PLC Code: {plc_code}"

        # Vẽ khung ROI và hiển thị kết quả lên màn hình
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        plc_code = PLC_COLOR_CODES.get(color_name, 0)
        label = f"{color_name} ({confidence}%) PLC Code: {plc_code}"
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow(window_title, frame)

        # Thoát nếu nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyAllWindows()
    print("Đã đóng camera.")

if __name__ == "__main__":
    main()