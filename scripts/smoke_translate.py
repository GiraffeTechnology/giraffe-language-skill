#!/usr/bin/env python3
"""Smoke-test a translation provider end to end.

Defaults to the ``mock`` provider so it runs with zero setup. To exercise the
real local backend, convert models first (see MODEL_SETUP.md) and run::

    GIRAFFE_TRANSLATION_PROVIDER=ctranslate2 python scripts/smoke_translate.py \\
        --source-language zh --target-language en \\
        --text "询价 5000 件格子衬衫，45天交东京"

Never run during tests.
"""

from __future__ import annotations

import argparse
import sys

from giraffe_language_skill.config import get_settings
from giraffe_language_skill.translation.base import get_translation_provider


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--text", default="询价 5000 件格子衬衫，45天交东京")
    parser.add_argument("--source-language", default="zh")
    parser.add_argument("--target-language", default="en")
    parser.add_argument("--domain-hint", default="trade_rfq")
    args = parser.parse_args(argv)

    settings = get_settings()
    provider = get_translation_provider(settings)
    print(f"[provider] {provider.name}")
    print(f"[models]   {provider.available_models()}")

    result = provider.translate(
        args.text, args.source_language, args.target_language, args.domain_hint
    )
    print(f"[source]     {args.text}")
    print(f"[translated] {result.translated_text}")
    print(f"[meta]       provider={result.provider} model={result.model}")
    for warning in result.warnings:
        print(f"[warning]    {warning.code}: {warning.message}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
