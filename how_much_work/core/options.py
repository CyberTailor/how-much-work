# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>
# No warranty

"""
Command line options object.
"""

from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from how_much_work.core.types import Package


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


class MainOptions(OptionsBase):
    """
    Main application options.
    """

    _pkg_filters: list[Callable[[Package], bool]] = PrivateAttr(default_factory=list)

    def add_pkg_filter(self, filter_func: Callable[[Package], bool]) -> None:
        """
        Add a callback to allow or block processing of a package.

        :param filter_func: package filtering function
        """

        self._pkg_filters.append(filter_func)

    def pkg_filter(self, pkg: Package) -> bool:
        """
        Package filtering callback function.

        :param pkg: package object to filter

        :returns: the result of all enabled package filtering functions combined
            with the logical AND operation. If none are enabled, always returns
            ``True``.
        """

        return all(filter_func(pkg) for filter_func in self._pkg_filters)
