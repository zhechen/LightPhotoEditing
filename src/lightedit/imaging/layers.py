"""Geometry operations for full-canvas RGBA layers (independent of Qt)."""

import cv2
import numpy as np


def place_on_canvas(image: np.ndarray, canvas_size: tuple[int, int]) -> np.ndarray:
    """Fit an RGBA image inside ``(width, height)`` and center it on a canvas."""
    width, height = canvas_size
    if image.dtype != np.uint8 or image.ndim != 3 or image.shape[2] != 4:
        raise ValueError("image must be an HxWx4 uint8 RGBA array")
    scale = min(width / image.shape[1], height / image.shape[0], 1.0)
    size = (max(1, round(image.shape[1] * scale)), max(1, round(image.shape[0] * scale)))
    fitted = cv2.resize(image, size, interpolation=cv2.INTER_AREA) if scale < 1 else image
    result = np.zeros((height, width, 4), np.uint8)
    x, y = (width - size[0]) // 2, (height - size[1]) // 2
    result[y : y + size[1], x : x + size[0]] = fitted
    return result


def content_bounds(image: np.ndarray) -> tuple[int, int, int, int]:
    """Return the x, y, width and height of non-transparent content."""
    ys, xs = np.nonzero(image[..., 3])
    if not len(xs):
        return (0, 0, image.shape[1], image.shape[0])
    return (
        int(xs.min()),
        int(ys.min()),
        int(xs.max() - xs.min() + 1),
        int(ys.max() - ys.min() + 1),
    )


def transform_content(image: np.ndarray, bounds: tuple[int, int, int, int]) -> np.ndarray:
    """Resize visible content into bounds, clipping it to the original canvas."""
    sx, sy, sw, sh = content_bounds(image)
    x, y, width, height = (int(v) for v in bounds)
    if width < 1 or height < 1:
        raise ValueError("width and height must be positive")
    source = image[sy : sy + sh, sx : sx + sw]
    resized = cv2.resize(source, (width, height), interpolation=cv2.INTER_LANCZOS4)
    result = np.zeros_like(image)
    left, top = max(0, x), max(0, y)
    right, bottom = min(image.shape[1], x + width), min(image.shape[0], y + height)
    if right > left and bottom > top:
        result[top:bottom, left:right] = resized[top - y : bottom - y, left - x : right - x]
    return result


def resize_canvas(image: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """Center-crop or pad a full-canvas array to ``(width, height)``."""
    width, height = size
    result = np.zeros((height, width, 4), np.uint8)
    copy_w, copy_h = min(width, image.shape[1]), min(height, image.shape[0])
    sx, sy = (image.shape[1] - copy_w) // 2, (image.shape[0] - copy_h) // 2
    dx, dy = (width - copy_w) // 2, (height - copy_h) // 2
    result[dy : dy + copy_h, dx : dx + copy_w] = image[sy : sy + copy_h, sx : sx + copy_w]
    return result
