import cv2
import numpy as np


def stroke_points(points: list[tuple[float, float]], spacing: float) -> list[tuple[float, float]]:
    """Linearly interpolate a pointer path so fast movement cannot leave gaps."""
    if not points:
        return []
    result = [points[0]]
    for start, end in zip(points, points[1:]):
        distance = np.hypot(end[0] - start[0], end[1] - start[1])
        count = max(1, int(np.ceil(distance / max(spacing, 0.1))))
        result.extend(
            (start[0] + (end[0] - start[0]) * i / count, start[1] + (end[1] - start[1]) * i / count)
            for i in range(1, count + 1)
        )
    return result


def paint(
    image: np.ndarray,
    points: list[tuple[float, float]],
    color: tuple[int, ...],
    radius: float,
    hardness: float = 0.7,
    opacity: float = 1,
) -> None:
    h, w = image.shape[:2]
    yy, xx = np.ogrid[:h, :w]
    for x, y in stroke_points(points, max(1, radius / 3)):
        d = np.sqrt((xx - x) ** 2 + (yy - y) ** 2) / max(radius, 0.1)
        falloff = np.clip((1 - d) / max(1 - hardness, 0.001), 0, 1) * opacity
        if image.ndim == 2:
            image[:] = image * (1 - falloff) + color[0] * falloff
        else:
            image[:] = image * (1 - falloff[..., None]) + np.array(color) * falloff[..., None]


def local_filter(
    image: np.ndarray, center: tuple[int, int], radius: int, kind: str, strength: float = 1
) -> None:
    x, y = center
    x0, y0 = max(0, x - radius), max(0, y - radius)
    x1, y1 = min(image.shape[1], x + radius + 1), min(image.shape[0], y + radius + 1)
    roi = image[y0:y1, x0:x1]
    blurred = cv2.GaussianBlur(roi, (0, 0), max(0.1, radius / 4))
    filtered = (
        blurred if kind == "blur" else cv2.addWeighted(roi, 1 + strength, blurred, -strength, 0)
    )
    yy, xx = np.ogrid[y0:y1, x0:x1]
    weight = np.clip(1 - np.hypot(xx - x, yy - y) / radius, 0, 1)[..., None]
    roi[:] = np.clip(roi * (1 - weight) + filtered * weight, 0, 255)
