# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>
# No warranty

"""
Implementation of CLI commands for the Depgraph module.
"""

import sys

import networkx as nx
from pluggy import PluginManager

from how_much_work.core.types import Package
from how_much_work.core.utils import aiohttp_session

from how_much_work.app.depgraph.builder import DependencyGraph
from how_much_work.app.depgraph.options import DepgraphOptions


async def build_depgraph(plugman: PluginManager, options: DepgraphOptions) -> None:
    pkg = Package(name=options.package, repo_name=options.from_repo)

    async with aiohttp_session() as session:
        builder = DependencyGraph(plugman, maxdepth=options.max_depth,
                                  aiohttp_session=session)
        await builder.add_depgraph(pkg)

    pgv = nx.nx_agraph.to_agraph(builder.graph)
    pgv.graph_attr.update(rankdir="LR")  # Left to right
    pgv.node_attr.update(shape="box", style="filled", fillcolor="lightgrey")
    pgv.write(sys.stdout)
