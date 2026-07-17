# R001 Decisions: python-configuration-system

## Status

This is a recovered draft proposal based on observed implementation evidence.
It does not approve or freeze R001.

R001 approval/freeze state remains unverified. The API is not frozen. Release Phase is not assigned.

All decisions in this file are proposed and unapproved unless explicitly stated
otherwise.

## Decisions To Ratify

### DEC-R001-001: R001 Owns Configuration Infrastructure

Decision to ratify:

R001 owns configuration schemas, sources, merge, validation, runtime access, and
diagnostics.

Evidence:

Observed source modules and tests implement these responsibilities.

Status:

Proposed, not approved.

### DEC-R001-002: R001 Has No Runtime Dependencies

Decision to ratify:

R001 remains dependency-light and has no runtime package dependencies.

Evidence:

`pyproject.toml` declares an empty dependency list.

Status:

Proposed, not approved.

### DEC-R001-003: Public Models Should Be Immutable Where Practical

Decision to ratify:

Boundary objects should use immutable dataclasses and mapping proxies where
practical.

Evidence:

Observed field, source, merge, validation, runtime, and diagnostics objects.

Status:

Proposed, not approved.

### DEC-R001-004: Secret Values Must Not Be Exposed

Decision to ratify:

Secret fields must not reveal values in validation or diagnostics.

Evidence:

Validation and diagnostics tests check secret-safe behavior.

Status:

Proposed, not approved.

### DEC-R001-005: Loader Orchestration Is Incomplete

Decision to ratify:

`ConfigLoader.resolve()` remains incomplete and must not be represented as
operational.

Evidence:

`loader.py` raises `NotImplementedError`.

Status:

Proposed, not approved.

## Open Decisions

- Whether `ConfigLoader` should remain public before implementation.
- Whether all currently exported source metadata objects should remain public.
- Whether merge strategy classes should remain internal or become public.
- Whether `ConfigProfile` should remain public.
- Whether loader orchestration should be implemented or explicitly deferred.
- Whether R001 should enter Release Phase after artifact recovery or require
  code work.

## Evidence Limitations

Source and tests provide implementation evidence. They do not prove prior
approval, API freeze, milestone approval, or release readiness.

This file does not approve R001, freeze R001, freeze the API, assign Release
Phase, approve milestones, or declare release readiness.
