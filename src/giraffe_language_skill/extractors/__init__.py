"""Deterministic raw extractors.

These extractors are the source of truth for explicit business facts. They run
directly on the raw multilingual text and never rely on the translation model
to recover quantities, destinations, lead times, quality levels, etc.
"""

from .raw_rules import extract_raw, gather_evidence

__all__ = ["extract_raw", "gather_evidence"]
