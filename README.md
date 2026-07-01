# giraffe-language-skill

**Giraffe Language Skill Layer** — a standalone multilingual canonicalization,
deterministic extraction, and local translation service for Giraffe products
(AIVAN, abcdYi, giraffe-agent).

It converts multilingual IM / email / private-domain business messages into
**canonical English business packets**, applies deterministic extraction and
Giraffe domain-glossary normalization, supports local CTranslate2 + OPUS-MT /
Marian translation, and renders outbound canonical packets back into the
recipient's target language.

## What it is

- a language canonicalization service
- a deterministic extraction layer
- a multilingual structuring service
- a local translation service
- a **pre-LLM skill layer**

## What it is not

- not an agent, chatbot, RFQ execution engine, or pricing engine
- not a GLTG client or an OpenClaw connector
- not a replacement for human approval

This service is **shared infrastructure**. It must not be embedded separately
inside AIVAN, abcdYi, or giraffe-agent.

## Why canonical English exists

The CTYUN AIVAN test showed that a small local LLM (`qwen3.5:0.8b`) cannot
reliably extract structured business fields from non-English input. For example
it dropped `destination = Tokyo`, `product modifier = plaid`, and
`quality level = high` from:

```
询价 5000 件格子衬衫，45天交东京，高品质，请给我一个初步报价
```

Therefore explicit business facts are never extracted by a small LLM. The
architecture is deterministic-first:

```
raw multilingual text
  → deterministic raw extraction        (quantities, cities, lead times…)
  → local translation to canonical EN   (CTranslate2 / OPUS-MT, or mock)
  → glossary normalization              (Giraffe domain terms)
  → domain-specific structuring         (trade RFQ / apparel customization)
  → validation gate                     (valid / needs_confirmation / …)
  → canonical English packet            → product workflow
```

LLMs may be used later only for low-risk normalization, explanation, or draft
polishing — never as the source of truth for explicit business facts.

## Production workflow

```
Inbound IM / Email / Approved Private-Domain Channel
  → OpenClaw Gateway
  → AIVAN / abcdYi / giraffe-agent
  → giraffe-language-skill API
  → canonical English business packet
  → product-specific DB / workflow
  → canonical English outbound packet
  → giraffe-language-skill API
  → target-language rendered message
  → OpenClaw Gateway
  → IM / Email recipient
```

## Install

Requires Python 3.11+. Uses [uv](https://docs.astral.sh/uv/).

```bash
uv venv --python 3.11
uv pip install -e ".[dev]"
```

The default translation provider is `mock`, so the API and the full test suite
run **without any model downloads or network access**.

## Run locally

```bash
cp .env.example .env
uv run python -m giraffe_language_skill.api.main --host 127.0.0.1 --port 8788
```

Then:

```bash
curl -s localhost:8788/healthz
curl -s localhost:8788/v1/models
```

## API examples

Inbound normalize (Chinese RFQ → canonical English + field evidence):

```bash
curl -s localhost:8788/v1/inbound/normalize -H 'content-type: application/json' -d '{
  "source_text": "询价 5000 件格子衬衫，45天交东京，高品质，请给我一个初步报价",
  "source_language": "auto",
  "canonical_language": "en",
  "domain_hint": "trade_rfq"
}'
```

Structure a trade RFQ:

```bash
curl -s localhost:8788/v1/structure/rfq -H 'content-type: application/json' -d '{
  "raw_text": "询价 5000 件格子衬衫，45天交东京，高品质，请给我一个初步报价"
}'
```

Render an outbound Chinese message from canonical English:

```bash
curl -s localhost:8788/v1/outbound/render -H 'content-type: application/json' -d '{
  "target_language": "zh",
  "target_channel": "wechat",
  "message_type": "rfq_status_update",
  "canonical_text": "RFQ ready for approval: 5000 pcs high-quality plaid shirts to Tokyo within 45 days. Two supplier inquiry drafts are pending approval."
}'
```

Full request/response schemas: [docs/API_CONTRACT.md](docs/API_CONTRACT.md).

## Tests

```bash
uv run pytest -q
```

Tests use the deterministic `mock` provider only — no network, no model weights.

## Model setup ⚠️

**Model weights are not bundled with this repository and must not be
committed.** OPUS-MT / Marian / CTranslate2 weights remain governed by their
upstream licenses. Only download + conversion scripts are provided:

- `scripts/download_opus_mt_models.py`
- `scripts/convert_models_to_ctranslate2.py`
- `scripts/smoke_translate.py`

See [docs/MODEL_SETUP.md](docs/MODEL_SETUP.md) to enable the real CTranslate2
backend (`GIRAFFE_TRANSLATION_PROVIDER=ctranslate2`).

## Documentation

- [docs/API_CONTRACT.md](docs/API_CONTRACT.md) — endpoints and schemas
- [docs/MODEL_SETUP.md](docs/MODEL_SETUP.md) — download, convert, enable CTranslate2
- [docs/GLOSSARY_POLICY.md](docs/GLOSSARY_POLICY.md) — glossary versioning and policy
- [docs/INTEGRATION_AIVAN_ABCDYI_GIRAFFE_AGENT.md](docs/INTEGRATION_AIVAN_ABCDYI_GIRAFFE_AGENT.md)
  — how each product calls the service

## License

Apache License 2.0. See [LICENSE](LICENSE) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
