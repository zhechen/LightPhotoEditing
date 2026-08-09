from PySide6.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout

from lightedit.shortcuts import SHORTCUTS


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        layout = QVBoxLayout(self)
        table = QTableWidget(len(SHORTCUTS), 2)
        table.setHorizontalHeaderLabels(["Action", "Shortcut"])
        for row, (label, shortcut) in enumerate(SHORTCUTS.values()):
            table.setItem(row, 0, QTableWidgetItem(label))
            table.setItem(row, 1, QTableWidgetItem(shortcut))
        layout.addWidget(table)
