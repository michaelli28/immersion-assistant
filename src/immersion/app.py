from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from typing import List

from immersion.config import ImmersionConfig
from immersion.language import to_pinyin, to_tone_colors
from immersion.logging_utils import configure_logging
from immersion.pipeline.ocr import OCRProcessor
from immersion.pipeline.screen_capture import ScreenCapture
from immersion.pipeline.translation import TranslationPipeline
from immersion.ui.overlay_model import build_overlay, OverlaySpan

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ImmersionState:
    overlay_spans: List[OverlaySpan]
    last_updated: float


class ImmersionApp:
    """Main application entry point coordinating the living pipeline."""

    def __init__(self, config: ImmersionConfig | None = None) -> None:
        configure_logging()
        self.config = config or ImmersionConfig.load()
        self.screen = ScreenCapture()
        self.ocr = OCRProcessor(self.config.ocr)
        self.translation = TranslationPipeline(self.config.translation)
        self.translation.load_glossary(self.config.glossary)

        self.state = ImmersionState(overlay_spans=[], last_updated=time.time())
        self._stop = threading.Event()

    def start(self, interval: float = 2.0) -> None:
        """Start the polling loop in the current thread."""
        logger.info("Starting immersion loop interval=%ss", interval)
        while not self._stop.is_set():
            try:
                self._tick()
            except Exception:  # pragma: no cover - defensive logging
                logger.exception("Pipeline tick failed.")
            finally:
                time.sleep(interval)

    def stop(self) -> None:
        self._stop.set()

    def _tick(self) -> None:
        frame = self.screen.capture_fullscreen()
        spans = self.ocr.detect(frame.image)
        translations = self.translation.translate_batch([span.text for span in spans])
        overlay = build_overlay(spans, translations, to_pinyin, to_tone_colors)
        self.state = ImmersionState(overlay_spans=overlay, last_updated=time.time())
        logger.debug("Immersion state updated with %d overlay spans", len(overlay))


def run() -> None:
    app = ImmersionApp()
    app.start()


if __name__ == "__main__":
    run()
