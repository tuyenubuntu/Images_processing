import os
import xml.etree.ElementTree as ET

def load_camera_config(config_path="configs/config.xml"):
    """
    Đọc file XML và trả về cấu hình dưới dạng Dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Không tìm thấy file cấu hình tại: {config_path}")

    # Phân tích cú pháp file XML
    tree = ET.parse(config_path)
    root = tree.getroot()

    # Trích xuất các thông số từ thẻ <Camera>
    camera_node = root.find("Camera")
    window_node = root.find("Window")

    config = {
        "camera_index": int(camera_node.find("Index").text.strip()),
        "width": int(camera_node.find("Width").text.strip()),
        "height": int(camera_node.find("Height").text.strip()),
        "fps": int(camera_node.find("Fps").text.strip()),
        "backend": camera_node.find("Backend").text.strip() if camera_node.find("Backend") is not None else "DEFAULT",
        "window_title": window_node.find("Title").text.strip() if window_node is not None else "Camera"
    }

    return config


def load_process_config(config_path="configs/config_process.xml"):
    """
    Đọc file XML và trả về cấu hình quá trình dưới dạng Dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Không tìm thấy file cấu hình tại: {config_path}")

    # Phân tích cú pháp file XML
    tree = ET.parse(config_path)
    root = tree.getroot()

    # Trích xuất các thông số từ thẻ <Camera>
    classifier_node = root.find("classifier")
    roi_node = root.find("roi")

    config = {
        "classifier": {
            "max_count": int(classifier_node.find("MaxCount").text.strip()),
            "min_pixel_ratio": float(classifier_node.find("min_pixel_ratio").text.strip()),
            "stability_filter": classifier_node.find("stability_filter").text.strip().lower() == "true"
        },
        "roi": {
            "x": int(roi_node.find("x").text.strip()),
            "y": int(roi_node.find("y").text.strip()),
            "width": int(roi_node.find("width").text.strip()),
            "height": int(roi_node.find("height").text.strip())
        }
    }

    return config

# Chạy test độc lập file này nếu cần
if __name__ == "__main__":
    try:
        cfg = load_process_config()
        print("Đọc cấu hình quá trình thành công:")
        print(cfg)
    except Exception as e:
        print(f"Lỗi: {e}")