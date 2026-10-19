from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import yaml


DEFAULT_CONFIG_PATH = Path.home() / ".immersion_assistant.yml"


@dataclass(slots=True)
class OCRConfig:
    provider: str = "tesseract"
    languages: List[str] = field(default_factory=lambda: ["eng", "chi_sim"])
    detect_screen_regions: bool = True
    confidence_threshold: float = 0.65


@dataclass(slots=True)
class TranslationConfig:
    provider: str = "local_marian"
    fallback_provider: str | None = None
    target_language: str = "zh-CN"
    max_cache_size: int = 10_000
    show_glossary: bool = True


@dataclass(slots=True)
class OverlayConfig:
    show_pinyin: bool = True
    show_tone_colors: bool = True
    show_tooltips: bool = True
    opacity: float = 0.85
    font_size: int = 14


@dataclass(slots=True)
class ImmersionConfig:
    ocr: OCRConfig = field(default_factory=OCRConfig)
    translation: TranslationConfig = field(default_factory=TranslationConfig)
    overlay: OverlayConfig = field(default_factory=OverlayConfig)
    excluded_apps: List[str] = field(default_factory=list)
    glossary: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path | None = None) -> "ImmersionConfig":
        config_path = path or DEFAULT_CONFIG_PATH
        if not config_path.exists():
            return cls()
        with config_path.open("r", encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        return cls(
            ocr=OCRConfig(**raw.get("ocr", {})),
            translation=TranslationConfig(**raw.get("translation", {})),
            overlay=OverlayConfig(**raw.get("overlay", {})),
            excluded_apps=raw.get("excluded_apps", []),
            glossary=raw.get("glossary", {}),
        )

    def dump(self, path: Path | None = None) -> None:
        config_path = path or DEFAULT_CONFIG_PATH
        with config_path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(
                {
                    "ocr": vars(self.ocr),
                    "translation": vars(self.translation),
                    "overlay": vars(self.overlay),
                    "excluded_apps": self.excluded_apps,
                    "glossary": self.glossary,
                },
                handle,
                allow_unicode=True,
                sort_keys=False,
            )
