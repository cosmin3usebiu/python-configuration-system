# API Reference

This document summarizes the current public API disposition for R001. It is
documentation only and does not freeze the API.

## Status

- R001 is not approved.
- R001 architecture is not frozen.
- R001 API is not frozen.
- R001 is not in Release Phase.

## Stable Public API Candidates

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

## Public But Deferred

- `ConfigProfile`

`ConfigProfile` is currently public profile metadata. Profile inheritance and
profile-specific file behavior are not implemented or frozen.

## Loader Behavior

`ConfigLoader.resolve()` coordinates source loading, override precedence,
merge, validation, and runtime projection. It raises `ProfileResolutionError`
for unknown profiles and unsupported inheritance. It raises `ValidationError`
when validation contains error-severity issues.
