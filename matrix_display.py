"""LED matrix display abstraction for SpotiGotchi.

This module provides a tiny API used by the rest of the app:
- create_matrix()
- show_image(matrix, image)

If the `rgbmatrix` dependency is available, images are rendered to a physical RGB
LED matrix. If not, the module gracefully degrades to a no-op backend so the
service can still run for development and setup flows.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from PIL import Image

try:
    from rgbmatrix import RGBMatrix, RGBMatrixOptions  # type: ignore
except ImportError:  # pragma: no cover - hardware dependency not always available
    RGBMatrix = None
    RGBMatrixOptions = None


@dataclass(frozen=True)
class _Config:
    width: int
    height: int
    chain_length: int
    parallel: int
    brightness: int
    hardware_mapping: str
    pwm_bits: int


class _NoopMatrix:
    """Fallback matrix object used when no hardware backend is present."""

    width = 64
    height = 64


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _load_config() -> _Config:
    return _Config(
        width=_env_int("SPOTIGOTCHI_MATRIX_WIDTH", 64),
        height=_env_int("SPOTIGOTCHI_MATRIX_HEIGHT", 64),
        chain_length=_env_int("SPOTIGOTCHI_MATRIX_CHAIN_LENGTH", 1),
        parallel=_env_int("SPOTIGOTCHI_MATRIX_PARALLEL", 1),
        brightness=max(1, min(100, _env_int("SPOTIGOTCHI_MATRIX_BRIGHTNESS", 60))),
        hardware_mapping=os.getenv("SPOTIGOTCHI_MATRIX_HARDWARE_MAPPING", "regular"),
        pwm_bits=max(1, min(11, _env_int("SPOTIGOTCHI_MATRIX_PWM_BITS", 11))),
    )


def create_matrix() -> object:
    """Create a matrix backend.

    Returns an RGBMatrix instance when available, otherwise a lightweight
    fallback object so callers can continue operating without hardware.
    """

    if RGBMatrix is None or RGBMatrixOptions is None:
        print("matrix_display: rgbmatrix not installed; using no-op backend.")
        return _NoopMatrix()

    cfg = _load_config()

    options = RGBMatrixOptions()
    options.cols = cfg.width
    options.rows = cfg.height
    options.chain_length = cfg.chain_length
    options.parallel = cfg.parallel
    options.brightness = cfg.brightness
    options.hardware_mapping = cfg.hardware_mapping
    options.pwm_bits = cfg.pwm_bits

    return RGBMatrix(options=options)


def _prepare_image(image: Image.Image, width: int, height: int) -> Image.Image:
    if image.mode != "RGB":
        image = image.convert("RGB")
    if image.size != (width, height):
        image = image.resize((width, height), Image.NEAREST)
    return image


def show_image(matrix: object, image: Image.Image) -> Optional[Image.Image]:
    """Display an image on the matrix.

    If running without hardware support, this is intentionally a no-op.
    Returns the prepared image for optional debugging/testing.
    """

    width = getattr(matrix, "width", 64)
    height = getattr(matrix, "height", 64)
    prepared = _prepare_image(image, width, height)

    if RGBMatrix is not None and hasattr(matrix, "SetImage"):
        matrix.SetImage(prepared)
        return prepared

    # No-op fallback path.
    return prepared
