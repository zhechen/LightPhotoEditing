from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QListWidget, QPushButton, QVBoxLayout, QWidget


class LayersPanel(QWidget):
    layer_selected = Signal(int)
    invert_mask = Signal()
    half_mask = Signal()

    def __init__(self):
        super().__init__()
        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._selected)
        invert = QPushButton("Invert mask")
        half = QPushButton("Mask 50%")
        invert.clicked.connect(self.invert_mask)
        half.clicked.connect(self.half_mask)
        buttons = QHBoxLayout()
        buttons.addWidget(invert)
        buttons.addWidget(half)
        layout = QVBoxLayout(self)
        layout.addWidget(self.list)
        layout.addLayout(buttons)

    def _selected(self, row):
        if row >= 0:
            self.layer_selected.emit(self.list.count() - row - 1)

    def count(self):
        return self.list.count()

    def set_document(self, document) -> None:
        self.list.clear()
        for layer in reversed(document.layers):
            self.list.addItem(("◉ " if layer.visible else "○ ") + layer.name)
        if self.list.count():
            self.list.setCurrentRow(0)
