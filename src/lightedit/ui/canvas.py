import math
from pathlib import Path

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QCursor, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QLabel


class Canvas(QLabel):
    """A non-destructive, zoomable view of the document canvas."""

    files_dropped = Signal(list)
    transform_requested = Signal(tuple)
    mode_changed = Signal(str)
    zoom_changed = Signal(float)

    def __init__(self) -> None:
        super().__init__("Open an image or project to begin")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAcceptDrops(True)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.grid_enabled = False
        self.grid_size = 32
        self.selection = None
        self.mode = "normal"
        self.zoom = 1.0
        self._fit_to_window = True
        self._source = None
        self._pan = QPointF()
        self._drag_start = None
        self._start_pan = None
        self._start_zoom = None
        self._start_bounds = None
        self._resizing = False
        self.set_mode("normal")

    def set_selection(self, bounds) -> None:
        self.selection = bounds
        self.update()

    def display(self, rgba) -> None:
        h, w = rgba.shape[:2]
        size_changed = self._source is None or self._source.size().toTuple() != (w, h)
        image = QImage(rgba.data, w, h, rgba.strides[0], QImage.Format.Format_RGBA8888).copy()
        self._source = QPixmap.fromImage(image)
        # Retain QLabel's pixmap API for integrations while doing custom scaled painting below.
        self.setPixmap(self._source)
        if size_changed:
            self.fit_to_window()
        self.update()

    def set_mode(self, mode: str) -> None:
        if mode not in {"normal", "zoom", "hand"}:
            raise ValueError(f"Unknown canvas mode: {mode}")
        self.mode = mode
        if mode == "hand":
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        elif mode == "zoom":
            self.setCursor(self._zoom_cursor())
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        self.mode_changed.emit(mode)

    @staticmethod
    def _zoom_cursor() -> QCursor:
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("black"), 3))
        painter.drawEllipse(2, 2, 13, 13)
        painter.drawLine(13, 13, 21, 21)
        painter.setPen(QPen(QColor("white"), 1))
        painter.drawEllipse(2, 2, 13, 13)
        painter.end()
        return QCursor(pixmap, 7, 7)

    def fit_to_window(self) -> None:
        if not self._source:
            return
        margin = 24
        self.zoom = min(
            1.0,
            max(0.01, (self.width() - margin) / self._source.width()),
            max(0.01, (self.height() - margin) / self._source.height()),
        )
        self._fit_to_window = True
        self._pan = QPointF()
        self.zoom_changed.emit(self.zoom)
        self.update()

    def set_zoom(self, zoom: float) -> None:
        self.zoom = min(32.0, max(0.01, zoom))
        self._fit_to_window = False
        self.zoom_changed.emit(self.zoom)
        self.update()

    def zoom_in(self) -> None:
        self.set_zoom(self.zoom * 1.25)

    def zoom_out(self) -> None:
        self.set_zoom(self.zoom / 1.25)

    def actual_size(self) -> None:
        self.set_zoom(1.0)
        self._pan = QPointF()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._fit_to_window:
            self.fit_to_window()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls() and any(url.isLocalFile() for url in event.mimeData().urls()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        paths = [Path(url.toLocalFile()) for url in event.mimeData().urls() if url.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()

    def _origin(self) -> QPointF:
        if not self._source:
            return QPointF()
        return QPointF(
            (self.width() - self._source.width() * self.zoom) / 2 + self._pan.x(),
            (self.height() - self._source.height() * self.zoom) / 2 + self._pan.y(),
        )

    def _image_point(self, position):
        origin = self._origin()
        return QPoint(
            round((position.x() - origin.x()) / self.zoom),
            round((position.y() - origin.y()) / self.zoom),
        )

    def mousePressEvent(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return super().mousePressEvent(event)
        self.setFocus()
        if self.mode in {"zoom", "hand"}:
            self._drag_start = event.position()
            self._start_pan = QPointF(self._pan)
            self._start_zoom = self.zoom
            if self.mode == "hand":
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
            return
        if not self.selection:
            return super().mousePressEvent(event)
        point = self._image_point(event.position())
        x, y, w, h = self.selection
        if QRectF(x, y, w, h).adjusted(-8, -8, 8, 8).contains(point):
            self._drag_start, self._start_bounds = point, self.selection
            self._resizing = abs(point.x() - (x + w)) < 12 and abs(point.y() - (y + h)) < 12

    def mouseMoveEvent(self, event):
        if self._drag_start is None:
            return
        if self.mode == "hand":
            delta = event.position() - self._drag_start
            self._pan = self._start_pan + delta
            self._fit_to_window = False
            self.update()
            return
        if self.mode == "zoom":
            delta = event.position().x() - self._drag_start.x()
            self.set_zoom(self._start_zoom * math.pow(2, delta / 160))
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
        if self._drag_start is None:
            return
        was_transform = self.mode == "normal" and self._start_bounds is not None
        self._drag_start = None
        self._start_bounds = None
        if self.mode == "hand":
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        if was_transform:
            self.transform_requested.emit(self.selection)

    def paintEvent(self, event):
        if not self._source:
            return super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(42, 42, 42))
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        origin = self._origin()
        target = QRectF(
            origin.x(),
            origin.y(),
            self._source.width() * self.zoom,
            self._source.height() * self.zoom,
        )
        painter.drawPixmap(target, self._source, QRectF(self._source.rect()))
        if self.grid_enabled:
            painter.setPen(QPen(Qt.GlobalColor.gray, 1, Qt.PenStyle.DotLine))
            for x in range(self.grid_size, self._source.width(), self.grid_size):
                painter.drawLine(
                    int(origin.x() + x * self.zoom),
                    int(origin.y()),
                    int(origin.x() + x * self.zoom),
                    int(target.bottom()),
                )
            for y in range(self.grid_size, self._source.height(), self.grid_size):
                painter.drawLine(
                    int(origin.x()),
                    int(origin.y() + y * self.zoom),
                    int(target.right()),
                    int(origin.y() + y * self.zoom),
                )
        if self.selection:
            x, y, w, h = self.selection
            rect = QRectF(
                origin.x() + x * self.zoom,
                origin.y() + y * self.zoom,
                w * self.zoom,
                h * self.zoom,
            )
            painter.setPen(QPen(Qt.GlobalColor.white, 1, Qt.PenStyle.DashLine))
            painter.drawRect(rect)
            painter.fillRect(
                QRectF(rect.right() - 5, rect.bottom() - 5, 10, 10), Qt.GlobalColor.white
            )
