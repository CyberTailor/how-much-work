# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty.

"""
Loadable plug-in interface.
"""

from collections.abc import AsyncIterator, Coroutine

import aiohttp
import click
import pluggy

from how_much_work.core.constants import PACKAGE
from how_much_work.core.types import Package

pkg_registry_hook_spec = pluggy.HookspecMarker(PACKAGE)
pkg_registry_hook_impl = pluggy.HookimplMarker(PACKAGE)


class PackageRegistryPluginSpec:
    """
    Specifications of plugin hooks for package registry providers.
    """

    @pkg_registry_hook_spec(firstresult=True)
    def normalize_package(
        self, pkg: Package, aiohttp_session: aiohttp.ClientSession
    ) -> Coroutine[None, None, Package] | None:
        """
        Normalize a package.

        Makes sure the canonical variants of properties are used.

        :param pkg: a package object
        :param aiohttp_session: :external+aiohttp:py:mod:`aiohttp` client session

        :raises PackageValidationError: on invalid packages

        :returns: normalized package or ``None``
        """

    @pkg_registry_hook_spec(firstresult=True)
    def get_package_children(
        self, pkg: Package, aiohttp_session: aiohttp.ClientSession
    ) -> AsyncIterator[Package] | None:
        """
        Get direct children of the given package in its dependency graph.

        If the package has a condition, only dependencies pulled by this
        condition will be returned.

        Otherwise this method returns all variants of the package with
        dependency-defining conditions as well as unconditional dependencies.

        Important notes:

        - This method will *not* normalize packages, detect duplicates or tell
          apart different types of children for you.

        - Children are returned in order they encountered.

        :param pkg: package from the registry
        :param aiohttp_session: :external+aiohttp:py:mod:`aiohttp` client session

        :returns: package's direct children
        """

    @pkg_registry_hook_spec
    def setup_plugin_options(self, click_group: click.Group) -> None:
        """
        Register plugin-specific command-line options.

        :param click_group: Click group of the main application
        """


__all__ = [
    "pkg_registry_hook_impl",
    "PackageRegistryPluginSpec",
]
