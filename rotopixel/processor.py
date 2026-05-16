from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import cv2
import imageio.v2 as imageio
import imageio.v3 as iio
import numpy as np

from .palettes import get_palette

ProgressCallback = Callable[[int, int], None]


@dataclass(frozen=True)
class RotoscopeSettings:
    palette: str = "Arcade Ink"
    max_width: int = 640
    pixel_size: int = 4
    color_levels: int = 6
    edge_low: int = 64
    edge_high: int = 132
    edge_strength: float = 0.85
    line_thickness: int = 1
    fps_limit: int = 18
    frame_limit: int | None = None


def process_image(frame_rgb: np.ndarray, settings: RotoscopeSettings) -> np.ndarray:
    """Convert a single RGB frame to a stable rotoscoped pixel-art look."""
    frame = _ensure_rgb(frame_rgb)
    frame = _resize_to_max_width(frame, settings.max_width)

    smoothed = cv2.bilateralFilter(frame, d=7, sigmaColor=58, sigmaSpace=58)
    colorized = _apply_palette(smoothed, settings.palette, settings.color_levels)
    colorized = _pixelate(colorized, settings.pixel_size)

    edges = _edge_mask(smoothed, settings)
    edges = _pixelate(edges, max(1, settings.pixel_size // 2))
    return _ink_edges(colorized, edges, settings.edge_strength)


def process_video(
    input_path: str | Path,
    output_path: str | Path,
    settings: RotoscopeSettings,
    progress: ProgressCallback | None = None,
) -> dict[str, float | int | str]:
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    meta = iio.immeta(input_path)
    source_fps = float(meta.get("fps") or 24)
    target_fps = min(source_fps, settings.fps_limit) if settings.fps_limit else source_fps
    frame_stride = max(1, round(source_fps / target_fps))
    total_frames = _safe_frame_total(meta.get("nframes"))
    expected_frames = _expected_frame_count(total_frames, frame_stride, settings.frame_limit)

    processed_count = 0
    with imageio_writer(output_path, fps=target_fps) as writer:
        for index, frame in enumerate(iio.imiter(input_path)):
            if index % frame_stride != 0:
                continue
            if settings.frame_limit is not None and processed_count >= settings.frame_limit:
                break
            styled = process_image(frame, settings)
            writer.write(styled)
            processed_count += 1
            if progress:
                progress(processed_count, expected_frames)

    return {
        "source_fps": source_fps,
        "output_fps": target_fps,
        "frames": processed_count,
        "path": str(output_path),
    }


def sample_frame(input_path: str | Path, at_second: float, settings: RotoscopeSettings) -> np.ndarray:
    frame = _read_frame_at(input_path, at_second)
    return process_image(frame, settings)


class imageio_writer:
    def __init__(self, path: Path, fps: float) -> None:
        self.path = path
        self.fps = fps
        self._writer = None

    def __enter__(self) -> "imageio_writer":
        self._writer = imageio.get_writer(
            self.path,
            fps=self.fps,
            codec="libx264",
            quality=8,
            macro_block_size=None,
        )
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._writer is not None:
            self._writer.close()

    def write(self, frame_rgb: np.ndarray) -> None:
        if self._writer is None:
            raise RuntimeError("writer is not open")
        self._writer.append_data(frame_rgb)


def _ensure_rgb(frame: np.ndarray) -> np.ndarray:
    if frame.ndim == 2:
        return cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
    if frame.shape[2] == 4:
        return cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
    return frame[:, :, :3].astype(np.uint8, copy=False)


def _resize_to_max_width(frame: np.ndarray, max_width: int) -> np.ndarray:
    height, width = frame.shape[:2]
    if width <= max_width:
        return frame
    scale = max_width / width
    target_size = (max_width, max(1, round(height * scale)))
    return cv2.resize(frame, target_size, interpolation=cv2.INTER_AREA)


def _pixelate(frame: np.ndarray, block_size: int) -> np.ndarray:
    if block_size <= 1:
        return frame
    height, width = frame.shape[:2]
    small_size = (max(1, width // block_size), max(1, height // block_size))
    small = cv2.resize(frame, small_size, interpolation=cv2.INTER_AREA)
    return cv2.resize(small, (width, height), interpolation=cv2.INTER_NEAREST)


def _apply_palette(frame: np.ndarray, palette_name: str, levels: int) -> np.ndarray:
    palette = get_palette(palette_name)
    if palette is None:
        return _stable_posterize(frame, levels)

    flat = frame.reshape(-1, 3).astype(np.int16)
    palette_i16 = palette.astype(np.int16)
    distances = np.sum((flat[:, None, :] - palette_i16[None, :, :]) ** 2, axis=2)
    nearest = np.argmin(distances, axis=1)
    return palette[nearest].reshape(frame.shape)


def _stable_posterize(frame: np.ndarray, levels: int) -> np.ndarray:
    levels = max(2, min(16, levels))
    step = 255 / (levels - 1)
    return (np.round(frame.astype(np.float32) / step) * step).clip(0, 255).astype(np.uint8)


def _edge_mask(frame: np.ndarray, settings: RotoscopeSettings) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(gray, settings.edge_low, settings.edge_high)
    if settings.line_thickness > 1:
        kernel = np.ones((settings.line_thickness, settings.line_thickness), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)
    return edges


def _ink_edges(frame: np.ndarray, edges: np.ndarray, strength: float) -> np.ndarray:
    strength = float(np.clip(strength, 0.0, 1.0))
    ink = np.array([10, 10, 14], dtype=np.float32)
    result = frame.astype(np.float32)
    edge_pixels = edges > 0
    result[edge_pixels] = (result[edge_pixels] * (1.0 - strength)) + (ink * strength)
    return result.clip(0, 255).astype(np.uint8)


def _read_frame_at(input_path: str | Path, at_second: float) -> np.ndarray:
    meta = iio.immeta(input_path)
    fps = float(meta.get("fps") or 24)
    target_index = max(0, round(at_second * fps))
    for index, frame in enumerate(iio.imiter(input_path)):
        if index >= target_index:
            return _ensure_rgb(frame)
    raise ValueError("Could not read a frame from the video")


def _safe_frame_total(value: object) -> int:
    if value is None:
        return 0
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0
    if not np.isfinite(numeric):
        return 0
    return max(0, int(numeric))


def _expected_frame_count(total_frames: int, stride: int, frame_limit: int | None) -> int:
    if total_frames <= 0:
        return frame_limit or 0
    expected = (total_frames + stride - 1) // stride
    if frame_limit is not None:
        expected = min(expected, frame_limit)
    return expected
