# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import asyncio

import aiohttp
import pytest

from how_much_work.tests.utils import to_list
from how_much_work.types import Package

from how_much_work.plugins.pypi.registry import normalize, get_children


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
async def test_normalize(session: aiohttp.ClientSession):
    pkg = Package(name="Requests", repo_name="PyPI", condition="extra=='socks'")
    expected = Package(name="requests", repo_name="pypi",
                       condition='extra == "socks"')

    async with asyncio.timeout(30):
        assert await normalize(pkg, session=session) == expected


@pytest.mark.vcr
@pytest.mark.asyncio(loop_scope="session")
async def test_get_children(session: aiohttp.ClientSession):
    pkg = Package(name="requests", repo_name="pypi")
    pkg_socks = Package(name="requests", repo_name="pypi",
                        condition='extra == "socks"')

    async with asyncio.timeout(30):
        tasks = [asyncio.create_task(to_list(get_children(x, session=session)))
                 for x in (pkg, pkg_socks)]
        ch, ch_socks = await asyncio.gather(*tasks)

    assert pkg_socks in ch
    assert Package(name="urllib3", repo_name="pypi") in ch

    only_for_socks = set(ch_socks) - set(ch)
    assert Package(name="PySocks", repo_name="pypi") in only_for_socks
