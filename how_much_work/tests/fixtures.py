# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

from collections.abc import AsyncGenerator

import aiohttp
import pytest_asyncio


@pytest_asyncio.fixture(loop_scope="session")
async def session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    timeout = aiohttp.ClientTimeout(total=15)
    test_session = aiohttp.ClientSession(timeout=timeout)
    try:
        yield test_session
    finally:
        await test_session.close()
