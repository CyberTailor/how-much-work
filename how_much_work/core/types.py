# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2025 Anna <cyber@sysrq.in>
# No warranty

"""
Common type definitions.
"""

from pydantic import BaseModel, ConfigDict, Field


class Package(BaseModel):
    """
    Graph node representing a package.
    """
    model_config = ConfigDict(frozen=True)

    #: Package name in the repository.
    name: str = Field(min_length=1)

    #: Repository name.
    repo_name: str = Field(min_length=1)

    #: Which condition pulls this package.
    condition: str | None = None

    def __str__(self) -> str:
        result = f"{self.name!s}::{self.repo_name!s}"
        if self.condition is not None:
            result += f"[{self.condition!s}]"

        return result
