# Architecture Overview

R001 is organized as a layered configuration infrastructure package.

## Layers

- Fields: immutable field metadata.
- Schema: immutable schema definition and field registration.
- Sources: raw configuration discovery and loading.
- Registry: ordered source registration and source loading coordination.
- Merge: deterministic source precedence.
- Validation: schema correctness, defaults, unknown fields, and type checks.
- Runtime: immutable application-facing configuration access.
- Diagnostics: structural summaries and secret redaction.
- Loader: high-level orchestration across the lower layers.

## Boundary Rules

The loader orchestrates. Sources retrieve raw data. Merge owns precedence.
Validation owns correctness. Runtime owns access. Diagnostics own presentation.

R001 must not depend on downstream repositories or implement HTTP, exchange,
market-data, dataset, trading, or strategy behavior.

## Status

This document does not approve or freeze R001. The repository remains
unapproved, API-unfrozen, architecture-unfrozen, and not in Release Phase.
