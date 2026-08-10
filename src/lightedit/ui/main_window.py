from pathlib import Path

import numpy as np
from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QFileDialog, QMainWindow, QMessageBox, QDockWidget, QInputDialog

from lightedit.core.document import Document, Layer
from lightedit.core.export import JPEGOptions, export_jpeg
from lightedit.core.history import History
from lightedit.core.project import load_project, save_project
from lightedit.imaging.layers import (
    content_bounds,
    place_on_canvas,
    resize_canvas,
    transform_content,
)
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
        self.active_layer = 0
        self.canvas.files_dropped.connect(self.import_paths)
        self.canvas.transform_requested.connect(self.transform_active_layer)
        self.layers.layer_selected.connect(self.select_layer)
        self.layers.invert_mask.connect(self.invert_active_mask)
        self.layers.half_mask.connect(self.half_active_mask)
        self._build_actions()
        self.set_document(Document(1280, 1280))

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
        edit.addAction("Set Canvas Size…", self.set_canvas_size)
        self.grid_action = edit.addAction("Align to Grid")
        self.grid_action.setCheckable(True)
        self.grid_action.toggled.connect(self.set_grid)
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

    def select_layer(self, index):
        self.active_layer = index
        if self.document and index < len(self.document.layers):
            self.canvas.set_selection(content_bounds(self.document.layers[index].pixels))

    def _refresh(self):
        self.canvas.display(self.document.composite())
        self.layers.set_document(self.document)

    def import_paths(self, paths):
        """Add all dropped/selected image files as layers in their given order."""
        paths = [Path(path) for path in paths]
        if len(paths) == 1 and paths[0].suffix.lower() == ".ledit":
            self.set_document(load_project(paths[0]))
            return
        for path in paths:
            if path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
                continue
            pixels = np.array(Image.open(path).convert("RGBA"))
            self.document.add_layer(
                Layer(
                    place_on_canvas(pixels, (self.document.width, self.document.height)), path.stem
                )
            )
        if paths:
            self.active_layer = max(0, len(self.document.layers) - 1)
            self._refresh()

    def transform_active_layer(self, bounds):
        if not self.document.layers:
            return
        layer = self.document.layers[self.active_layer]
        layer.pixels[:] = transform_content(layer.pixels, bounds)
        if layer.mask is not None:
            layer.mask = transform_content(np.dstack([layer.mask] * 4), bounds)[..., 0]
        self.document.dirty = True
        self._refresh()

    def invert_active_mask(self):
        if not self.document.layers:
            return
        layer = self.document.layers[self.active_layer]
        layer.mask = 255 - (
            layer.mask if layer.mask is not None else np.full(layer.pixels.shape[:2], 255, np.uint8)
        )
        self.document.dirty = True
        self._refresh()

    def half_active_mask(self):
        if not self.document.layers:
            return
        self.document.layers[self.active_layer].mask = np.full(
            (self.document.height, self.document.width), 128, np.uint8
        )
        self.document.dirty = True
        self._refresh()

    def set_grid(self, enabled):
        self.canvas.grid_enabled = enabled
        self.canvas.update()

    def set_canvas_size(self):
        width, ok = QInputDialog.getInt(
            self, "Canvas Size", "Width:", self.document.width, 1, 20000
        )
        if not ok:
            return
        height, ok = QInputDialog.getInt(
            self, "Canvas Size", "Height:", self.document.height, 1, 20000
        )
        if not ok:
            return
        for layer in self.document.layers:
            layer.pixels = resize_canvas(layer.pixels, (width, height))
            if layer.mask is not None:
                rgba_mask = np.dstack([layer.mask] * 4)
                layer.mask = resize_canvas(rgba_mask, (width, height))[..., 0]
        self.document.width, self.document.height, self.document.dirty = width, height, True
        self._refresh()

    def open_path(self, path: Path):
        if Path(path).suffix.lower() == ".ledit":
            document = load_project(path)
        else:
            pixels = np.array(Image.open(path).convert("RGBA"))
            document = Document(1280, 1280)
            document.add_layer(Layer(place_on_canvas(pixels, (1280, 1280)), Path(path).stem))
        self.set_document(document)

    def open(self):
        if not self.confirm_discard():
            return
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Open", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp);;LightEdit (*.ledit)"
        )
        if paths:
            if len(paths) == 1 and Path(paths[0]).suffix.lower() == ".ledit":
                self.open_path(Path(paths[0]))
            else:
                self.set_document(Document(1280, 1280))
                self.import_paths(paths)

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
