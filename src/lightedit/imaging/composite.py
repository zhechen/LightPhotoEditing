import numpy as np


def blend_rgb(base: np.ndarray, top: np.ndarray, mode: str) -> np.ndarray:
    b, t = base.astype(np.float32) / 255, top.astype(np.float32) / 255
    modes = {
        "normal": t,
        "multiply": b * t,
        "screen": 1 - (1 - b) * (1 - t),
        "overlay": np.where(b <= 0.5, 2 * b * t, 1 - 2 * (1 - b) * (1 - t)),
    }
    if mode.lower() not in modes:
        raise ValueError(f"unsupported blend mode: {mode}")
    return np.clip(modes[mode.lower()] * 255 + 0.5, 0, 255).astype(np.uint8)


def composite_layers(layers: list, shape: tuple[int, int]) -> np.ndarray:
    out = np.zeros((*shape, 4), dtype=np.uint8)
    for layer in layers:
        if not layer.visible:
            continue
        src = layer.pixels
        alpha = src[..., 3:4].astype(np.float32) / 255 * layer.opacity
        if layer.mask is not None:
            alpha *= layer.mask[..., None].astype(np.float32) / 255
        dst_a = out[..., 3:4].astype(np.float32) / 255
        source_over = alpha + dst_a * (1 - alpha)
        blended = blend_rgb(out[..., :3], src[..., :3], layer.blend_mode).astype(np.float32)
        premul = blended * alpha + out[..., :3].astype(np.float32) * dst_a * (1 - alpha)
        out[..., :3] = np.divide(
            premul, source_over, out=np.zeros_like(premul), where=source_over > 0
        )
        out[..., 3:4] = np.clip(source_over * 255 + 0.5, 0, 255)
    return out
