from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from immersion.pipeline.ocr import OCRSpan
from immersion.pipeline.translation import TranslationResult


@dataclass(slots=True)
class OverlaySpan:
    """Representation of translated content to render as an overlay."""

    bbox: Tuple[int, int, int, int]
    source_text: str
    translated_text: str
    pinyin: str | None
    tone_colors: List[str] | None
    glossary_applied: bool


def build_overlay(
    spans: List[OCRSpan],
    translations: List[TranslationResult],
    pinyin_lookup: callable[[str], str | None],
    tone_color_lookup: callable[[str], List[str] | None],
) -> List[OverlaySpan]:
    overlay_spans: List[OverlaySpan] = []

    for span, translation in zip(spans, translations):
        pinyin = pinyin_lookup(translation.target) if translation.target else None
        tone_colors = (
            tone_color_lookup(translation.target) if translation.target else None
        )
        overlay_spans.append(
            OverlaySpan(
                bbox=span.bbox,
                source_text=span.text,
                translated_text=translation.target,
                pinyin=pinyin,
                tone_colors=tone_colors,
                glossary_applied=translation.glossary_applied,
            )
        )
    return overlay_spans
