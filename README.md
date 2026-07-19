# python-configuration-system

Reusable Python infrastructure for defining, loading, validating, and exposing
application configuration through immutable runtime objects.

R001 is intended to provide configuration infrastructure for higher-level
repositories without depending on those repositories.

## Current Status

R001 has implemented configuration behavior through the loader orchestration
layer, including schemas, fields, sources, source registration, deterministic
merge, validation, runtime access, diagnostics, and minimal
`ConfigLoader.resolve()` orchestration.

Governance status:

- R001 is not approved.
- R001 architecture is not frozen.
- R001 public API is not frozen.
- R001 is not in Release Phase.
- This repository has not been declared release-ready.
- Build, sdist, wheel, publication, and production readiness are not claimed.

Validation evidence exists from prior portfolio consolidation tasks, but
validation evidence does not imply approval, freeze, Release Phase, release
readiness, package publication readiness, or production readiness.

## Implemented Capabilities

- Immutable configuration field definitions.
- Immutable configuration schema definitions.
- Environment variable configuration source.
- JSON file configuration source.
- Source registration and ordered source loading.
- Deterministic merge with source precedence.
- Schema-driven validation.
- Required field validation.
- Unknown field reporting.
- Default value application.
- Type compatibility checks.
- Secret-safe validation issue metadata.
- Immutable runtime configuration access.
- Quiet and verbose diagnostic summaries.
- Minimal high-level `ConfigLoader.resolve()` orchestration.

`ConfigLoader.resolve()` currently coordinates source loading, optional profile
name pass-through, explicit overrides as highest precedence, merge, validation,
and `ResolvedConfig` creation.

## Public API Disposition

The current package-root exports are considered coherent with the implemented
architecture and are candidates for documentation and later API-freeze review.
They are not frozen by this document.

Stable public API candidates:

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

`ConfigProfile` is currently usable as profile metadata. Profile inheritance and
profile-specific file behavior are not implemented by `ConfigLoader.resolve()`
and must not be treated as stable behavior.

## Basic Usage

```python
from python_configuration_system import (
    ConfigLoader,
    ConfigSchema,
    EnvConfigSource,
    IntegerField,
    StringField,
)

schema = ConfigSchema(
    name="service",
    fields=[
        StringField(name="service_name", description="Service name."),
        IntegerField(name="port", description="Port.", default=8080),
    ],
)

loader = ConfigLoader(
    schema=schema,
    sources=[
        EnvConfigSource(prefix="APP_"),
    ],
)

config = loader.resolve(overrides={"service_name": "example"})

service_name = config["service_name"]
port = config.require("port")
```

## Non-Goals

R001 does not implement:

- HTTP communication.
- Exchange integration.
- Market-data acquisition.
- Dataset persistence.
- Trading logic.
- Strategy logic.
- Remote/cloud configuration backends.
- Database-backed configuration.
- Secret storage.
- Secret value display.
- Live reload or file watchers.
- CLI utilities.
- YAML or TOML source support.
- Profile inheritance.
- Profile-specific file loading behavior.

## Repository Layout

- `src/python_configuration_system/`: package implementation.
- `tests/`: behavioral tests.
- `docs/`: supporting documentation.
- `examples/`: usage notes and examples.
- `.github/`: CI workflow.

## Dependency Position

R001 has no runtime package dependencies. Higher-level platform repositories may
consume R001 through its public package exports, but R001 must not depend on
downstream repositories.
