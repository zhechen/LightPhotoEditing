from pathlib import Path

from PySide6.QtCore import QPoint, QRect, Qt, Signal
from PySide6.QtGui import QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel


class Canvas(QLabel):
    files_dropped = Signal(list)
    transform_requested = Signal(tuple)

    def __init__(self) -> None:
        super().__init__("Open an image or project to begin")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.grid_enabled = False
        self.grid_size = 32
        self.selection = None
        self._drag_start = None
        self._start_bounds = None
        self._resizing = False

    def set_selection(self, bounds) -> None:
        self.selection = bounds
        self.update()

    def display(self, rgba) -> None:
        h, w = rgba.shape[:2]
        image = QImage(rgba.data, w, h, rgba.strides[0], QImage.Format.Format_RGBA8888).copy()
        self.setPixmap(QPixmap.fromImage(image))

    def dragEnterEvent(self, event):
        if any(url.isLocalFile() for url in event.mimeData().urls()):
            event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        self.files_dropped.emit(paths)
        event.acceptProposedAction()

    def _image_point(self, position):
        pixmap = self.pixmap()
        if not pixmap:
            return QPoint()
        return QPoint(
            round(position.x() - (self.width() - pixmap.width()) / 2),
            round(position.y() - (self.height() - pixmap.height()) / 2),
        )

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton or not self.selection:
            return super().mousePressEvent(event)
        point = self._image_point(event.position())
        x, y, w, h = self.selection
        rect = QRect(x, y, w, h)
        if rect.adjusted(-8, -8, 8, 8).contains(point):
            self._drag_start, self._start_bounds = point, self.selection
            self._resizing = abs(point.x() - (x + w)) < 12 and abs(point.y() - (y + h)) < 12

    def mouseMoveEvent(self, event):
        if self._drag_start is None:
            return
        point = self._image_point(event.position())
        dx, dy = point.x() - self._drag_start.x(), point.y() - self._drag_start.y()
        x, y, w, h = self._start_bounds
        bounds = (
            (x, y, max(1, w + dx), max(1, h + dy)) if self._resizing else (x + dx, y + dy, w, h)
        )
        if self.grid_enabled:
            bounds = tuple(
                round(v / self.grid_size) * self.grid_size if i < 2 or self._resizing else v
                for i, v in enumerate(bounds)
            )
        self.selection = bounds
        self.update()

    def mouseReleaseEvent(self, event):
        if self._drag_start is not None:
            self._drag_start = None
            self.transform_requested.emit(self.selection)

    def paintEvent(self, event):
        super().paintEvent(event)
        pixmap = self.pixmap()
        if not pixmap:
            return
        painter = QPainter(self)
        ox, oy = (self.width() - pixmap.width()) // 2, (self.height() - pixmap.height()) // 2
        if self.grid_enabled:
            painter.setPen(QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DotLine))
            for x in range(self.grid_size, pixmap.width(), self.grid_size):
                painter.drawLine(ox + x, oy, ox + x, oy + pixmap.height())
            for y in range(self.grid_size, pixmap.height(), self.grid_size):
                painter.drawLine(ox, oy + y, ox + pixmap.width(), oy + y)
        if self.selection:
            x, y, w, h = self.selection
            painter.setPen(QPen(Qt.GlobalColor.white, 1, Qt.PenStyle.DashLine))
            painter.drawRect(ox + x, oy + y, w, h)
            painter.fillRect(ox + x + w - 5, oy + y + h - 5, 10, 10, Qt.GlobalColor.white)
