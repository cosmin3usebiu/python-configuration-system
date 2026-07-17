"""Profile definitions for layered configuration resolution.

This module defines the object model used to describe configuration profiles.
"""

from __future__ import annotations

from dataclasses import dataclass

from python_configuration_system.types import ProfileName


@dataclass(slots=True, frozen=True)
class ConfigProfile:
    """Describe a named configuration profile.

    Attributes:
        name: Profile identifier such as ``dev`` or ``prod``.
        description: Human-readable description of the profile.
        extends: Optional parent profile name for future profile inheritance.
        file_name: Optional profile-specific configuration file name.

    Usage Notes:
        Profile inheritance is not implemented in Milestone 2.
    """

    name: ProfileName
    description: str = ""
    extends: ProfileName | None = None
    file_name: str | None = None
