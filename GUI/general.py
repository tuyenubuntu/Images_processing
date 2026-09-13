import os
from PySide6.QtWidgets import QMainWindow
from PySide6.QtUiTools import QUiLoader
from PySide6.QtCore import QFile

class GeneralVisionUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ui_path = os.path.join(current_dir, "GUI_vision.ui")
        
        ui_file = QFile(ui_path)
        if not ui_file.open(QFile.ReadOnly):
            raise FileNotFoundError(f"Không thể mở file giao diện tại: {ui_path}")
            
        loader = QUiLoader()
        self.ui = loader.load(ui_file, None)
        ui_file.close()

        if self.ui is None:
            raise RuntimeError(loader.errorString())

        # Gán toàn bộ widget vào giao diện chính để không bị rỗng
        self.setCentralWidget(self.ui)
        self.resize(self.ui.size())
        self.setWindowTitle(self.ui.windowTitle() or "Vision System")
        
        # Shortcut truy cập nhanh đến các widget quan trọng
        self.stream_label = self.ui.findChild(type(self.ui), "stream_label") or getattr(self.ui, "stream_label", None)
        self.connect_btn = self.ui.findChild(type(self.ui), "connect_btn") or getattr(self.ui, "connect_btn", None)
        self.index_camera_cbb = self.ui.findChild(type(self.ui), "index_camera_cbb") or getattr(self.ui, "index_camera_cbb", None)
        self.mode_cbb = self.ui.findChild(type(self.ui), "mode_cbb") or getattr(self.ui, "mode_cbb", None)