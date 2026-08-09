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
