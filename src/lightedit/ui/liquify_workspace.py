from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout


class LiquifyWorkspace(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Liquify")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Drag to push pixels; accept to apply."))
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
