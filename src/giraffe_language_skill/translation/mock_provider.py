"""Deterministic mock translation provider.

Uses glossary phrase substitution (longest-first) plus light punctuation and
spacing cleanup to produce a stable, network-free "translation". It exists so
tests and local API smoke runs behave deterministically without downloading
any model weights.
"""

from __future__ import annotations

import re

from ..glossary import GlossaryMatcher
from ..language.detector import detect_language
from ..schemas.common import Warning, WarningCode
from .base import TranslationProvider, TranslationResult

_CJK_SPACE = re.compile(r"(?<=[぀-ヿ一-鿿])\s+(?=[぀-ヿ一-鿿])")


class MockTranslationProvider(TranslationProvider):
    name = "mock"

    def __init__(self, glossary: GlossaryMatcher | None = None) -> None:
        self.glossary = glossary or GlossaryMatcher()

    def translate(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        domain_hint: str | None = None,
    ) -> TranslationResult:
        warnings: list[Warning] = []

        src = source_language
        if not src or src == "auto":
            src = detect_language(source_text).detected

        if not self.supports_pair(src, target_language) and src != target_language:
            warnings.append(
                Warning(
                    code=WarningCode.UNSUPPORTED_LANGUAGE_PAIR,
                    message=f"No glossary/model for {src}-{target_language}; "
                    "returning best-effort substitution.",
                )
            )

        text = self.glossary.substitute(source_text, src, target_language)

        if target_language == "en":
            # Fold CJK punctuation into ASCII for readable canonical English.
            text = text.replace("，", ", ").replace("。", ". ").replace("、", ", ")
            text = re.sub(r"\s+", " ", text).strip()
        else:
            # Target is a CJK language: drop spaces between CJK characters.
            text = _CJK_SPACE.sub("", text)

        return TranslationResult(
            translated_text=text, provider=self.name, model="mock", warnings=warnings
        )
