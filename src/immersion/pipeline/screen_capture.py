from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

try:
    import Quartz  # type: ignore
    from Quartz import CoreGraphics
except ImportError:  # pragma: no cover - runtime only
    Quartz = None  # type: ignore
    CoreGraphics = None  # type: ignore

from PIL import Image

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ScreenFrame:
    image: Image.Image
    width: int
    height: int


class ScreenCaptureError(RuntimeError):
    """Raised when we fail to acquire screen content."""


class ScreenCapture:
    """Capture screenshots or app-specific frames for downstream processing."""

    def __init__(self) -> None:
        if Quartz is None:
            logger.warning(
                "Quartz module not available; screen capture will return blank frames."
            )

    def capture_fullscreen(self) -> ScreenFrame:
        """Grab the current desktop image."""
        if Quartz is None or CoreGraphics is None:
            image = Image.new("RGB", (1920, 1080), color="black")
            return ScreenFrame(image=image, width=1920, height=1080)

        display_id = CoreGraphics.CGMainDisplayID()
        region = CoreGraphics.CGRectInfinite
        shot: Optional[CoreGraphics.CGImageRef] = CoreGraphics.CGWindowListCreateImage(
            region,
            CoreGraphics.kCGWindowListOptionOnScreenOnly,
            CoreGraphics.kCGNullWindowID,
            CoreGraphics.kCGWindowImageDefault,
        )
        if shot is None:
            raise ScreenCaptureError("Failed to capture display content.")

        width = CoreGraphics.CGImageGetWidth(shot)
        height = CoreGraphics.CGImageGetHeight(shot)
        bytes_per_row = CoreGraphics.CGImageGetBytesPerRow(shot)
        data_provider = CoreGraphics.CGImageGetDataProvider(shot)
        data = CoreGraphics.CGDataProviderCopyData(data_provider)

        image = Image.frombuffer(
            "RGBA",
            (width, height),
            data,
            "raw",
            "BGRA",
            bytes_per_row,
            1,
        )
        return ScreenFrame(image=image, width=width, height=height)
