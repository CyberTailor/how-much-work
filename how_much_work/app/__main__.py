# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import asyncio
import functools

import click
import pluggy
from click_aliases import ClickAliasedGroup

from how_much_work.core.constants import (
    PACKAGE,
    REGISTRY_PLUGINS_ENTRY_POINT,
    VERSION,
)
from how_much_work.core.options import MainOptions
from how_much_work.core.plugin_api import PackageRegistryPluginSpec


@functools.cache
def get_plugin_manager() -> pluggy.PluginManager:
    """
    Load plug-ins from entry points.

    Calls to this functions are cached.

    :returns: plugin manager instance
    """

    plugman = pluggy.PluginManager(PACKAGE)
    plugman.add_hookspecs(PackageRegistryPluginSpec)
    plugman.load_setuptools_entrypoints(REGISTRY_PLUGINS_ENTRY_POINT)

    return plugman


@click.group(cls=ClickAliasedGroup,
             context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(VERSION, "-V", "--version")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Estimate the amount of work needed to package a project.

    See `man how-much-work` for the full help.
    """

    ctx.ensure_object(MainOptions)


@click.argument("package")
@click.option("-D", "--max-depth", type=int, default=6,
              help="Maximum depth level (default: 6).")
@click.option("-r", "--repo", metavar="REPO", required=True,
              help="Repository name.")
@cli.command(aliases=["dep", "dg", "d"])
@click.pass_obj
def depgraph(options: MainOptions, package: str, repo: str, max_depth: int) -> None:
    """
    Compute a dependency graph.

    The result will be printed to the standard output in the DOT format.
    """
    from how_much_work.app.depgraph.cli import build_depgraph
    from how_much_work.app.depgraph.options import DepgraphOptions

    plugman = get_plugin_manager()
    options.children["depgraph"] = DepgraphOptions(
        package=package, from_repo=repo, max_depth=max_depth
    )

    asyncio.run(build_depgraph(plugman, options))


get_plugin_manager().hook.setup_plugin_options(click_group=cli)
