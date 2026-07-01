# Model Setup

## Model weights are not bundled

This repository **does not** contain OPUS-MT / Marian / CTranslate2 model
weights, and they must never be committed. `.gitignore` excludes `models/*`
(except `models/.gitkeep`) and weight file extensions (`*.ct2`, `*.bin`,
`*.safetensors`, `*.onnx`, `*.model`, `*.vocab`).

Model weights remain governed by their upstream licenses — see
[../THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).

The default translation provider is `mock`, so tests and local API smoke run
with **no model downloads and no network access**. You only need the steps below
to enable the real local translation backend.

## Supported pairs

```
zh-en   ja-en   en-zh   en-ja
```

## 1. Install the optional dependency group

```bash
uv pip install -e ".[ctranslate2]"
```

This adds `ctranslate2`, `sentencepiece`, and `transformers`.

## 2. Download OPUS-MT / Marian models

```bash
python scripts/download_opus_mt_models.py --pairs zh-en ja-en en-zh en-ja
```

HuggingFace snapshots are written to `models/hf/<pair>/`.

## 3. Convert to CTranslate2

```bash
python scripts/convert_models_to_ctranslate2.py --pairs zh-en ja-en en-zh en-ja --quantization int8
```

Converted models are written to `models/<pair>/` (the layout the runtime
provider loads). SentencePiece models (`source.spm` / `target.spm`) are copied
alongside for tokenization.

## 4. Enable the CTranslate2 provider

Set in `.env` (or the environment):

```env
GIRAFFE_TRANSLATION_PROVIDER=ctranslate2
GIRAFFE_TRANSLATION_MODEL_DIR=./models
GIRAFFE_TRANSLATION_DEVICE=cpu
GIRAFFE_TRANSLATION_COMPUTE_TYPE=int8
```

`GET /v1/models` will then report `provider: "ctranslate2"` and list the model
directories discovered under `GIRAFFE_TRANSLATION_MODEL_DIR`.

## 5. Smoke test

```bash
GIRAFFE_TRANSLATION_PROVIDER=ctranslate2 \
  python scripts/smoke_translate.py \
  --source-language zh --target-language en \
  --text "询价 5000 件格子衬衫，45天交东京"
```

The same script runs against the default `mock` provider with no arguments.

## Graceful degradation

If the optional dependencies are missing, or a model directory is absent, the
CTranslate2 provider does **not** crash the API. It echoes the source text and
attaches a typed warning (`TRANSLATION_PROVIDER_UNAVAILABLE` or
`TRANSLATION_MODEL_MISSING`) to the response.
