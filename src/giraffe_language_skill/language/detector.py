"""Heuristic, dependency-free language detection.

We deliberately avoid external language-detection libraries and model
downloads. The heuristic distinguishes the languages this MVP supports:
Chinese (zh), Japanese (ja) and English (en). It is intentionally simple and
returns a confidence so callers can raise ``LANGUAGE_DETECTION_LOW_CONFIDENCE``
when appropriate.
"""

from __future__ import annotations

from ..schemas.common import LanguageDetection


def _char_counts(text: str) -> dict[str, int]:
    counts = {"han": 0, "kana": 0, "latin": 0}
    for ch in text:
        code = ord(ch)
        if 0x3040 <= code <= 0x30FF:  # hiragana + katakana
            counts["kana"] += 1
        elif 0x4E00 <= code <= 0x9FFF:  # CJK unified ideographs (han)
            counts["han"] += 1
        elif ("a" <= ch <= "z") or ("A" <= ch <= "Z"):
            counts["latin"] += 1
    return counts


def detect_language(text: str, declared: str = "auto") -> LanguageDetection:
    """Detect the language of ``text``.

    If ``declared`` is an explicit language (not ``auto``/empty) it is trusted
    with high confidence.
    """
    if declared and declared != "auto":
        return LanguageDetection(detected=declared, confidence=0.99)

    counts = _char_counts(text)
    han, kana, latin = counts["han"], counts["kana"], counts["latin"]

    # Presence of kana is a strong, unambiguous signal for Japanese.
    if kana > 0:
        confidence = min(0.99, 0.8 + 0.02 * kana)
        return LanguageDetection(detected="ja", confidence=round(confidence, 2))

    if han > 0:
        # Han characters without kana → treat as Chinese.
        total = han + latin
        confidence = 0.9 if total == 0 else min(0.99, 0.6 + 0.38 * (han / total))
        return LanguageDetection(detected="zh", confidence=round(confidence, 2))

    if latin > 0:
        return LanguageDetection(detected="en", confidence=0.9)

    # No script signal at all (digits/punctuation only) — low confidence.
    return LanguageDetection(detected="en", confidence=0.3)
