"""Translation provider interface and factory.

Providers must be swappable behind this interface. Failures are represented as
typed :class:`~giraffe_language_skill.schemas.common.Warning` entries on the
result rather than raised exceptions, so a missing model or absent optional
dependency degrades gracefully instead of crashing the API.
"""

from __future__ import annotations

import abc
from dataclasses import dataclass, field

from ..config import Settings, get_settings
from ..schemas.common import Warning

# Language pairs this service advertises support for.
SUPPORTED_PAIRS = ("zh-en", "ja-en", "en-zh", "en-ja")


@dataclass
class TranslationResult:
    translated_text: str
    provider: str
    model: str
    warnings: list[Warning] = field(default_factory=list)


class TranslationProvider(abc.ABC):
    """Abstract base class for translation backends."""

    name: str = "base"

    @abc.abstractmethod
    def translate(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        domain_hint: str | None = None,
    ) -> TranslationResult:
        """Translate ``source_text`` from source to target language."""

    def available_models(self) -> list[str]:
        """Return identifiers of locally available models (empty for mock)."""
        return []

    @staticmethod
    def supports_pair(source_language: str, target_language: str) -> bool:
        return f"{source_language}-{target_language}" in SUPPORTED_PAIRS


def get_translation_provider(settings: Settings | None = None) -> TranslationProvider:
    """Instantiate the configured translation provider.

    Never raises for a misconfigured or unavailable real backend: falls back to
    a provider that echoes text and attaches a ``TRANSLATION_PROVIDER_UNAVAILABLE``
    warning, keeping the API responsive.
    """
    settings = settings or get_settings()
    provider = (settings.translation_provider or "mock").lower()

    if provider == "mock":
        from .mock_provider import MockTranslationProvider

        return MockTranslationProvider()

    if provider == "ctranslate2":
        from .ctranslate2_provider import CTranslate2Provider

        return CTranslate2Provider(settings)

    # Unknown provider name — degrade to mock so the service still runs.
    from .mock_provider import MockTranslationProvider

    return MockTranslationProvider()
