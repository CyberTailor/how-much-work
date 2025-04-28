# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

from collections.abc import AsyncIterator, Coroutine

import aiohttp

from how_much_work.core.plugin_api import pkg_registry_hook_impl
from how_much_work.core.types import Package


@pkg_registry_hook_impl
def normalize_package(
    pkg: Package, aiohttp_session: aiohttp.ClientSession
) -> Coroutine[None, None, Package] | None:
    if pkg.repo_name == "pypi":
        from how_much_work.plugins.pypi.registry import normalize
        return normalize(pkg, session=aiohttp_session)
    return None


@pkg_registry_hook_impl
def get_package_children(
    pkg: Package, aiohttp_session: aiohttp.ClientSession
) -> AsyncIterator[Package] | None:
    if pkg.repo_name == "pypi":
        from how_much_work.plugins.pypi.registry import get_children
        return get_children(pkg, session=aiohttp_session)
    return None
