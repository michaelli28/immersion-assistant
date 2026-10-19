from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from pypinyin import Style, lazy_pinyin

TONE_COLOR_MAP = {
    1: "#ff6666",
    2: "#ffcc66",
    3: "#66ccff",
    4: "#99ff99",
    5: "#cccccc",
}


def to_pinyin(text: str) -> Optional[str]:
    if not text:
        return None
    syllables = lazy_pinyin(text, style=Style.TONE3, errors="ignore")
    return " ".join(syllables)


def to_tone_colors(text: str) -> Optional[List[str]]:
    if not text:
        return None
    tones: List[str] = []
    for syllable in lazy_pinyin(text, style=Style.TONE3, errors="ignore"):
        tone = 5
        if syllable and syllable[-1].isdigit():
            tone = int(syllable[-1])
        tones.append(TONE_COLOR_MAP.get(tone, TONE_COLOR_MAP[5]))
    return tones


@dataclass(slots=True)
class DictionaryEntry:
    term: str
    pinyin: str
    glosses: List[str]
    measure_words: List[str]


def build_dictionary_entry(term: str, translation: str) -> DictionaryEntry:
    return DictionaryEntry(
        term=term,
        pinyin=to_pinyin(translation) or "",
        glosses=[translation],
        measure_words=[],
    )
