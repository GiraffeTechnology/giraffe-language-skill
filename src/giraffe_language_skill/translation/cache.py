"""Tiny in-memory translation cache.

Deterministic and process-local. Enabled via
``GIRAFFE_TRANSLATION_CACHE_ENABLED``. This is intentionally simple — no TTL,
bounded size with FIFO eviction — because translations here are deterministic
for a given (provider, model, direction, text).
"""

from __future__ import annotations

from collections import OrderedDict


class TranslationCache:
    def __init__(self, max_size: int = 2048, enabled: bool = True) -> None:
        self.enabled = enabled
        self.max_size = max_size
        self._store: OrderedDict[tuple[str, str, str, str], str] = OrderedDict()

    def get(self, key: tuple[str, str, str, str]) -> str | None:
        if not self.enabled:
            return None
        value = self._store.get(key)
        if value is not None:
            self._store.move_to_end(key)
        return value

    def set(self, key: tuple[str, str, str, str], value: str) -> None:
        if not self.enabled:
            return
        self._store[key] = value
        self._store.move_to_end(key)
        while len(self._store) > self.max_size:
            self._store.popitem(last=False)

    def clear(self) -> None:
        self._store.clear()
