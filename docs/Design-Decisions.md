# Design Decisions

## Immutable Boundary Objects

Configuration fields, schemas, source payloads, validation reports, runtime
objects, and diagnostics summaries use immutable data boundaries where
appropriate. This keeps layer inputs and outputs predictable.

## Source Separation

Source composition belongs to `SourceRegistry`. Individual sources discover and
load raw data only. They do not validate schemas, merge values, or create
runtime configuration.

## Merge and Validation Separation

Merge owns deterministic precedence. Validation owns correctness. Unknown
fields pass through merge and are reported by validation.

## Runtime Minimalism

`ResolvedConfig` is an immutable view over validated configuration. It exposes
mapping access, attribute access, iteration, `get()`, and `require()`. It does
not inspect validation issues or perform loading.

## Loader Orchestration

`ConfigLoader.resolve()` coordinates the existing lower-level components. It
does not own source behavior, merge strategy internals, validation rules,
runtime access behavior, or diagnostics formatting.

## Profile Deferral

`ConfigProfile` remains public but non-frozen. Profile inheritance and
profile-specific file behavior are explicitly deferred.

## Status

These design notes document current implementation decisions. They do not
approve R001, freeze architecture, freeze API, or declare release readiness.
