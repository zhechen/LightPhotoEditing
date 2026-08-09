import cv2
import numpy as np


def inpaint(image: np.ndarray, mask: np.ndarray, radius: float = 3) -> np.ndarray:
    rgb = cv2.inpaint(image[..., :3], mask, radius, cv2.INPAINT_TELEA)
    return np.dstack((rgb, image[..., 3])) if image.shape[2] == 4 else rgb


def clone_stamp(
    image: np.ndarray,
    source: tuple[int, int],
    target: tuple[int, int],
    radius: int,
    aligned: bool = True,
    offset: tuple[int, int] | None = None,
) -> tuple[int, int]:
    effective = (
        offset if aligned and offset is not None else (source[0] - target[0], source[1] - target[1])
    )
    ox, oy = effective
    original = image.copy()
    h, w = image.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    mask = (xx - target[0]) ** 2 + (yy - target[1]) ** 2 <= radius**2
    ys, xs = np.where(mask)
    sx, sy = xs + ox, ys + oy
    valid = (sx >= 0) & (sx < w) & (sy >= 0) & (sy < h)
    image[ys[valid], xs[valid]] = original[sy[valid], sx[valid]]
    return effective
