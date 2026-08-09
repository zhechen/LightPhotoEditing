"""Versioned, lossless and atomic .ledit persistence."""

from __future__ import annotations

import json
import os
import tempfile
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from .document import Document, Layer, Transform

FORMAT_VERSION = 1


def _png_bytes(array: np.ndarray) -> bytes:
    import io

    stream = io.BytesIO()
    Image.fromarray(array).save(stream, format="PNG")
    return stream.getvalue()


def save_project(document: Document, path: Path) -> None:
    path = Path(path)
    manifest = {
        "version": FORMAT_VERSION,
        "width": document.width,
        "height": document.height,
        "layers": [],
    }
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    os.close(fd)
    try:
        with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
            for layer in document.layers:
                image_name = f"layers/{layer.id}.png"
                mask_name = f"masks/{layer.id}.png" if layer.mask is not None else None
                archive.writestr(image_name, _png_bytes(layer.pixels))
                if mask_name:
                    archive.writestr(mask_name, _png_bytes(layer.mask))
                manifest["layers"].append(
                    {
                        "id": layer.id,
                        "name": layer.name,
                        "opacity": layer.opacity,
                        "blend_mode": layer.blend_mode,
                        "visible": layer.visible,
                        "image": image_name,
                        "mask": mask_name,
                        "transform": vars(layer.transform),
                    }
                )
            archive.writestr("manifest.json", json.dumps(manifest, indent=2))
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
    document.mark_saved(path)


def load_project(path: Path) -> Document:
    with zipfile.ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("version") != FORMAT_VERSION:
            raise ValueError("unsupported .ledit version")
        layers = []
        import io

        for item in manifest["layers"]:
            pixels = np.array(Image.open(io.BytesIO(archive.read(item["image"]))).convert("RGBA"))
            mask = (
                np.array(Image.open(io.BytesIO(archive.read(item["mask"]))).convert("L"))
                if item["mask"]
                else None
            )
            layers.append(
                Layer(
                    pixels,
                    item["name"],
                    item["opacity"],
                    item["blend_mode"],
                    item["visible"],
                    mask,
                    Transform(**item["transform"]),
                    item["id"],
                )
            )
    return Document(manifest["width"], manifest["height"], layers, path=Path(path))


class RecoveryManager:
    def __init__(self, directory: Path) -> None:
        self.path = Path(directory) / "recovery.ledit"

    def autosave(self, document: Document) -> None:
        save_project(document, self.path)
        document.dirty = True

    def available(self) -> bool:
        return self.path.exists()

    def recover(self) -> Document:
        return load_project(self.path)

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)
