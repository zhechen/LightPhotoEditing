"""Editable document model. Pixel storage is deliberately UI-independent."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from uuid import uuid4

import numpy as np


@dataclass
class Transform:
    x: float = 0
    y: float = 0
    rotation: float = 0
    scale_x: float = 1
    scale_y: float = 1


@dataclass
class Selection:
    mask: np.ndarray | None = None


@dataclass
class Layer:
    pixels: np.ndarray
    name: str = "Layer"
    opacity: float = 1.0
    blend_mode: str = "normal"
    visible: bool = True
    mask: np.ndarray | None = None
    transform: Transform = field(default_factory=Transform)
    id: str = field(default_factory=lambda: uuid4().hex)

    def __post_init__(self) -> None:
        if self.pixels.dtype != np.uint8 or self.pixels.ndim != 3 or self.pixels.shape[2] != 4:
            raise ValueError("layer pixels must be an HxWx4 uint8 RGBA array")
        if self.mask is not None and (
            self.mask.dtype != np.uint8 or self.mask.shape != self.pixels.shape[:2]
        ):
            raise ValueError("mask must be an aligned HxW uint8 array")
        self.opacity = float(np.clip(self.opacity, 0, 1))


@dataclass
class Document:
    width: int
    height: int
    layers: list[Layer] = field(default_factory=list)
    selection: Selection = field(default_factory=Selection)
    path: Path | None = None
    dirty: bool = False

    def add_layer(self, layer: Layer) -> None:
        if layer.pixels.shape[:2] != (self.height, self.width):
            raise ValueError("layer dimensions must match the document")
        self.layers.append(layer)
        self.dirty = True

    def mark_saved(self, path: Path | None = None) -> None:
        self.path = path or self.path
        self.dirty = False

    def composite(self) -> np.ndarray:
        from lightedit.imaging.composite import composite_layers

        return composite_layers(self.layers, (self.height, self.width))
