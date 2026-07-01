"""Glossary-driven phrase substitution and term lookup."""

from __future__ import annotations

from .loader import Glossary, get_glossary


class GlossaryMatcher:
    """Apply glossary substitutions for translation post-processing and for
    structured field normalization.
    """

    def __init__(self, glossary: Glossary | None = None) -> None:
        self.glossary = glossary or get_glossary()

    @property
    def version(self) -> str:
        return self.glossary.version

    def substitute(self, text: str, source_language: str, target_language: str) -> str:
        """Replace every glossary source phrase in ``text`` with its target.

        Longest phrases are substituted first so compound terms win over their
        parts.
        """
        result = text
        for source, target in self.glossary.sorted_items(source_language, target_language):
            if source and source in result:
                result = result.replace(source, target)
        return result

    def lookup(self, phrase: str, source_language: str, target_language: str) -> str | None:
        """Return the glossary translation of an exact phrase, if present."""
        return self.glossary.direction(source_language, target_language).get(phrase)

    def contains_source_term(self, text: str, term: str, source_language: str,
                             target_language: str = "en") -> bool:
        """True if ``term`` (a glossary source key) occurs in ``text``."""
        return term in self.glossary.direction(source_language, target_language) and term in text
