# Third-Party Notices

`giraffe-language-skill` is licensed under the Apache License 2.0. It depends on
and interoperates with the third-party components listed below. Each remains
governed by its own license. **Model weights are not distributed with this
repository**; they are downloaded and converted by the user via the scripts in
`scripts/` and remain subject to their upstream licenses.

## Translation runtime & models

### CTranslate2
- Project: https://github.com/OpenNMT/CTranslate2
- License: MIT License
- Use: fast local inference engine for the real translation provider
  (`src/giraffe_language_skill/translation/ctranslate2_provider.py`). Optional
  dependency, not required for the default `mock` provider or the test suite.

### Marian / OPUS-MT
- Marian NMT: https://github.com/marian-nmt/marian — License: MIT License
- OPUS-MT training pipeline: https://github.com/Helsinki-NLP/Opus-MT — License: MIT License
- Use: the model architecture and training toolchain behind the OPUS-MT models.

### Helsinki-NLP OPUS-MT models
- Models: https://huggingface.co/Helsinki-NLP (e.g. `opus-mt-zh-en`,
  `opus-mt-ja-en`, `opus-mt-en-zh`, `opus-mt-en-jap`)
- License: CC-BY-4.0 (per the Helsinki-NLP model cards; verify each model card)
- Use: pretrained translation weights downloaded and converted by
  `scripts/download_opus_mt_models.py` and
  `scripts/convert_models_to_ctranslate2.py`. **Not vendored into this repo.**

### SentencePiece
- Project: https://github.com/google/sentencepiece
- License: Apache License 2.0
- Use: subword tokenization for OPUS-MT models at inference time. Optional
  dependency (`ctranslate2` extra).

### Transformers (Hugging Face)
- Project: https://github.com/huggingface/transformers
- License: Apache License 2.0
- Use: model download and conversion helpers in the setup scripts. Optional
  dependency (`ctranslate2` extra).

## Service framework & core dependencies

### FastAPI
- Project: https://github.com/tiangolo/fastapi
- License: MIT License
- Use: HTTP API framework.

### Starlette
- Project: https://github.com/encode/starlette
- License: BSD 3-Clause License
- Use: ASGI toolkit underlying FastAPI.

### Pydantic / pydantic-settings
- Project: https://github.com/pydantic/pydantic
- License: MIT License
- Use: request/response schemas and environment-driven configuration.

### Uvicorn
- Project: https://github.com/encode/uvicorn
- License: BSD 3-Clause License
- Use: ASGI server for local runs.

### httpx
- Project: https://github.com/encode/httpx
- License: BSD 3-Clause License
- Use: test client transport / HTTP client.

### PyYAML
- Project: https://github.com/yaml/pyyaml
- License: MIT License
- Use: loading the Giraffe trade glossary.

### pytest
- Project: https://github.com/pytest-dev/pytest
- License: MIT License
- Use: test framework (development only).

---

If you add a new dependency or enable a new model, update this file and confirm
the applicable upstream license before distribution.
