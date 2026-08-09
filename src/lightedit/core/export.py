"""JPEG is a flattened export and never changes editable project state."""

import io
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageCms


@dataclass
class JPEGOptions:
    quality: int = 90
    size: tuple[int, int] | None = None
    resampling: Image.Resampling = Image.Resampling.LANCZOS
    preserve_aspect: bool = True
    matte: tuple[int, int, int] = (255, 255, 255)
    keep_metadata: bool = False


def jpeg_bytes(document, options: JPEGOptions) -> bytes:
    rgba = Image.fromarray(document.composite(), "RGBA")
    if options.size:
        rgba.thumbnail(options.size, options.resampling) if options.preserve_aspect else None
        if not options.preserve_aspect:
            rgba = rgba.resize(options.size, options.resampling)
    matte = Image.new("RGB", rgba.size, options.matte)
    matte.paste(rgba, mask=rgba.getchannel("A"))
    # Explicitly tag output as sRGB; editable source metadata is intentionally not inherited by default.
    profile = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    stream = io.BytesIO()
    matte.save(
        stream,
        "JPEG",
        quality=max(1, min(100, options.quality)),
        optimize=True,
        icc_profile=profile,
    )
    return stream.getvalue()


def estimate_size(document, options: JPEGOptions) -> int:
    return len(jpeg_bytes(document, options))


def export_jpeg(document, path: Path, options: JPEGOptions, overwrite: bool = False) -> None:
    path = Path(path)
    if path.exists() and not overwrite:
        raise FileExistsError(path)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(jpeg_bytes(document, options))
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise
