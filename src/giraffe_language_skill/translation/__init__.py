"""Translation providers and the provider interface.

The service ships with a deterministic ``mock`` provider (default, used by
tests and local smoke) and a real ``ctranslate2`` provider that is enabled by
configuration and loaded lazily so its optional dependencies never break the
API when absent.
"""

from .base import TranslationProvider, TranslationResult, get_translation_provider

__all__ = ["TranslationProvider", "TranslationResult", "get_translation_provider"]
