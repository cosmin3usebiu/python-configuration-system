# R001 Design: python-configuration-system

## Status

This document reflects the current implemented R001 architecture after the
minimal `ConfigLoader.resolve()` implementation.

It does not approve R001, freeze the architecture, freeze the API, assign
Release Phase, declare release readiness, validate build artifacts, or declare
package publication readiness.

Current governance status:

- R001 is not approved.
- R001 architecture is not frozen.
- R001 API is not frozen.
- R001 is not in Release Phase.

## Purpose

R001 provides a reusable Python configuration system with typed schemas, source
loading, deterministic merging, validation, immutable runtime access, and
diagnostic summaries.

## Scope

R001 owns:

- Configuration field metadata.
- Configuration schema definitions.
- Configuration source contracts.
- Environment source loading.
- JSON file source loading.
- Source registration.
- Deterministic merge behavior.
- Validation against schema.
- Default value application.
- Unknown field reporting.
- Secret-safe validation issues and diagnostics.
- Immutable runtime configuration views.
- Diagnostics presentation.
- High-level loader orchestration.

## Non-Goals

R001 does not own:

- HTTP communication.
- Exchange integration.
- Market-data acquisition.
- Dataset persistence.
- Trading logic.
- Strategy logic.
- Credential storage.
- Secret value display.
- Database-backed configuration.
- Remote/cloud configuration loading.
- Live reload or file watching.
- CLI behavior unless separately approved.
- YAML or TOML parsing.
- Profile inheritance.
- Profile-specific file loading behavior.

## Architecture Boundaries

Metadata layer:

- `fields.py`
- `schema.py`
- `paths.py`
- `profiles.py`

Acquisition layer:

- `sources/base.py`
- `sources/env.py`
- `sources/file.py`
- `sources/registry.py`

Processing layer:

- `merge.py`
- `validate.py`

Consumption layer:

- `runtime.py`

Presentation layer:

- `diagnostics.py`

Orchestration layer:

- `loader.py`

The intended dependency direction is:

```text
Fields
  -> Schema
  -> Sources and Registry
  -> Merge
  -> Validation
  -> Runtime
  -> Diagnostics
  -> Loader Orchestration
```

Lower-level modules should not depend on downstream repositories or higher
application domains.

## Loader Orchestration

`ConfigLoader.resolve()` is implemented as minimal orchestration.

It coordinates:

1. Profile name validation.
2. Source loading through `SourceRegistry`.
3. Optional override payload creation.
4. Deterministic merge through `ConfigMerger`.
5. Schema validation through `ConfigValidator`.
6. Runtime projection through `ResolvedConfig.from_validation_report(...)`.

The loader does not own source discovery logic, source loading behavior, merge
policy, schema validation rules, runtime lookup behavior, or diagnostics
formatting.

## Profile Semantics

`ConfigProfile` is public but explicitly non-frozen and deferred.

Currently supported:

- Named profile metadata.
- Optional profile description.
- Registration lookup by `ConfigLoader.resolve(profile_name=...)`.
- Passing the resolved profile name to sources.

Currently unsupported:

- Profile inheritance through `extends`.
- Profile-specific file behavior through `file_name`.
- Profile composition or profile-specific source policy.

If `ConfigProfile.extends` is set for a requested profile,
`ConfigLoader.resolve()` raises `ProfileResolutionError`.

## Source Responsibilities

Sources own only raw configuration acquisition:

- discover available input;
- load raw values;
- return immutable source payload metadata.

Sources must not validate schema correctness, apply merge precedence, interpret
profiles beyond source-local loading behavior, or produce runtime objects.

## Validation Responsibilities

Validation owns schema correctness:

- required field checks;
- default application;
- type compatibility checks;
- unknown field reporting;
- secret-safe issue reporting;
- immutable validation output.

Validation does not perform runtime lookup, diagnostics formatting, source
loading, or merge precedence decisions.

## Runtime Responsibilities

`ResolvedConfig` owns immutable access to already validated configuration.

It provides mapping access, iteration, membership checks, `get()`, `require()`,
and attribute-style access. It must not perform loading, merging, validation,
or diagnostics formatting.

## Diagnostics Responsibilities

Diagnostics present structural summaries of resolved configuration and
validation output. Diagnostics must not expose secret values.

## Dependency Policy

R001 has no runtime package dependencies. It must remain independent of all
downstream repositories. Downstream repository needs must not silently redefine
R001 architecture, public API, or scope.

## Public / Private Module Boundary

Package-root exports are current public API candidates, not frozen contracts.
Internal helper functions and non-exported types remain implementation details.

## Evidence Limitations

Source, tests, CI history, and validation evidence demonstrate implementation
state only. They do not approve R001, freeze R001, freeze the API, assign
Release Phase, approve release readiness, or validate package publication.
