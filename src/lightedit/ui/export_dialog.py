from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QSpinBox,
)


class JPEGExportDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Export JPEG")
        layout = QFormLayout(self)
        self.quality = QSpinBox()
        self.quality.setRange(1, 100)
        self.quality.setValue(90)
        self.width = QSpinBox()
        self.width.setRange(1, 100000)
        self.height = QSpinBox()
        self.height.setRange(1, 100000)
        self.aspect = QCheckBox()
        self.aspect.setChecked(True)
        self.matte = QColorDialog()
        self.matte.setOption(QColorDialog.ColorDialogOption.NoButtons)
        layout.addRow("Quality", self.quality)
        layout.addRow("Width", self.width)
        layout.addRow("Height", self.height)
        layout.addRow("Preserve aspect", self.aspect)
        layout.addRow("Matte", self.matte)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)
