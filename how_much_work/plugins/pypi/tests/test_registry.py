# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>
# No warranty

import asyncio

import aiohttp
import pytest

from how_much_work.core.tests.utils import to_list
from how_much_work.core.types import Package

from how_much_work.plugins.pypi.filters import exclude_python_extras
from how_much_work.plugins.pypi.registry import normalize, get_children


def test_filter_extras():
    pkg_filter = exclude_python_extras("dev*", "doc*", "test*", "all")
    pkg = Package(name="example", repo_name="pypi")

    assert pkg_filter(pkg)
    assert pkg_filter(pkg.model_copy(update={"condition": "extra=='feature'"}))
    assert pkg_filter(pkg.model_copy(update={"condition": "extra!='doc'"}))
    assert pkg_filter(pkg.model_copy(update={"condition": "python_version<='3.12'"}))

    assert not pkg_filter(pkg.model_copy(update={"condition": "extra=='test'"}))
    assert not pkg_filter(pkg.model_copy(update={"condition": "extra=='tests'"}))
    assert not pkg_filter(pkg.model_copy(update={"condition": "extra=='all'"}))


@pytest.mark.vcr
@pytest.mark.asyncio
async def test_normalize(session: aiohttp.ClientSession):
    pkg = Package(name="Requests", repo_name="PyPI", condition="extra=='socks'")
    expected = Package(name="requests", repo_name="pypi",
                       condition='extra == "socks"')

    async with asyncio.timeout(30):
        assert await normalize(pkg, session=session) == expected


@pytest.mark.vcr
@pytest.mark.asyncio
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
