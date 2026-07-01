"""Discovery of locally available translation models.

For the mock provider there are no on-disk models. For the CTranslate2 provider
this scans the configured model directory for converted model folders named by
language pair, e.g. ``models/zh-en``.
"""

from __future__ import annotations

from pathlib import Path

from ..config import Settings, get_settings
from .base import SUPPORTED_PAIRS


def available_language_pairs() -> list[str]:
    """Return the language pairs the service advertises support for."""
    return list(SUPPORTED_PAIRS)


def model_dir_for_pair(settings: Settings, source_language: str, target_language: str) -> Path:
    return Path(settings.translation_model_dir) / f"{source_language}-{target_language}"


def discover_local_models(settings: Settings | None = None) -> list[str]:
    """Return names of language-pair model directories present on disk."""
    settings = settings or get_settings()
    root = Path(settings.translation_model_dir)
    if not root.exists():
        return []
    found = []
    for pair in SUPPORTED_PAIRS:
        if (root / pair).is_dir():
            found.append(pair)
    return found
