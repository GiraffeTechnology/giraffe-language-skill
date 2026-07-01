"""Deterministic canonical-English -> target-language rewrite rules.

These ordered regex rules handle the reordering and unit/phrase conversions
that a plain glossary substitution cannot (e.g. English "to Tokyo within 45
days" -> Chinese "45 天内交东京"). Rules run before glossary substitution; the
glossary then fills in any remaining known phrases. This keeps outbound
rendering fully deterministic and offline for the mock provider.
"""

from __future__ import annotations

import re

# English city -> localized city names.
_CITY_ZH = {"Tokyo": "东京", "Osaka": "大阪"}
_CITY_JA = {"Tokyo": "東京", "Osaka": "大阪"}


def _zh_delivery(match: re.Match[str]) -> str:
    city = _CITY_ZH.get(match.group(1), match.group(1))
    return f"{match.group(2)} 天内交{city}"


def _ja_delivery(match: re.Match[str]) -> str:
    city = _CITY_JA.get(match.group(1), match.group(1))
    return f"{match.group(2)}日以内に{city}へ納品"


# Each entry: (compiled pattern, replacement str or callable). Order matters.
RULES: dict[str, list[tuple[re.Pattern[str], object]]] = {
    "zh": [
        (re.compile(r"RFQ ready for approval:\s*", re.IGNORECASE), "RFQ 已准备好审批："),
        (re.compile(r"high-quality\s+plaid\s+shirts", re.IGNORECASE), "高品质格子衬衫"),
        (
            re.compile(r"to\s+(Tokyo|Osaka)\s+within\s+(\d+)\s+days", re.IGNORECASE),
            _zh_delivery,
        ),
        (re.compile(r"(\d+)\s*pcs\b", re.IGNORECASE), r"\1 件"),
        (re.compile(r"\bTwo\b", re.IGNORECASE), "已有 2 份"),
        (re.compile(r"\s+are\s+", re.IGNORECASE), ""),
    ],
    "ja": [
        (re.compile(r"RFQ ready for approval:\s*", re.IGNORECASE), "RFQ は承認待ちです："),
        (
            re.compile(r"to\s+(Tokyo|Osaka)\s+within\s+(\d+)\s+days", re.IGNORECASE),
            _ja_delivery,
        ),
        (re.compile(r"(\d+)\s*pcs\b", re.IGNORECASE), r"\1枚"),
    ],
}
