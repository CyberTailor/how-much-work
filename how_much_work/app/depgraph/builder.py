# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>
# No warranty

"""
Build a dependency graph for any package.
"""

import asyncio
import dataclasses
import math
import sys
from collections.abc import AsyncIterator, Awaitable, Callable, Collection
from enum import Enum
from typing import SupportsFloat

import aiohttp
import networkx as nx
from pluggy import PluginManager

from how_much_work.core.exceptions import (
    PackageDependenciesFetchError,
    PackageValidationError,
)
from how_much_work.core.types import Package


@dataclasses.dataclass(frozen=True)
class SpecialNode:
    """
    Special node with attributes.
    """

    #: Short node status description.
    status: str

    #: Color used to fill the background of a node.
    fillcolor: str


class NodeStatus(SpecialNode, Enum):
    """
    Pre-defined nodes.
    """

    #: This node is incomplete because the maximum depth was reached.
    INCOMPLETE = ("incomplete", "yellow")

    #: This node is invalid because it could not be normalized.
    INVALID = ("invalid", "red")

    #: This node has matching package(s) from another repository.
    DONE = ("done", "green")

    #: This node is from another repository.
    VIRTUAL = ("virtual", "white")


class DependencyGraph:
    """
    Dependency graph builder.
    """

    def __init__(
        self, plugman: PluginManager, *,
        aiohttp_session: aiohttp.ClientSession,
        maxdepth: SupportsFloat = math.inf,
        pkg_filter: Callable[[Package], bool] | None = None,
        pkg_distromap: Callable[..., Awaitable[Collection[Package]]] | None = None
    ):
        """
        :param plugman: pluggy plugin manager
        :param aiohttp_session: :py:mod:`aiohttp` client session
        :param maxdepth: maximum number of nodes (including root) allowed in a
            single branch
        :param pkg_filter: callback to allow or block processing the current
            package (can be also used for progress reporting)
        :param pkg_distromap: callback to connect the original package with
            packages from another repository
        """

        self._maxdepth = maxdepth
        self._plugman = plugman
        self._aiohttp_session = aiohttp_session
        self._pkg_filter = pkg_filter
        self._pkg_distromap = pkg_distromap

        self._graph: "nx.DiGraph[Package]" = nx.DiGraph()
        self._visited: set[Package] = set()
        self._in_processing: dict[Package, asyncio.Event] = {}

    async def normalize_package(self, pkg: Package) -> Package:
        return await self._plugman.hook.normalize_package(
            pkg=pkg, aiohttp_session=self._aiohttp_session
        )

    def get_package_children(self, pkg: Package) -> AsyncIterator[Package]:
        return self._plugman.hook.get_package_children(
            pkg=pkg, aiohttp_session=self._aiohttp_session
        )

    def filter_pkg(self, pkg: Package) -> bool:
        if callable(self._pkg_filter):
            return self._pkg_filter(pkg)
        return True

    async def get_package_children_override(self, pkg: Package) -> Collection[Package]:
        if callable(self._pkg_distromap):
            return await self._pkg_distromap(pkg, aiohttp_session=self._aiohttp_session)
        return frozenset()

    @property
    def graph(self) -> "nx.DiGraph[Package]":
        """
        Read-only view of the dependency graph.

        All graph nodes are instances of :py:class:`Package`.

        Some nodes can have ``status`` attribute set, providing insight into the
        circumstances they were added.
        """

        return self._graph.copy(as_view=True)

    def mark_node(self, pkg: Package, *, marker: NodeStatus) -> None:
        self._graph.nodes[pkg].update(dataclasses.asdict(marker))

    async def add_depgraph(self, pkg: Package) -> None:
        """
        Add a package with its dependencies to the graph.

        Important notes:

        - Version constraints are completely ignored since there's no reliable
          method to compare them between repositories.

        :param pkg: package object
        """

        pkg = await self.normalize_package(pkg)
        if pkg in self._visited:
            # Consider the following consequent calls:
            # >>> await builder.add_depgraph(example)
            # >>> await builder.add_depgraph(dependency_of_example)
            # >>> await builder.add_depgraph(ignored_dependency_of_example")
            return

        self._graph.add_node(pkg)
        await self._add_depgraph(pkg, depth=float(self._maxdepth) - 1)

    async def _add_depgraph(self, pkg: Package, *, depth: SupportsFloat) -> None:

        self._visited.add(pkg)

        if len(pkg_subst := await self.get_package_children_override(pkg)) != 0:
            # Add replacements as children and terminate further processing.
            #
            # Marking replacements as visited is not needed: if it's a real
            # dependency for some other package, let it be processed as
            # usual.
            self.mark_node(pkg, marker=NodeStatus.DONE)
            for other in pkg_subst:
                self._graph.add_edge(pkg, other)
                self.mark_node(other, marker=NodeStatus.VIRTUAL)
            return

        tasks = [asyncio.create_task(self._process_child(pkg, child, depth=depth))
                 async for child in self.get_package_children(pkg)]
        try:
            await asyncio.gather(*tasks)
        except PackageDependenciesFetchError:
            # Fetching dependencies failed.
            # Mark the package as incomplete.
            self.mark_node(pkg, marker=NodeStatus.INCOMPLETE)

    async def _process_child(self, parent: Package, child: Package, *,
                             depth: SupportsFloat) -> None:
        try:
            child = await self.normalize_package(child)
        except PackageValidationError:
            # Add invalid package and mark it as visited.
            self._visited.add(child)
            self._graph.add_edge(parent, child)
            self.mark_node(child, marker=NodeStatus.INVALID)
            return

        if child in self._visited:
            if child in self._graph:
                # Existing nodes should always be linked.
                self._graph.add_edge(parent, child)
        elif float(depth) > 0:
            if not self.filter_pkg(child):
                # Skipped by the filters.
                # Mark as visited without adding to the graph.
                self._visited.add(child)
            else:
                # Package not marked as visited yet - going deeper.
                self._graph.add_edge(parent, child)
                await self._add_depgraph(child, depth=float(depth) - 1)
        else:
            # Not allowed to go deeper - mark current node as
            # incomplete.
            #
            # As it's been marked as visited, incomplete status will
            # stay.
            self.mark_node(parent, marker=NodeStatus.INCOMPLETE)
