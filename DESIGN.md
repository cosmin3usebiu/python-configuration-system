# R001 Design: python-configuration-system

## Status

This is a recovered draft proposal based on observed implementation evidence.
It does not approve or freeze R001.

R001 approval/freeze state remains unverified. The API is not frozen. Release Phase is not assigned.

This design is not yet approved.

## Purpose

Provide a reusable Python configuration system with typed schemas, source
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
- Secret-safe validation issues.
- Immutable runtime configuration views.
- Diagnostics presentation.

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
- Database management.
- CLI behavior unless separately approved.

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

## Dependency Policy

R001 has no runtime package dependencies.

R001 must remain independent of downstream repositories. Downstream repository
needs must not silently redefine R001 architecture, public API, or scope.

## Public / Private Module Boundary

The package root exports observed public objects. Exported objects are
implementation evidence, not a frozen public contract, until `API.md` is
reviewed and approved.

Internal helper functions and non-exported types remain implementation details.

## Validation Expectations

Validation should be schema-driven, deterministic, and secret-safe. Validation
must not expose secret values in issues, diagnostics, exceptions, or other
public reporting surfaces.

## Error-Handling Expectations

Repository-native exceptions derive from `ConfigurationError`.

Source, schema, merge, profile, and validation failures should use explicit
exception types.

## Known Incomplete Capabilities

`ConfigLoader.resolve()` is incomplete and raises `NotImplementedError`.

High-level end-to-end loader orchestration is incomplete.

## Evidence Limitations

This design is recovered from observed source, tests, metadata, and stale
documentation. Source and tests are evidence of implementation, not approval.

This document does not approve R001, freeze R001, freeze the API, assign Release
Phase, approve milestones, or declare release readiness.
