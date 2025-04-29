# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

from collections.abc import AsyncIterator, Callable, Coroutine, Sequence

import aiohttp
import click

from how_much_work.core.options import MainOptions
from how_much_work.core.plugin_api import pkg_registry_hook_impl
from how_much_work.core.types import Package

from how_much_work.plugins.pypi.constants import REPO_NAME


@pkg_registry_hook_impl
def normalize_package(
    pkg: Package, aiohttp_session: aiohttp.ClientSession
) -> Coroutine[None, None, Package] | None:
    if pkg.repo_name == REPO_NAME:
        from how_much_work.plugins.pypi.registry import normalize
        return normalize(pkg, session=aiohttp_session)
    return None


@pkg_registry_hook_impl
def get_package_children(
    pkg: Package, aiohttp_session: aiohttp.ClientSession
) -> AsyncIterator[Package] | None:
    if pkg.repo_name == REPO_NAME:
        from how_much_work.plugins.pypi.registry import get_children
        return get_children(pkg, session=aiohttp_session)
    return None


def pypi_filter_extras_option() -> Callable[[click.Group], click.Group]:

    def callback(ctx: click.Context, param: click.Option, value: Sequence[str]) -> None:
        from how_much_work.plugins.pypi.filters import exclude_python_extras

        if not value or ctx.resilient_parsing:
            return
        ctx.ensure_object(MainOptions)
        options: MainOptions = ctx.obj
        options.add_pkg_filter(exclude_python_extras(*value))

    return click.option("--pypi-filter-extras", metavar="GLOB", multiple=True,
                        expose_value=False, callback=callback,
                        help="Exclude Python optional dependency groups "
                             "matching a pattern.")


@pkg_registry_hook_impl
def setup_plugin_options(click_group: click.Group) -> None:
    with_pypi_filter_extras_option = pypi_filter_extras_option()

    click_group = with_pypi_filter_extras_option(click_group)
