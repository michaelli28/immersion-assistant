from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Iterable, List, Tuple

import pytesseract
from PIL import Image

from immersion.config import OCRConfig

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class OCRSpan:
    text: str
    bbox: Tuple[int, int, int, int]
    confidence: float


class OCRProcessor:
    """Execute OCR over captured screen regions."""

    def __init__(self, config: OCRConfig) -> None:
        self.config = config

    def detect(self, image: Image.Image) -> List[OCRSpan]:
        languages = "+".join(self.config.languages)
        logger.debug("Running OCR with languages=%s", languages)
        data = pytesseract.image_to_data(image, lang=languages, output_type="dict")

        spans: List[OCRSpan] = []
        n = len(data.get("text", []))
        for idx in range(n):
            text = data["text"][idx].strip()
            if not text:
                continue
            conf = float(data["conf"][idx]) / 100.0
            if conf < self.config.confidence_threshold:
                continue
            bbox = (
                int(data["left"][idx]),
                int(data["top"][idx]),
                int(data["width"][idx]),
                int(data["height"][idx]),
            )
            spans.append(OCRSpan(text=text, bbox=bbox, confidence=conf))
        logger.info("OCR produced %d spans", len(spans))
        return spans

    def batched_detect(self, images: Iterable[Image.Image]) -> List[List[OCRSpan]]:
        return [self.detect(image) for image in images]
