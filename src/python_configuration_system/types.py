"""Shared typing contracts for the package.

This module contains stable type aliases used across the public and internal
object model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, TypeAlias

FieldName: TypeAlias = str
ProfileName: TypeAlias = str
SourceName: TypeAlias = str
ConfigValue: TypeAlias = Any
ConfigMapping: TypeAlias = Mapping[FieldName, ConfigValue]
FieldRuntimeType: TypeAlias = type[Any] | tuple[type[Any], ...]
PathValue: TypeAlias = str | Path
