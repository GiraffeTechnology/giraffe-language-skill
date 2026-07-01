# Glossary Policy

The Giraffe trade glossary lives at:

```
src/giraffe_language_skill/glossary/giraffe_trade_glossary.yml
```

Its path is configurable via `GIRAFFE_GLOSSARY_PATH`. If the configured file is
missing, the service falls back to the bundled glossary and (when loading truly
fails) surfaces a `GLOSSARY_LOAD_FAILED` warning rather than crashing.

## Structure

```yaml
version: "2026-07-01"
zh_en: { <chinese phrase>: <english phrase>, ... }
ja_en: { <japanese phrase>: <english phrase>, ... }
en_zh: { <english phrase>: <chinese phrase>, ... }
en_ja: { <english phrase>: <japanese phrase>, ... }
```

Each top-level key is a **translation direction** (`<source>_<target>`).

## Versioning

- `version` is a date string (e.g. `2026-07-01`).
- Bump `version` whenever any entry changes.
- The active version is echoed in every `/v1/inbound/normalize` response under
  `translation.glossary_version`, so downstream products can record exactly
  which glossary normalized a packet.
- Treat the glossary as an auditable artifact: prefer additive changes; when you
  must change an existing mapping, bump the version and note it in the commit.

## Where the glossary participates

The glossary is used in **two** places, by design:

1. **Translation post-processing** — the mock provider and the outbound renderer
   apply glossary substitution (longest phrase first) so domain terms render
   consistently regardless of the underlying model.
2. **Structured field normalization** — the deterministic extractors and domain
   parsers use glossary terms to normalize values (e.g. `格子 → plaid`,
   `交东京 → deliver to Tokyo → destination: Tokyo`).

Longest-match-first ordering guarantees compound terms win over their parts
(`格子衬衫 → plaid shirt` beats `格子 → plaid` + `衬衫 → shirt`).

## How the glossary affects field evidence

When a field value is derived with glossary help, its `source` records the
provenance:

- `raw_rule` — pure deterministic rule (e.g. a quantity like `5000 件`).
- `glossary` — value came from a glossary term (e.g. `product_modifier: plaid`).
- `raw_rule+glossary` — a rule matched a glossary-backed phrase (e.g.
  `交东京 → destination: Tokyo`).
- `canonical_parser+glossary` — composed while parsing canonical English (e.g.
  `product_name: plaid shirt`).

This lets downstream consumers audit whether a fact came from the raw text, the
glossary, or both — and never from a translation model guessing.

## Adding entries

1. Open `giraffe_trade_glossary.yml`.
2. Add the phrase under the correct direction section (`zh_en`, `ja_en`,
   `en_zh`, `en_ja`).
3. For multi-word/compound domain terms, add the full compound too, so it wins
   over component matches.
4. Bump `version`.
5. Add or extend a test if the term participates in extraction/structuring.
6. Keep source keys as literal phrases (quote them in YAML if they could be
   parsed as non-strings).
