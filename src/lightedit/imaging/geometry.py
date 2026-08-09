import cv2
import numpy as np


def resize(
    image: np.ndarray, size: tuple[int, int], interpolation: int = cv2.INTER_LANCZOS4
) -> np.ndarray:
    return cv2.resize(image, size, interpolation=interpolation)


def rotate(image: np.ndarray, degrees: float) -> np.ndarray:
    h, w = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((w / 2, h / 2), degrees, 1)
    return cv2.warpAffine(
        image, matrix, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT
    )


def crop(image: np.ndarray, bounds: tuple[int, int, int, int]) -> np.ndarray:
    x, y, w, h = bounds
    if min(x, y, w, h) < 0 or x + w > image.shape[1] or y + h > image.shape[0]:
        raise ValueError("crop is outside image")
    return image[y : y + h, x : x + w].copy()
