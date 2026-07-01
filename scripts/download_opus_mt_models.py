#!/usr/bin/env python3
"""Download Helsinki-NLP OPUS-MT / Marian models for the supported pairs.

Model weights are NOT bundled with this repository and are governed by their
upstream licenses (see THIRD_PARTY_NOTICES.md). This script only *downloads*
them locally for later conversion to CTranslate2.

It is never run during tests. Requires the optional ``ctranslate2`` dependency
group (which pulls in ``transformers``)::

    uv pip install -e ".[ctranslate2]"
    python scripts/download_opus_mt_models.py --pairs zh-en en-zh

Downloaded HF snapshots land in ``models/hf/<pair>``; run
``convert_models_to_ctranslate2.py`` next.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Helsinki-NLP OPUS-MT model ids per language pair.
OPUS_MT_MODELS: dict[str, str] = {
    "zh-en": "Helsinki-NLP/opus-mt-zh-en",
    "ja-en": "Helsinki-NLP/opus-mt-ja-en",
    "en-zh": "Helsinki-NLP/opus-mt-en-zh",
    "en-ja": "Helsinki-NLP/opus-mt-en-jap",
}

DEFAULT_PAIRS = list(OPUS_MT_MODELS)


def download_pair(pair: str, out_root: Path) -> Path:
    try:
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer  # type: ignore
    except ImportError as exc:  # pragma: no cover - script-only path
        raise SystemExit(
            "transformers is required. Install with: uv pip install -e '.[ctranslate2]'"
        ) from exc

    model_id = OPUS_MT_MODELS[pair]
    target = out_root / "hf" / pair
    target.mkdir(parents=True, exist_ok=True)
    print(f"[download] {pair} <- {model_id} -> {target}")
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    tokenizer.save_pretrained(target)
    model.save_pretrained(target)
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pairs", nargs="+", default=DEFAULT_PAIRS,
        choices=DEFAULT_PAIRS, help="Language pairs to download.",
    )
    parser.add_argument(
        "--out", default="./models", help="Root output directory (default ./models).",
    )
    args = parser.parse_args(argv)

    out_root = Path(args.out)
    for pair in args.pairs:
        download_pair(pair, out_root)
    print("[done] Downloaded pairs:", ", ".join(args.pairs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
