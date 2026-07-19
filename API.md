# R001 API: python-configuration-system

## Status

This document describes the current package-root API disposition after
`ConfigLoader.resolve()` implementation and public export review.

It does not approve R001, freeze R001 architecture, freeze the public API,
assign Release Phase, declare release readiness, validate build artifacts, or
declare package publication readiness.

Current governance status:

- R001 is not approved.
- R001 architecture is not frozen.
- R001 API is not frozen.
- R001 is not in Release Phase.

## Package-Root Public Exports

Stable public API candidates for documentation and later freeze review:

- `BooleanField`
- `ConfigField`
- `ConfigLoader`
- `ConfigSchema`
- `ConfigSource`
- `ConfigValidator`
- `ConfigurationSummary`
- `ConfigurationError`
- `DiagnosticsFormatter`
- `DiagnosticsMode`
- `EnvConfigSource`
- `FloatField`
- `FileConfigSource`
- `IntegerField`
- `ListField`
- `MappingField`
- `MergeConflictError`
- `PathField`
- `ProfileResolutionError`
- `ResolvedConfig`
- `SchemaDefinitionError`
- `SecretField`
- `SourceDiscovery`
- `SourceLoadError`
- `SourceMetadata`
- `SourcePayload`
- `SourceRegistrationError`
- `SourceRegistry`
- `StringField`
- `UNSET`
- `ValidationError`
- `ValidationIssue`
- `ValidationReport`
- `ValidationSeverity`
- `ValidationStatistics`

Public but explicitly non-frozen/deferred:

- `ConfigProfile`

No package-root export is currently classified as an accidental internal-only
export or as a removal candidate before documentation remediation.

## Field and Schema API

The field and schema exports define declarative configuration contracts:

- `ConfigField`
- `StringField`
- `IntegerField`
- `FloatField`
- `BooleanField`
- `ListField`
- `MappingField`
- `SecretField`
- `PathField`
- `UNSET`
- `ConfigSchema`

Field definitions are immutable configuration metadata. `ConfigSchema`
collects named fields and rejects invalid schema definitions such as empty
schema names, duplicate fields, and mapping keys that do not match field names.

## Source API

The source exports define raw configuration acquisition:

- `ConfigSource`
- `EnvConfigSource`
- `FileConfigSource`
- `SourceRegistry`
- `SourceMetadata`
- `SourceDiscovery`
- `SourcePayload`

`ConfigSource` implementations discover available input and load raw values.
They must not own merge policy, validation policy, runtime projection, or
schema-specific correctness decisions.

`SourcePayload`, `SourceMetadata`, and `SourceDiscovery` remain public API
candidates because external source implementations need these objects to
implement the `ConfigSource` contract.

`EnvConfigSource` loads raw values from environment variables using a prefix.
`FileConfigSource` loads JSON object files only.

## Merge, Validation, Runtime, and Diagnostics API

Validation exports:

- `ConfigValidator`
- `ValidationReport`
- `ValidationIssue`
- `ValidationSeverity`

Runtime export:

- `ResolvedConfig`

Diagnostics exports:

- `DiagnosticsFormatter`
- `ConfigurationSummary`
- `DiagnosticsMode`
- `ValidationStatistics`

`ConfigValidator` validates merged values against a `ConfigSchema`, applies
schema defaults, filters unknown fields from validated runtime values, and
records validation issues.

`ResolvedConfig` exposes validated configuration as an immutable runtime object
with mapping access, attribute access, iteration, `get()`, and `require()`.

`DiagnosticsFormatter` presents structural configuration summaries. Diagnostics
must not reveal secret values.

`ValidationStatistics` is a public diagnostics support object. It should be
treated as structural reporting metadata, not as validation policy.

## Loader API

`ConfigLoader` is the high-level orchestration entry point.

Implemented `ConfigLoader.resolve()` behavior:

- Validates requested profile names against registered profiles.
- Raises `ProfileResolutionError` for unknown profiles.
- Raises `ProfileResolutionError` for profile inheritance because inheritance is
  not implemented.
- Loads sources through `SourceRegistry`.
- Passes the resolved profile name to registered sources.
- Adds explicit `overrides` as the highest-precedence source payload.
- Merges source payloads through `ConfigMerger` and `MergeInput`.
- Validates merged values through `ConfigValidator`.
- Raises `ValidationError` when error-severity validation issues exist.
- Returns `ResolvedConfig.from_validation_report(...)` on success.

`ConfigLoader` does not implement source-specific behavior, merge algorithms,
validation rules, runtime access behavior, or diagnostics formatting.

## ConfigProfile

`ConfigProfile` remains exported but is explicitly non-frozen and deferred.

Current supported use:

- Describe a named profile.
- Provide optional descriptive metadata.
- Allow `ConfigLoader.resolve(profile_name=...)` to validate that a requested
  profile exists.

Unsupported behavior:

- Profile inheritance through `extends`.
- Profile-specific file resolution through `file_name`.
- Profile composition.
- Profile-specific source discovery beyond passing the profile name to sources.

Documentation and downstream consumers must not treat `ConfigProfile` semantics
as frozen.

## Public Exception Candidates

Repository-native public exception candidates:

- `ConfigurationError`
- `SchemaDefinitionError`
- `SourceRegistrationError`
- `SourceLoadError`
- `ProfileResolutionError`
- `MergeConflictError`
- `ValidationError`

These exceptions form the current external error contract candidates. Their
future API-freeze status requires explicit review and approval.

## Unsupported and Deferred Behavior

R001 does not currently provide:

- YAML or TOML file loading.
- Remote/cloud/database configuration loading.
- Secret storage.
- Secret value display.
- Configuration reload/watch behavior.
- CLI behavior.
- Profile inheritance.
- Profile-specific file behavior.
- HTTP, exchange, market-data, dataset, trading, or strategy behavior.

## API Freeze Status

The API is not frozen. This document records the current disposition for
documentation remediation and later review only.
