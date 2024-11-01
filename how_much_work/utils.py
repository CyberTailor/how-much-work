# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Utility functions and classes.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aiohttp

from how_much_work.constants import USER_AGENT


@asynccontextmanager
async def aiohttp_session() -> AsyncGenerator[aiohttp.ClientSession, None]:
    """
    Construct an :py:class:`aiohttp.ClientSession` object with out settings.
    """

    headers = {"user-agent": USER_AGENT}
    timeout = aiohttp.ClientTimeout(total=30)
    session = aiohttp.ClientSession(headers=headers, timeout=timeout)

    try:
        yield session
    finally:
        await session.close()
