# Folder Structure

## Repository Layout

- `src/python_configuration_system/`: package source.
- `src/python_configuration_system/sources/`: source contracts and built-ins.
- `tests/`: behavioral tests.
- `docs/`: supporting documentation.
- `docs/api/`: API documentation notes.
- `docs/adr/`: architecture decision record placeholder.
- `examples/`: usage examples and notes.
- `.github/workflows/`: CI workflow.

## Package Modules

- `fields.py`: field metadata.
- `schema.py`: schema definitions.
- `profiles.py`: profile metadata.
- `sources/base.py`: source contracts and source payload objects.
- `sources/env.py`: environment source.
- `sources/file.py`: JSON file source.
- `sources/registry.py`: source registration.
- `merge.py`: merge engine.
- `validate.py`: validation engine.
- `runtime.py`: immutable runtime object.
- `diagnostics.py`: diagnostic summaries.
- `loader.py`: high-level orchestration.

This document does not define or freeze public API status.
