# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Command line options object.
"""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OptionsBase(BaseModel):
    """
    Base class for all option objects.
    """
    model_config = ConfigDict(validate_assignment=True, extra="forbid")

    #: Subcommand options.
    children: dict[str, "OptionsBase"] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)

    def __setitem__(self, key: str, value: Any) -> None:
        setattr(self, key, value)
