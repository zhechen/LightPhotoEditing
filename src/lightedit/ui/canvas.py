from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel


class Canvas(QLabel):
    def __init__(self) -> None:
        super().__init__("Open an image or project to begin")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def display(self, rgba) -> None:
        h, w = rgba.shape[:2]
        image = QImage(rgba.data, w, h, rgba.strides[0], QImage.Format.Format_RGBA8888).copy()
        self.setPixmap(QPixmap.fromImage(image))
