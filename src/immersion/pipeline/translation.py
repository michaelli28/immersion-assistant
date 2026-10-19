from __future__ import annotations

import logging
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, List

from immersion.config import TranslationConfig

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class TranslationResult:
    source: str
    target: str
    provider: str
    glossary_applied: bool


class TranslationProvider:
    """Abstract base for translation providers."""

    name = "base"

    def translate(self, text: str, target_lang: str) -> str:  # pragma: no cover
        raise NotImplementedError


class EchoTranslator(TranslationProvider):
    """Fallback translator used while no engines are wired up."""

    name = "echo"

    def translate(self, text: str, target_lang: str) -> str:
        logger.warning(
            "Using EchoTranslator fallback; returning source text for %r -> %s",
            text,
            target_lang,
        )
        return text


class TranslationPipeline:
    """Coordinate translation with caching and glossary overrides."""

    def __init__(
        self,
        config: TranslationConfig,
        provider: TranslationProvider | None = None,
    ) -> None:
        self.config = config
        self.provider = provider or EchoTranslator()

        maxsize = config.max_cache_size

        @lru_cache(maxsize=maxsize)
        def cache_translate(text: str) -> str:
            logger.debug("Cache miss for translation of %r", text)
            return self.provider.translate(text, self.config.target_language)

        self._cached_translate = cache_translate
        self.glossary = dict[str, str]()

    def load_glossary(self, glossary: dict[str, str]) -> None:
        self.glossary = glossary

    def translate_text(self, text: str) -> TranslationResult:
        applied = False
        translated = self.glossary.get(text)
        if translated:
            applied = True
            logger.debug("Glossary applied for %r", text)
        else:
            translated = self._cached_translate(text)
        return TranslationResult(
            source=text,
            target=translated,
            provider=self.provider.name,
            glossary_applied=applied,
        )

    def translate_batch(self, texts: Iterable[str]) -> List[TranslationResult]:
        return [self.translate_text(text) for text in texts]
