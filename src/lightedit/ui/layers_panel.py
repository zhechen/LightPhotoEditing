from PySide6.QtWidgets import QListWidget


class LayersPanel(QListWidget):
    def set_document(self, document) -> None:
        self.clear()
        for layer in reversed(document.layers):
            self.addItem(("◉ " if layer.visible else "○ ") + layer.name)
