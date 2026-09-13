import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from GUI.general import GeneralVisionUI
from services.images_loader import CameraStreamThread
from services.config_loader import load_camera_config, load_process_config

class AppController:
    def __init__(self):
        self.window = GeneralVisionUI()
        
        self.cam_config = load_camera_config("configs/config.xml")
        self.proc_config = load_process_config("configs/config_process.xml")
        
        self._init_comboboxes()
        self.camera_thread = None

        # Kết nối sự kiện nút bấm & thay đổi mode
        if self.window.connect_btn:
            self.window.connect_btn.clicked.connect(self.toggle_camera)

        if self.window.mode_cbb:
            self.window.mode_cbb.currentTextChanged.connect(self.on_mode_changed)

    def _init_comboboxes(self):
        if self.window.index_camera_cbb:
            self.window.index_camera_cbb.clear()
            self.window.index_camera_cbb.addItems(["Camera 0", "Camera 1", "Camera 2"])
            self.window.index_camera_cbb.setCurrentIndex(self.cam_config.get("camera_index", 0))
            
        if self.window.mode_cbb:
            self.window.mode_cbb.clear()
            self.window.mode_cbb.addItems(["Color Classifier", "YOLOv11"])

    def on_mode_changed(self, mode_name):
        """Đổi mode động khi thread đang stream"""
        if self.camera_thread and self.camera_thread.isRunning():
            self.camera_thread.set_mode(mode_name)

    def toggle_camera(self):
            if self.camera_thread is None or not self.camera_thread.isRunning():
                selected_cam = self.window.index_camera_cbb.currentIndex() if self.window.index_camera_cbb else None
                selected_mode = self.window.mode_cbb.currentText() if self.window.mode_cbb else "Color Classifier"
                
                self.camera_thread = CameraStreamThread(camera_index=selected_cam, mode=selected_mode)
                self.camera_thread.frame_received.connect(self.update_stream_label)
                self.camera_thread.start()
                
                # Đổi text nút Connect
                if self.window.connect_btn:
                    self.window.connect_btn.setText("Disconnect")
                
                # KHÓA CÁC COMBOBOX KHI ĐANG CHẠY
                if self.window.index_camera_cbb:
                    self.window.index_camera_cbb.setEnabled(False)
                if self.window.mode_cbb:
                    self.window.mode_cbb.setEnabled(False)

            else:
                self.camera_thread.stop()
                self.camera_thread = None
                
                if self.window.connect_btn:
                    self.window.connect_btn.setText("Connect")
                    
                # MỞ KHÓA LẠI CÁC COMBOBOX KHI DISCONNECT
                if self.window.index_camera_cbb:
                    self.window.index_camera_cbb.setEnabled(True)
                if self.window.mode_cbb:
                    self.window.mode_cbb.setEnabled(True)

    def update_stream_label(self, qt_image, result_info):
        if self.window.stream_label:
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.window.stream_label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.window.stream_label.setPixmap(scaled_pixmap)

    def run(self):
        self.window.show()

def main():
    app = QApplication(sys.argv)
    controller = AppController()
    controller.run()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()