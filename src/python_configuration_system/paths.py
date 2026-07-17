"""Filesystem path normalization helpers.

This module defines declarative path-handling contracts used by path fields.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class PathKind(StrEnum):
    """Represent the intended kind of a configured filesystem path."""

    ANY = "any"
    FILE = "file"
    DIRECTORY = "directory"


@dataclass(slots=True, frozen=True)
class PathRules:
    """Declare future normalization and validation rules for a path field.

    Attributes:
        kind: Intended path kind.
        must_exist: Whether the path must already exist during validation.
        resolve_relative_to_workspace: Whether relative paths should resolve
            from an application-defined workspace root.
    """

    kind: PathKind = PathKind.ANY
    must_exist: bool = False
    resolve_relative_to_workspace: bool = True
