from pathlib import Path

import numpy as np
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QDockWidget

from lightedit.core.document import Document, Layer
from lightedit.core.export import JPEGOptions, export_jpeg
from lightedit.core.history import History
from lightedit.core.project import load_project, save_project
from lightedit.shortcuts import SHORTCUTS
from .canvas import Canvas
from .export_dialog import JPEGExportDialog
from .layers_panel import LayersPanel
from .liquify_workspace import LiquifyWorkspace
from .shortcuts_dialog import ShortcutsDialog
from .tool_options import ToolOptions


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("LightEdit")
        self.resize(1100, 750)
        self.document = None
        self.history = History()
        self.active_tool = "brush"
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)
        self.layers = LayersPanel()
        dock = QDockWidget("Layers")
        dock.setWidget(self.layers)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        tools = QDockWidget("Tool Options")
        tools.setWidget(ToolOptions())
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, tools)
        self._actions = {}
        self._build_actions()

    def _action(self, key, callback):
        label, shortcut = SHORTCUTS[key]
        action = QAction(label, self)
        action.setShortcut(QKeySequence(shortcut))
        action.setToolTip(f"{label} ({shortcut})")
        action.triggered.connect(callback)
        self._actions[key] = action
        return action

    def _build_actions(self):
        file = self.menuBar().addMenu("&File")
        file.addAction(self._action("open", self.open))
        file.addAction(self._action("save", self.save))
        file.addAction(self._action("export", self.export))
        edit = self.menuBar().addMenu("&Edit")
        edit.addAction(self._action("undo", self.undo))
        edit.addAction(self._action("redo", self.redo))
        filters = self.menuBar().addMenu("Fi&lter")
        filters.addAction(self._action("liquify", lambda: LiquifyWorkspace(self).exec()))
        help_menu = self.menuBar().addMenu("&Help")
        help_menu.addAction(self._action("shortcuts", lambda: ShortcutsDialog(self).exec()))
        toolbar = self.addToolBar("Tools")
        for key in ("brush", "clone", "heal", "blur_sharpen"):
            toolbar.addAction(
                self._action(key, lambda checked=False, tool=key: self.select_tool(tool))
            )

    def select_tool(self, tool):
        self.active_tool = tool

    def undo(self):
        if self.history.undo() and self.document:
            self.document.dirty = True
            self.canvas.display(self.document.composite())

    def redo(self):
        if self.history.redo() and self.document:
            self.document.dirty = True
            self.canvas.display(self.document.composite())

    def set_document(self, document):
        self.document = document
        self.canvas.display(document.composite())
        self.layers.set_document(document)

    def open_path(self, path: Path):
        if Path(path).suffix.lower() == ".ledit":
            document = load_project(path)
        else:
            pixels = np.array(Image.open(path).convert("RGBA"))
            document = Document(pixels.shape[1], pixels.shape[0], [Layer(pixels, Path(path).stem)])
        self.set_document(document)

    def open(self):
        if not self.confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Open", "", "Images (*.png *.jpg *.jpeg);;LightEdit (*.ledit)"
        )
        if path:
            self.open_path(Path(path))

    def save(self):
        if not self.document:
            return
        path = self.document.path
        if not path:
            path = Path(
                QFileDialog.getSaveFileName(self, "Save Project", "", "LightEdit (*.ledit)")[0]
            )
        if path:
            save_project(self.document, path.with_suffix(".ledit"))

    def export(self):
        if not self.document:
            return
        dialog = JPEGExportDialog(self)
        dialog.width.setValue(self.document.width)
        dialog.height.setValue(self.document.height)
        if not dialog.exec():
            return
        path, _ = QFileDialog.getSaveFileName(self, "Export JPEG", "", "JPEG (*.jpg *.jpeg)")
        if not path:
            return
        target = Path(path).with_suffix(".jpg")
        if (
            target.exists()
            and QMessageBox.question(self, "Overwrite?", f"Replace {target.name}?")
            != QMessageBox.StandardButton.Yes
        ):
            return
        color = dialog.matte.currentColor()
        options = JPEGOptions(
            dialog.quality.value(),
            (dialog.width.value(), dialog.height.value()),
            preserve_aspect=dialog.aspect.isChecked(),
            matte=(color.red(), color.green(), color.blue()),
        )
        export_jpeg(self.document, target, options, overwrite=True)

    def confirm_discard(self) -> bool:
        if not self.document or not self.document.dirty:
            return True
        result = QMessageBox.question(
            self,
            "Unsaved changes",
            "Discard unsaved changes?",
            QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
        )
        return result == QMessageBox.StandardButton.Discard

    def closeEvent(self, event):
        event.accept() if self.confirm_discard() else event.ignore()
