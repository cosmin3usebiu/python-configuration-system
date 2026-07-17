# R001 API: python-configuration-system

## Status

This is a recovered draft proposal based on observed implementation evidence.
It does not approve or freeze R001.

R001 approval/freeze state remains unverified. The API is not frozen. Release Phase is not assigned.

Current `__all__` is observed implementation evidence, not a frozen public
contract.

Any future API freeze requires explicit review and approval.

## Observed Public Exports

- `BooleanField`
- `ConfigField`
- `ConfigLoader`
- `ConfigProfile`
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

## Proposed Classification: Core Public API

- `ConfigSchema`
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
- `ConfigSource`
- `EnvConfigSource`
- `FileConfigSource`
- `SourceRegistry`
- `ConfigValidator`
- `ValidationReport`
- `ValidationIssue`
- `ValidationSeverity`
- `ResolvedConfig`
- `DiagnosticsFormatter`
- `ConfigurationSummary`
- `DiagnosticsMode`

## Proposed Classification: Public But Requires Review

- `ConfigLoader`
- `ConfigProfile`
- `SourceDiscovery`
- `SourceMetadata`
- `SourcePayload`
- `ValidationStatistics`

## Proposed Classification: Public Exceptions

- `ConfigurationError`
- `SchemaDefinitionError`
- `SourceRegistrationError`
- `SourceLoadError`
- `ProfileResolutionError`
- `MergeConflictError`
- `ValidationError`

## Known API Caveat

`ConfigLoader.resolve()` is exported but not operational. It raises
`NotImplementedError`.

## API Freeze Status

The API is not frozen.

This file does not approve R001, freeze R001, assign Release Phase, approve any
milestone, or declare release readiness.
