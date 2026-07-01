"""Very small sentence segmentation shared across languages."""

from __future__ import annotations

import re

# Split on CJK and ASCII sentence terminators, keeping content only.
_SENTENCE_SPLIT = re.compile(r"[。！？!?\n]+|(?<=[.])\s+")


def split_sentences(text: str) -> list[str]:
    """Split ``text`` into trimmed, non-empty sentence-like chunks."""
    parts = _SENTENCE_SPLIT.split(text)
    return [p.strip() for p in parts if p and p.strip()]
