# Integration: AIVAN / abcdYi / giraffe-agent

`giraffe-language-skill` is **shared infrastructure**. AIVAN, abcdYi, and
giraffe-agent call it over HTTP; they must not re-implement or embed it.

All three products follow the same shape:

```
inbound message
  → POST /v1/inbound/normalize        (raw → canonical EN + field_evidence)
  → POST /v1/structure/<domain>       (canonical → validated structured fields)
  → product DB / workflow / graph
  → POST /v1/outbound/render          (canonical EN → target-language message)
  → OpenClaw / channel
```

## Per-product flow

### AIVAN

```
OpenClaw event
  → /v1/inbound/normalize
  → /v1/structure/rfq
  → AIVAN DB
  → workflow
  → /v1/outbound/render
  → OpenClaw
```

### abcdYi

```
customer customization message
  → /v1/inbound/normalize
  → /v1/structure/apparel-customization
  → abcdYi DB
  → workflow
  → /v1/outbound/render
```

### giraffe-agent

```
business command
  → /v1/inbound/normalize
  → selected structure endpoint (rfq | apparel-customization)
  → execution graph / memory
  → /v1/outbound/render
```

## Environment variables

### AIVAN

```env
AIVAN_LANGUAGE_SKILL_ENABLED=true
AIVAN_LANGUAGE_SKILL_BASE_URL=http://127.0.0.1:8788
AIVAN_LANGUAGE_SKILL_TIMEOUT_SECONDS=10
AIVAN_LANGUAGE_SKILL_FAIL_SOFT=true
```

### abcdYi

```env
ABCDYI_LANGUAGE_SKILL_ENABLED=true
ABCDYI_LANGUAGE_SKILL_BASE_URL=http://127.0.0.1:8788
ABCDYI_LANGUAGE_SKILL_TIMEOUT_SECONDS=10
ABCDYI_LANGUAGE_SKILL_FAIL_SOFT=true
```

### giraffe-agent

```env
GIRAFFE_AGENT_LANGUAGE_SKILL_ENABLED=true
GIRAFFE_AGENT_LANGUAGE_SKILL_BASE_URL=http://127.0.0.1:8788
GIRAFFE_AGENT_LANGUAGE_SKILL_TIMEOUT_SECONDS=10
GIRAFFE_AGENT_LANGUAGE_SKILL_FAIL_SOFT=true
```

## Availability behavior (fail-soft contract)

**If the language skill is available:**
use the normalized canonical packet and structured fields.

**If the language skill is unavailable:**
- preserve the raw message,
- do **not** hallucinate missing fields,
- ask the operator for confirmation, or fall back to a safe deterministic local
  parser only.

## What each product should store

At minimum, persist the full provenance chain returned by the service:

```
raw_text
source_language
canonical_text
translation metadata      (provider, model, glossary_version)
field_evidence
structured <domain> fields
validation_status
missing_fields
```

Storing `field_evidence` and `validation_status` is what lets a product prove
which facts were deterministic vs. glossary-derived, and gate on
`needs_confirmation` before any irreversible or outward-facing action.

## Next integration step (AIVAN)

Implement AIVAN RFQ intake canonicalization in a **separate** AIVAN PR
(`feat: call giraffe-language-skill for RFQ intake canonicalization`). AIVAN
calls `/v1/inbound/normalize`, `/v1/structure/rfq`, and `/v1/outbound/render`,
and stores the fields listed above. Do not implement AIVAN integration inside
this repository.
