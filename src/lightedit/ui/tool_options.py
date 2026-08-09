from PySide6.QtWidgets import QDoubleSpinBox, QFormLayout, QWidget


class ToolOptions(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QFormLayout(self)
        self.size = QDoubleSpinBox()
        self.size.setRange(1, 1000)
        self.size.setValue(40)
        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0, 100)
        self.opacity.setValue(100)
        layout.addRow("Size", self.size)
        layout.addRow("Opacity", self.opacity)
