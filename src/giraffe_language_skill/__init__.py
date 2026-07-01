"""Giraffe Language Skill Layer.

A standalone multilingual canonicalization, deterministic extraction, and
local translation service for Giraffe products (AIVAN, abcdYi, giraffe-agent).

The internal business language is canonical English. This package converts
multilingual IM / email / private-domain business messages into canonical
English business packets and renders canonical outbound packets back into a
recipient's target language.
"""

__version__ = "0.1.0"
SERVICE_NAME = "giraffe-language-skill"
