import numpy as np

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
    from PIL import Image

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
