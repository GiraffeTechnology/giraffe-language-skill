# giraffe-language-skill — P0 Canonical Language Boundary

`Canonical English` | `Pre-workflow Skill Layer` | `Multilingual Input Normalization` | `Localized Output Rendering` | `Shared Giraffe Infrastructure`

`giraffe-language-skill` is the shared language boundary for Giraffe Technology products.

It converts raw multilingual operator, buyer, supplier, QC, IM, email, and marketplace text into **canonical English business packets** before any product workflow performs extraction, routing, GLTG simulation, Giraffe DB writes, QC test-point generation, decision-packet creation, or outbound draft generation.

This repository is not an optional helper. It is a P0 architecture layer.

---

## P0 Global Rule

```text
Standard English is the only internal working language across Giraffe products.

All raw multilingual input must pass through giraffe-language-skill before product workflow.

After internal work is complete, user-facing output is localized into the target language requested by the user.
```

Any implementation that bypasses this rule is invalid.

---

## Why This Exists

Giraffe products operate across Chinese, English, Japanese, and other trade languages. AIVAN, abcdYi, giraffe-agent, giraffe-db, GLTG, and QC workflows must not each invent their own translation prompts, city aliases, SKU maps, product maps, material maps, or multilingual extraction shortcuts.

Without a shared language boundary, the same raw phrase can produce different product, destination, quality, lead-time, or supplier-routing facts in different repositories.

The solution is a single canonical path:

```text
raw multilingual message
-> language detection
-> canonical English normalization
-> deterministic business-field extraction where safe
-> domain-glossary normalization
-> structured canonical packet
-> validation gate
-> downstream product workflow
-> localized user-facing output
```

---

## What This Repository Owns

`giraffe-language-skill` owns:

```text
language detection
canonical English normalization
multilingual RFQ canonicalization
multilingual QC requirement canonicalization
safe deterministic extraction for explicit fields
Giraffe domain glossary normalization
canonical packet schemas
language metadata
localized output rendering
validation gates for ambiguous input
static guard policy for product repositories
```

---

## What This Repository Does Not Own

It does not own:

```text
AIVAN RFQ execution
GLTG lead-time simulation
giraffe-db persistence
GPM procurement path reasoning
QC visual inspection
OpenClaw channel connectivity
commercial approval
legal responsibility
```

Language normalization happens before those systems run. It does not replace them.

---

## Required Downstream Contract

Every relevant Giraffe product must follow this rule:

```text
if input_language != English:
    call giraffe-language-skill
    require a valid canonical English packet
    block product workflow if canonicalization fails
else:
    local English workflow may continue
```

Downstream products must consume:

```text
canonical_english_text
canonical_business_packet
detected_language
requested_output_language
final_output_language
source_conversation_language
confidence
needs_confirmation
questions
```

Localized output is never the internal source of truth. The canonical English packet is the audit source.

---

## AIVAN Enforcement

AIVAN does not own multilingual RFQ extraction.

For non-English RFQ input:

```text
giraffe-language-skill must normalize raw text into canonical English.
giraffe-language-skill must produce the structured RFQ packet.
AIVAN must not call its requirement LLM with raw non-English business text.
AIVAN must not run deterministic fallback extraction over raw non-English business text.
AIVAN must not infer product, category, destination, material, quality, supplier capability, price, or lead time from raw non-English text.
If language-skill cannot produce a valid packet, AIVAN must block extraction and ask for confirmation.
```

GLTG, supplier routing, Giraffe DB graph writes, and outbound draft creation must not run from raw non-English input.

---

## Prohibited in Product Repositories

Product repositories must not add:

```text
internal RFQ translation prompts
multilingual city alias maps
destination alias maps
product alias maps
SKU alias maps
material alias maps
quality alias maps
supplier alias or capability maps
category keyword maps
raw non-English field extraction paths that bypass giraffe-language-skill
LLM extraction directly from raw non-English business text
```

Those rules belong here, in canonical resolver services, or in Giraffe DB canonical data layers.

---

## Required Tests

Each relevant product repo must include tests proving:

1. Non-English input calls `giraffe-language-skill` before business extraction.
2. Non-English input without a valid canonical packet is blocked.
3. Local LLM does not receive raw non-English business text.
4. Deterministic fallback does not canonicalize raw non-English product, destination, category, material, quality, or supplier information.
5. Final user-facing output is localized into the requested target language.
6. Canonical English internal state is preserved separately from localized output.
7. Static guards fail if product repos add multilingual business-semantic alias maps.

---

## Ecosystem Role

```text
giraffe-language-skill = language boundary
giraffe-db             = private business fact layer
GLTG                   = lead-time simulation layer
GPM                    = procurement graph reasoning layer
AIVAN                  = trade execution worker
giraffe-agent          = open-core orchestration reference
abcdYi / Giraffe-JP    = industry / deployment applications
giraffe-qc-model       = visual QC intelligence
OpenClaw               = channel runtime
```

---

## Final Required Statement

P0 Global Rule Enforced:

```text
Standard English is the only internal working language across Giraffe products.
All raw multilingual input must pass through giraffe-language-skill before product workflow.
After internal work is complete, user-facing output is localized into the target language requested by the user.
```

---

## License

See `LICENSE`.
