"""Real local translation provider backed by CTranslate2 + OPUS-MT / Marian.

This provider is enabled with ``GIRAFFE_TRANSLATION_PROVIDER=ctranslate2``. It
imports ``ctranslate2`` and a SentencePiece/HF tokenizer lazily so that the API
never crashes when those optional dependencies are absent. Missing dependencies
or missing model directories are reported as typed warnings and the source text
is echoed back, keeping the service responsive.

Model weights are NOT bundled with this repository. See docs/MODEL_SETUP.md and
the scripts/ directory for download + conversion.
"""

from __future__ import annotations

from ..config import Settings, get_settings
from ..schemas.common import Warning, WarningCode
from .base import TranslationProvider, TranslationResult
from .cache import TranslationCache
from .model_registry import discover_local_models, model_dir_for_pair


class CTranslate2Provider(TranslationProvider):
    name = "ctranslate2"

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.cache = TranslationCache(enabled=self.settings.translation_cache_enabled)
        # Lazily-populated per-pair (translator, tokenizer) handles.
        self._loaded: dict[str, tuple[object, object]] = {}

    def available_models(self) -> list[str]:
        return discover_local_models(self.settings)

    # -- lazy dependency + model loading ----------------------------------
    def _load_pair(
        self, source_language: str, target_language: str
    ) -> tuple[object | None, object | None, Warning | None]:
        pair = f"{source_language}-{target_language}"
        if pair in self._loaded:
            translator, tokenizer = self._loaded[pair]
            return translator, tokenizer, None

        try:
            import ctranslate2  # type: ignore
            import sentencepiece  # type: ignore  # noqa: F401
        except ImportError:
            return None, None, Warning(
                code=WarningCode.TRANSLATION_PROVIDER_UNAVAILABLE,
                message="ctranslate2 / sentencepiece not installed; install the "
                "'ctranslate2' optional dependency group.",
            )

        model_path = model_dir_for_pair(self.settings, source_language, target_language)
        if not model_path.is_dir():
            return None, None, Warning(
                code=WarningCode.TRANSLATION_MODEL_MISSING,
                message=f"No converted model at {model_path}. Run the download + "
                "convert scripts first.",
            )

        try:
            translator = ctranslate2.Translator(
                str(model_path),
                device=self.settings.translation_device,
                compute_type=self.settings.translation_compute_type,
            )
            tokenizer = self._load_tokenizer(model_path)
        except Exception as exc:  # noqa: BLE001 - surface any load failure as a warning
            return None, None, Warning(
                code=WarningCode.TRANSLATION_FAILED,
                message=f"Failed to load CTranslate2 model at {model_path}: {exc}",
            )

        self._loaded[pair] = (translator, tokenizer)
        return translator, tokenizer, None

    @staticmethod
    def _load_tokenizer(model_path):  # type: ignore[no-untyped-def]
        """Load a SentencePiece tokenizer from the model directory.

        OPUS-MT conversions typically ship ``source.spm`` / ``target.spm``.
        """
        import sentencepiece as spm  # type: ignore

        source_spm = model_path / "source.spm"
        target_spm = model_path / "target.spm"
        sp_source = spm.SentencePieceProcessor(model_file=str(source_spm))
        sp_target = spm.SentencePieceProcessor(model_file=str(target_spm))
        return (sp_source, sp_target)

    # -- translation ------------------------------------------------------
    def translate(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        domain_hint: str | None = None,
    ) -> TranslationResult:
        warnings: list[Warning] = []
        cache_key = (self.name, source_language, target_language, source_text)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return TranslationResult(cached, self.name, "ctranslate2", warnings)

        translator, tokenizer, load_warning = self._load_pair(source_language, target_language)
        if load_warning is not None:
            # Graceful degradation: echo source text, attach the typed warning.
            warnings.append(load_warning)
            return TranslationResult(source_text, self.name, "unavailable", warnings)

        try:
            sp_source, sp_target = tokenizer  # type: ignore[misc]
            tokens = sp_source.encode(source_text, out_type=str)  # type: ignore[attr-defined]
            results = translator.translate_batch([tokens])  # type: ignore[attr-defined]
            hypothesis = results[0].hypotheses[0]
            translated = sp_target.decode(hypothesis)  # type: ignore[attr-defined]
        except Exception as exc:  # noqa: BLE001
            warnings.append(
                Warning(code=WarningCode.TRANSLATION_FAILED, message=str(exc))
            )
            return TranslationResult(source_text, self.name, "ctranslate2", warnings)

        self.cache.set(cache_key, translated)
        return TranslationResult(translated, self.name, "ctranslate2", warnings)
