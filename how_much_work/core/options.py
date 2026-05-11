# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>
# No warranty

"""
Command line options object.
"""

import aiohttp
from collections.abc import Awaitable, Callable, Collection
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

    _pkg_filters: list[
        Callable[[Package], bool]
    ] = PrivateAttr(default_factory=list)
    _pkg_distromaps: list[
        Callable[..., Awaitable[Collection[Package]]]
    ] = PrivateAttr(default_factory=list)

    #: Source repository name.
    from_repo: str = Field(default="", min_length=1)

    #: Target repository name.
    to_repo: str = ""

    def add_pkg_filter(self, filter_func: Callable[[Package], bool]) -> None:
        """
        Add a callback to allow or block processing of a package.

        :param filter_func: package filtering function
        """

        self._pkg_filters.append(filter_func)

    def add_pkg_distromap(
        self, distromap_func: Callable[..., Awaitable[Collection[Package]]]
    ) -> None:
        """
        Add a callback to replace a package with equivalent package(s) from
        another repository.

        Mappings added first have highest priority.

        :param distromap_func: package substitution function
        """

        self._pkg_distromaps.append(distromap_func)

    def pkg_filter(self, pkg: Package) -> bool:
        """
        Package filtering callback function.

        :param pkg: package object to filter

        :returns: the result of all enabled package filtering functions combined
            with the logical AND operation. If none are enabled, always returns
            ``True``.
        """

        return all(filter_func(pkg) for filter_func in self._pkg_filters)

    async def pkg_distromap(
        self, pkg: Package, *, aiohttp_session: aiohttp.ClientSession
    ) -> Collection[Package]:
        """
        Package substitution callback function.

        :param pkg: package object to get replacements for
        :param aiohttp_session: :py:mod:`aiohttp` client session

        :returns: the first non-empty result returned by any of enabled
            distromap functions, and the empty set otherwise
        """

        if self.to_repo and len(self._pkg_distromaps) == 0:
            raise RuntimeError(
                f"No {self.from_repo}:{self.to_repo} mappings configured"
            )

        for distromap_func in self._pkg_distromaps:
            pkg_subst = await distromap_func(pkg, aiohttp_session=aiohttp_session)
            if len(pkg_subst) != 0:
                return pkg_subst
        return frozenset()
