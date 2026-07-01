# API Contract

Base URL (local default): `http://127.0.0.1:8788`

All request and response bodies are JSON. The service is a **stateless HTTP
API** — no database, no session state.

Typed warning/error codes that may appear in `warnings[]`:

```
LANGUAGE_DETECTION_LOW_CONFIDENCE
TRANSLATION_PROVIDER_UNAVAILABLE
TRANSLATION_MODEL_MISSING
TRANSLATION_FAILED
STRUCTURING_FAILED
CRITICAL_FIELD_MISSING
UNSUPPORTED_LANGUAGE_PAIR
GLOSSARY_LOAD_FAILED
```

---

## GET /healthz

Response:

```json
{ "ok": true, "service": "giraffe-language-skill", "version": "0.1.0" }
```

---

## GET /v1/models

Response (mock provider):

```json
{
  "provider": "mock",
  "canonical_language": "en",
  "available_language_pairs": ["zh-en", "ja-en", "en-zh", "en-ja"],
  "models": []
}
```

For `ctranslate2` mode, `models` lists the language-pair model directories found
under `GIRAFFE_TRANSLATION_MODEL_DIR`.

---

## POST /v1/inbound/normalize

Request:

```json
{
  "source_text": "询价 5000 件格子衬衫，45天交东京，高品质，请给我一个初步报价",
  "source_language": "auto",
  "canonical_language": "en",
  "domain_hint": "trade_rfq",
  "source_channel": "wechat",
  "conversation_context": { "tenant_id": "default", "sender_role": "buyer" }
}
```

Response:

```json
{
  "raw_text": "…",
  "language": { "detected": "zh", "confidence": 0.98 },
  "canonical_language": "en",
  "canonical_text": "…",
  "field_evidence": {
    "quantity":     { "value": 5000,    "source": "raw_rule",          "span": "5000 件", "confidence": 1.0 },
    "destination":  { "value": "Tokyo", "source": "raw_rule+glossary", "span": "交东京",  "confidence": 1.0 },
    "lead_time_days": { "value": 45,    "source": "raw_rule",          "span": "45天",   "confidence": 1.0 },
    "product_modifier": { "value": ["plaid"], "source": "glossary",    "span": "格子",   "confidence": 0.95 },
    "quality_level":  { "value": "high", "source": "glossary",         "span": "高品质", "confidence": 0.95 }
  },
  "translation": { "provider": "mock", "model": "mock", "glossary_version": "2026-07-01" },
  "warnings": []
}
```

`field_evidence` is produced by **deterministic raw extraction** on the raw
text. It is the source of truth for explicit business facts and is independent
of the translation. `span` preserves the original substring.

---

## POST /v1/translate

Request:

```json
{
  "source_text": "询价 5000 件格子衬衫，45天交东京",
  "source_language": "zh",
  "target_language": "en",
  "domain_hint": "trade_rfq"
}
```

Response:

```json
{
  "source_language": "zh",
  "target_language": "en",
  "translated_text": "…",
  "provider": "mock",
  "model": "mock",
  "warnings": []
}
```

`source_language` may be `"auto"`; it is then detected and echoed back resolved.

---

## POST /v1/structure/rfq

Request:

```json
{
  "raw_text": "询价 5000 件格子衬衫，45天交东京，高品质，请给我一个初步报价",
  "canonical_text": "Inquiry: 5000 pcs high-quality plaid shirts, deliver to Tokyo within 45 days.",
  "field_evidence": {},
  "schema_version": "trade_rfq.v1"
}
```

Response:

```json
{
  "schema": "trade_rfq.v1",
  "validation_status": "valid",
  "structured": {
    "quantity": 5000,
    "quantity_unit": "pcs",
    "product_name": "plaid shirt",
    "product_category": "apparel",
    "product_modifier": ["plaid"],
    "destination": "Tokyo",
    "lead_time_days": 45,
    "quality_level": "high",
    "intent": "preliminary_quote"
  },
  "missing_fields": [],
  "confidence_score": 0.95,
  "field_sources": {
    "quantity": "raw_rule",
    "destination": "raw_rule+glossary",
    "product_name": "canonical_parser+glossary",
    "quality_level": "glossary"
  }
}
```

`validation_status` ∈ `valid | needs_confirmation | blocked | failed`.

Critical RFQ fields:

```
quantity
product_name OR product_category
destination
lead_time_days OR delivery_deadline
```

If a critical field is missing, the response is `needs_confirmation` with the
missing field names in `missing_fields`. Missing data is **never hallucinated**.

`field_evidence` may be supplied from a prior `/v1/inbound/normalize` call; when
present it takes precedence over locally re-extracted evidence.

---

## POST /v1/structure/apparel-customization

Request:

```json
{
  "raw_text": "我要定制 200 件白色纯棉衬衣，男款，东京交货",
  "canonical_text": "I want to customize 200 white pure cotton men's shirts, deliver to Tokyo.",
  "field_evidence": {},
  "schema_version": "apparel_customization.v1"
}
```

Response:

```json
{
  "schema": "apparel_customization.v1",
  "validation_status": "valid",
  "structured": {
    "garment_type": "shirt",
    "fabric": "cotton",
    "color": "white",
    "gender": "men",
    "quantity": 200,
    "delivery_destination": "Tokyo",
    "delivery_deadline": null,
    "customization_notes": []
  },
  "missing_fields": [],
  "confidence_score": 0.94,
  "field_sources": {
    "garment_type": "glossary",
    "fabric": "glossary",
    "color": "glossary",
    "gender": "glossary",
    "quantity": "raw_rule",
    "delivery_destination": "raw_rule+glossary"
  }
}
```

Critical apparel fields: `garment_type`, `quantity`, `delivery_destination`.

---

## POST /v1/outbound/render

Request:

```json
{
  "target_language": "zh",
  "target_channel": "wechat",
  "message_type": "rfq_status_update",
  "canonical_text": "RFQ ready for approval: 5000 pcs high-quality plaid shirts to Tokyo within 45 days. Two supplier inquiry drafts are pending approval.",
  "business_refs": { "rfq_id": "rfq_xxx", "draft_ids": ["draft_1", "draft_2"] },
  "tone": "operator_control"
}
```

Response:

```json
{
  "target_language": "zh",
  "rendered_text": "RFQ 已准备好审批：5000 件高品质格子衬衫 45 天内交东京. 已有 2 份供应商询价草稿等待审批.",
  "provider": "mock",
  "postprocess": ["glossary", "channel_formatting"],
  "approval_required": true
}
```

`approval_required` is `true` when the canonical text (or message type) mentions
approval. Rendering is deterministic: ordered rewrite rules run first, then
glossary substitution, then channel/CJK-spacing cleanup.
