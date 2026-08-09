import cv2
import numpy as np


def identity_field(height: int, width: int) -> np.ndarray:
    x, y = np.meshgrid(np.arange(width, dtype=np.float32), np.arange(height, dtype=np.float32))
    return np.dstack((x, y))


def push(
    field: np.ndarray,
    center: tuple[float, float],
    delta: tuple[float, float],
    radius: float,
    strength: float = 1,
) -> None:
    yy, xx = np.mgrid[: field.shape[0], : field.shape[1]]
    weight = np.clip(1 - np.hypot(xx - center[0], yy - center[1]) / radius, 0, 1) ** 2 * strength
    # Backward map: dragging content right samples pixels from the left.
    field[..., 0] -= delta[0] * weight
    field[..., 1] -= delta[1] * weight


def apply(image: np.ndarray, field: np.ndarray) -> np.ndarray:
    return cv2.remap(
        image, field[..., 0], field[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT
    )
