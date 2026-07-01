"""Language detection, segmentation and text normalization."""

from .detector import detect_language
from .normalization import normalize_text
from .segmentation import split_sentences

__all__ = ["detect_language", "normalize_text", "split_sentences"]
