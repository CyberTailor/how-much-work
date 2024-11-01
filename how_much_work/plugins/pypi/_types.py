# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Types for PyPI JSON API, implemented as Pydantic models.
"""

from pydantic import BaseModel, ConfigDict, Field


class JsonProjectInfo(BaseModel):
    """
    Project metadata information returned by PyPI JSON API.
    """
    model_config = ConfigDict(frozen=True, defer_build=True)

    #: Canonical project name.
    name: str = Field(min_length=1)

    #: Dependencies.
    requires_dist: frozenset[str] | None = None


class JsonProject(BaseModel):
    """
    Project object returned by PyPI JSON API.
    """
    model_config = ConfigDict(frozen=True)

    info: JsonProjectInfo
