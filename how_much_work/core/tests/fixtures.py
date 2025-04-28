# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>
# No warranty

from collections.abc import AsyncGenerator

import aiohttp
import pluggy
import pytest
import pytest_asyncio

from how_much_work.core.constants import PACKAGE
from how_much_work.core.plugin_api import PackageRegistryPluginSpec


@pytest_asyncio.fixture(loop_scope="session")
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    timeout = aiohttp.ClientTimeout(total=15)
    test_session = aiohttp.ClientSession(timeout=timeout)
    try:
        yield test_session
    finally:
        await test_session.close()


@pytest.fixture(scope="function")
def plugman() -> pluggy.PluginManager:
    pm = pluggy.PluginManager(PACKAGE)
    pm.add_hookspecs(PackageRegistryPluginSpec)
    return pm
