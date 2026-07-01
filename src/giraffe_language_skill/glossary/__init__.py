"""Giraffe domain glossary: loading and phrase matching."""

from .loader import Glossary, get_glossary, load_glossary
from .matcher import GlossaryMatcher

__all__ = ["Glossary", "GlossaryMatcher", "get_glossary", "load_glossary"]
