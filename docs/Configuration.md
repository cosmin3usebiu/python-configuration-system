# Configuration

R001 configuration resolution is schema-driven and source-ordered.

## Resolution Flow

1. Define a `ConfigSchema` with field objects.
2. Register one or more `ConfigSource` implementations.
3. Create a `ConfigLoader`.
4. Call `ConfigLoader.resolve()`.
5. Consume the returned `ResolvedConfig`.

`ConfigLoader.resolve()` loads source payloads through `SourceRegistry`, applies
explicit overrides as highest precedence, merges payloads, validates against the
schema, and returns an immutable runtime object when validation succeeds.

## Profiles

`ConfigProfile` is public but explicitly non-frozen and deferred.

Supported behavior:

- registered profile name validation;
- profile name pass-through to sources.

Unsupported behavior:

- profile inheritance through `extends`;
- profile-specific file behavior through `file_name`;
- profile composition.

## Sources

Built-in sources:

- `EnvConfigSource`
- `FileConfigSource`

`FileConfigSource` supports JSON object files only. YAML and TOML are not
implemented.

## Status

This document does not approve R001, freeze the API, assign Release Phase, or
declare release readiness.
