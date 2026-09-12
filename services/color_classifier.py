import cv2
import numpy as np

# Bảng ngưỡng HSV chuẩn cho OpenCV (H: 0-180, S: 0-255, V: 0-255)
# Lưu ý: Màu Đỏ nằm ở 2 đầu dải Hue (0-10 và 170-180) nên cần 2 khoảng
COLOR_RANGES = {
    "Red": [
        (np.array([0, 70, 50]), np.array([10, 255, 255])),
        (np.array([170, 70, 50]), np.array([180, 255, 255]))
    ],
    "Orange": [
        (np.array([11, 70, 50]), np.array([25, 255, 255]))
    ],
    "Yellow": [
        (np.array([26, 70, 50]), np.array([35, 255, 255]))
    ],
    "Green": [
        (np.array([36, 50, 50]), np.array([85, 255, 255]))
    ],
    "Blue": [
        (np.array([86, 50, 50]), np.array([130, 255, 255]))
    ],
    "Purple": [
        (np.array([131, 50, 50]), np.array([169, 255, 255]))
    ],
    # Nhóm không màu (Achromatic) dựa chủ yếu vào S và V:
    "Black": [
        (np.array([0, 0, 0]), np.array([180, 255, 45]))
    ],
    "White": [
        (np.array([0, 0, 200]), np.array([180, 40, 255]))
    ],
    "Gray": [
        (np.array([0, 0, 46]), np.array([180, 50, 199]))
    ]
}


def classify_dominant_color(bgr_image, min_pixel_ratio=0.6):
    """
    Phân loại màu sắc chiếm ưu thế nhất trong một vùng ảnh (ROI).
    
    :param bgr_image: Ảnh đầu vào dạng BGR (numpy array)
    :param min_pixel_ratio: Tỷ lệ pixel tối thiểu để công nhận màu đó (mặc định 60%)
    :return: Tuple (Tên_màu, Tỷ_lệ_phần_trăm) hoặc ("Unknown", 0.0)
    """
    if bgr_image is None or bgr_image.size == 0:
        return "None", 0.0

    # Lọc nhiễu nhẹ trước khi đổi không gian màu
    blurred = cv2.GaussianBlur(bgr_image, (5, 5), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    
    total_pixels = bgr_image.shape[0] * bgr_image.shape[1]
    color_scores = {}

    # Quét qua từng khoảng màu đã định nghĩa
    for color_name, ranges in COLOR_RANGES.items():
        combined_mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        
        for lower, upper in ranges:
            mask = cv2.inRange(hsv, lower, upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Đếm số pixel khớp với màu
        matched_pixels = cv2.countNonZero(combined_mask)
        color_scores[color_name] = matched_pixels

    # Tìm màu có số pixel nhiều nhất
    dominant_color = max(color_scores, key=color_scores.get)
    max_count = color_scores[dominant_color]
    ratio = max_count / total_pixels

    if ratio >= min_pixel_ratio:
        return dominant_color, round(ratio * 100, 2)
    
    return "Unknown", round(ratio * 100, 2)