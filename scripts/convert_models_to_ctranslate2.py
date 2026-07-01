#!/usr/bin/env python3
"""Convert downloaded OPUS-MT / Marian models to the CTranslate2 format.

Reads the HuggingFace snapshots produced by ``download_opus_mt_models.py`` from
``models/hf/<pair>`` and writes CTranslate2 model directories to
``models/<pair>`` (which the runtime CTranslate2 provider then loads).

Never run during tests. Requires the optional ``ctranslate2`` dependency group::

    uv pip install -e ".[ctranslate2]"
    python scripts/convert_models_to_ctranslate2.py --pairs zh-en en-zh
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

DEFAULT_PAIRS = ["zh-en", "ja-en", "en-zh", "en-ja"]


def convert_pair(pair: str, root: Path, quantization: str) -> Path:
    try:
        from ctranslate2.converters import TransformersConverter  # type: ignore
    except ImportError as exc:  # pragma: no cover - script-only path
        raise SystemExit(
            "ctranslate2 is required. Install with: uv pip install -e '.[ctranslate2]'"
        ) from exc

    hf_dir = root / "hf" / pair
    if not hf_dir.is_dir():
        raise SystemExit(f"Missing HF snapshot {hf_dir}; run download_opus_mt_models.py first.")

    out_dir = root / pair
    print(f"[convert] {hf_dir} -> {out_dir} (quantization={quantization})")
    converter = TransformersConverter(str(hf_dir))
    converter.convert(str(out_dir), quantization=quantization, force=True)

    # OPUS-MT SentencePiece models are needed at runtime; copy if present.
    for spm in ("source.spm", "target.spm"):
        src = hf_dir / spm
        if src.exists():
            shutil.copy2(src, out_dir / spm)
    return out_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pairs", nargs="+", default=DEFAULT_PAIRS, choices=DEFAULT_PAIRS)
    parser.add_argument("--root", default="./models", help="Model root directory.")
    parser.add_argument(
        "--quantization", default="int8",
        help="CTranslate2 quantization / compute type (e.g. int8, int8_float16, float16).",
    )
    args = parser.parse_args(argv)

    for pair in args.pairs:
        convert_pair(pair, Path(args.root), args.quantization)
    print("[done] Converted pairs:", ", ".join(args.pairs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
