# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>
# No warranty.

"""
Loadable plug-in interface.
"""

from collections.abc import AsyncIterator, Awaitable

import aiohttp
import click
import pluggy

from how_much_work.core.constants import PACKAGE
from how_much_work.core.options import MainOptions
from how_much_work.core.types import Package

hook_spec = pluggy.HookspecMarker(PACKAGE)
hook_impl = pluggy.HookimplMarker(PACKAGE)


class PackageRegistryPluginSpec:
    """
    Specifications of plugin hooks for package registry providers.
    """

    @hook_spec(firstresult=True)
    def normalize_package(
        self, pkg: Package, aiohttp_session: aiohttp.ClientSession
    ) -> Awaitable[Package] | None:
        """
        Normalize a package.

        Makes sure the canonical variants of properties are used.

        :param pkg: a package object
        :param aiohttp_session: :py:mod:`aiohttp` client session

        :raises PackageValidationError: on invalid packages

        :returns: normalized package or ``None``
        """

    @hook_spec(firstresult=True)
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
        :param aiohttp_session: :py:mod:`aiohttp` client session

        :returns: package's direct children
        """

    @hook_spec
    def setup_registry_plugin_options(self, click_group: click.Group) -> None:
        """
        Register plugin-specific command-line options.

        :param click_group: Click group of the main application
        """


class DistromapPluginSpec:
    """
    Specifications of plugin hooks for package mapping providers.
    """

    @hook_spec
    def setup_distromap_plugin(self, options: MainOptions, config: object) -> None:
        """
        Configure a plugin.

        :param options: main application options
        :param config: parsed :file:`distromap.toml` configuration file
        """


__all__ = [
    "DistromapPluginSpec",
    "PackageRegistryPluginSpec",
    "hook_impl",
]
