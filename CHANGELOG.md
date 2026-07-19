# Changelog

All notable changes to this project will be documented in this file.

## [0.1.0] - Unreleased

### Documentation

- Refreshed README, API, design, milestone, docs, and example documentation to
  reflect the current implemented R001 state.
- Removed obsolete skeleton-only statements from repository documentation.
- Documented the implemented minimal `ConfigLoader.resolve()` orchestration
  behavior.
- Documented the current package-root export disposition.
- Documented `ConfigProfile` as public but explicitly non-frozen and deferred.
- Documented unsupported behavior and non-goals.

### Implementation Status

- `ConfigLoader.resolve()` has been implemented in prior work and no longer
  raises `NotImplementedError` as normal behavior.

### Governance

- R001 remains unapproved.
- R001 architecture is not frozen.
- R001 public API is not frozen.
- R001 is not in Release Phase.
- No release, build validation, package publication, or production-readiness
  claim is made by this changelog.
