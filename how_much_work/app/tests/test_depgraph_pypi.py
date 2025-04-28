# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>
# No warranty.

import aiohttp
import pluggy
import pytest
import pytest_asyncio

from how_much_work.core.types import Package
from how_much_work.app.depgraph.builder import (
    DependencyGraph,
    NodeStatus,
)

try:
    import how_much_work.plugins.pypi
    HAS_PYPI_PLUGIN = True
except ImportError:
    HAS_PYPI_PLUGIN = False


@pytest_asyncio.fixture(scope="function")
async def builder(
    request: pytest.FixtureRequest,
    plugman: pluggy.PluginManager,
    session: aiohttp.ClientSession
) -> DependencyGraph:

    builder_args: dict = {}
    if (marker := request.node.get_closest_marker("builder_args")) is not None:
        builder_args = marker.kwargs

    plugman.register(how_much_work.plugins.pypi)
    return DependencyGraph(plugman, aiohttp_session=session, **builder_args)


@pytest.mark.skipif(not HAS_PYPI_PLUGIN,
                    reason="how-much-work-pypi plugin not available")
@pytest.mark.asyncio
class TestDepgraphPypi:

    @pytest.mark.vcr
    async def test_depgraph_nodeps(self, builder: DependencyGraph):
        pkg = Package(name="poetry-core", repo_name="pypi")
        await builder.add_depgraph(pkg)

        graph = builder.graph
        assert len(graph) == 1
        assert not graph.edges

    @pytest.mark.vcr
    async def test_depgraph_nocond(self, builder: DependencyGraph):
        expected_edge = (
            Package(name="cffi", repo_name="pypi"),
            Package(name="pycparser", repo_name="pypi"),
        )

        pkg = Package(name="cffi", repo_name="pypi")
        await builder.add_depgraph(pkg)

        graph = builder.graph
        assert expected_edge in graph.edges

    @pytest.mark.vcr
    @pytest.mark.builder_args(maxdepth=2)
    async def test_depgraph_maxdepth(self, builder: DependencyGraph):
        pkg = Package(name="requests", repo_name="pypi")
        await builder.add_depgraph(pkg)

        graph = builder.graph
        dep = Package(name="urllib3", repo_name="pypi")
        assert dep in graph
        assert graph.nodes[dep].get("status") == NodeStatus.INCOMPLETE.status
