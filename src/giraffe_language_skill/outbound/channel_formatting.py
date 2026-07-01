"""Channel-specific outbound formatting.

Kept intentionally light for the MVP: normalizes whitespace and, for CJK
targets, removes stray spaces introduced between CJK characters during
rule/glossary substitution. Real channels (email, WeChat, etc.) can extend this
with signatures, length limits, or markup rules later.
"""

from __future__ import annotations

import re

_CJK_SPACE = re.compile(r"(?<=[぀-ヿ一-鿿])\s+(?=[぀-ヿ一-鿿])")


def format_for_channel(text: str, channel: str | None, target_language: str) -> str:
    """Apply channel/target-language formatting cleanup."""
    result = text
    if target_language in {"zh", "ja"}:
        # Collapse spaces that fall strictly between two CJK characters.
        prev = None
        while prev != result:
            prev = result
            result = _CJK_SPACE.sub("", result)
    # Collapse any accidental double spaces and trim.
    result = re.sub(r"[ \t]{2,}", " ", result).strip()
    return result
