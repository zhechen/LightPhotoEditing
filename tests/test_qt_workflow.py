import numpy as np
from PIL import Image
from PySide6.QtCore import QMimeData, QPoint, Qt, QUrl
from PySide6.QtTest import QTest

from lightedit.core.document import Document, Layer
from lightedit.ui.main_window import MainWindow


def test_offscreen_window_workflow(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    pixels = np.zeros((4, 5, 4), np.uint8)
    pixels[..., 3] = 255
    window.set_document(Document(5, 4, [Layer(pixels)]))
    window.show()
    assert window.canvas.pixmap() is not None
    assert window.layers.count() == 1


def test_multiple_image_import_and_mask_controls(qtbot, tmp_path):
    paths = []
    for index, color in enumerate(((255, 0, 0, 255), (0, 255, 0, 255))):
        path = tmp_path / f"image-{index}.png"
        Image.fromarray(np.full((4, 6, 4), color, np.uint8)).save(path)
        paths.append(path)
    window = MainWindow()
    qtbot.addWidget(window)
    window.import_paths(paths)
    assert (window.document.width, window.document.height) == (1280, 1280)
    assert [layer.name for layer in window.document.layers] == ["image-0", "image-1"]
    window.half_active_mask()
    assert np.all(window.document.layers[window.active_layer].mask == 128)
    window.invert_active_mask()
    assert np.all(window.document.layers[window.active_layer].mask == 127)
    window.document.dirty = False


def test_large_canvas_fits_and_zoom_drag_changes_preview_only(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    window.resize(600, 400)
    pixels = np.zeros((1000, 2000, 4), np.uint8)
    window.set_document(Document(2000, 1000, [Layer(pixels)]))
    window.show()
    qtbot.wait(10)

    assert window.canvas.zoom < 1
    original_size = (window.document.width, window.document.height)
    window.select_tool("zoom")
    start_zoom = window.canvas.zoom
    QTest.mousePress(window.canvas, Qt.MouseButton.LeftButton, pos=QPoint(200, 200))
    QTest.mouseMove(window.canvas, QPoint(300, 200), delay=10)
    QTest.mouseRelease(window.canvas, Qt.MouseButton.LeftButton, pos=QPoint(300, 200))

    assert window.canvas.zoom > start_zoom
    assert (window.document.width, window.document.height) == original_size
    window.select_tool("hand")
    assert window.canvas.cursor().shape() == Qt.CursorShape.OpenHandCursor
    window.select_tool("normal")
    assert window.canvas.cursor().shape() == Qt.CursorShape.ArrowCursor


def test_canvas_drop_emits_local_paths(qtbot, tmp_path):
    window = MainWindow()
    qtbot.addWidget(window)
    path = tmp_path / "dropped.png"
    Image.fromarray(np.zeros((2, 2, 4), np.uint8)).save(path)
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(path))])

    class DropEvent:
        accepted = False

        def mimeData(self):
            return mime

        def acceptProposedAction(self):
            self.accepted = True

    event = DropEvent()
    with qtbot.waitSignal(window.canvas.files_dropped) as blocker:
        window.canvas.dropEvent(event)

    assert blocker.args == [[path]]
    assert event.accepted
    window.document.dirty = False
