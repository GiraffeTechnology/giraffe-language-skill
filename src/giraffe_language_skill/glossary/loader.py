"""Load and cache the Giraffe trade glossary from YAML."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import yaml

from ..config import get_settings

# Supported translation directions kept as glossary sections.
DIRECTIONS = ("zh_en", "ja_en", "en_zh", "en_ja")


@dataclass
class Glossary:
    """In-memory glossary keyed by translation direction.

    ``maps[direction]`` is an ordered dict-like mapping of source phrase to
    target phrase. Callers should match longer phrases first; use
    :meth:`sorted_items` for that.
    """

    version: str = "unknown"
    maps: dict[str, dict[str, str]] = field(default_factory=dict)

    def direction(self, source_language: str, target_language: str) -> dict[str, str]:
        key = f"{source_language}_{target_language}"
        return self.maps.get(key, {})

    def sorted_items(self, source_language: str, target_language: str) -> list[tuple[str, str]]:
        """Return (source, target) pairs sorted by descending source length.

        Longest-first ordering ensures compound terms such as ``格子衬衫`` win
        over their component parts ``格子`` / ``衬衫`` during substitution.
        """
        items = self.direction(source_language, target_language).items()
        return sorted(items, key=lambda kv: len(kv[0]), reverse=True)


def load_glossary(path: str | Path | None = None) -> Glossary:
    """Load a glossary from ``path`` (defaults to the configured path).

    Never raises on a missing/invalid file — returns an empty glossary so the
    caller can surface a ``GLOSSARY_LOAD_FAILED`` warning instead of a crash.
    """
    if path is None:
        path = get_settings().resolved_glossary_path
    path = Path(path)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except (OSError, yaml.YAMLError):
        return Glossary()

    version = str(raw.get("version", "unknown"))
    maps: dict[str, dict[str, str]] = {}
    for direction in DIRECTIONS:
        section = raw.get(direction) or {}
        # Force string keys/values; YAML may parse bare tokens as non-strings.
        maps[direction] = {str(k): str(v) for k, v in section.items()}
    return Glossary(version=version, maps=maps)


@lru_cache
def get_glossary() -> Glossary:
    """Return a cached glossary loaded from the configured path."""
    return load_glossary()
