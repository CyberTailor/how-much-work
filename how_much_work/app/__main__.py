# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

import asyncio

import click
import pluggy
from click_aliases import ClickAliasedGroup

from how_much_work.core.constants import (
    PACKAGE,
    VERSION,
)
from how_much_work.core.plugin_api import PackageRegistryPluginSpec


@click.group(cls=ClickAliasedGroup,
             context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(VERSION, "-V", "--version")
@click.pass_context
def cli(ctx: click.Context) -> None:
    """
    Estimate the amount of work needed to package a project.

    See `man how-much-work` for the full help.
    """

    plugman = pluggy.PluginManager(PACKAGE)
    plugman.add_hookspecs(PackageRegistryPluginSpec)
    plugman.load_setuptools_entrypoints("how_much_work.plugins")

    ctx.obj = plugman


@click.argument("package")
@click.option("-D", "--max-depth", type=int, default=6,
              help="Maximum depth level (default: 6).")
@click.option("-r", "--repo", metavar="REPO", required=True,
              help="Repository name.")
@cli.command(aliases=["dep", "dg", "d"])
@click.pass_obj
def depgraph(plugman: pluggy.PluginManager, max_depth: int, repo: str,
             package: str) -> None:
    """
    Compute a dependency graph.

    The result will be printed to the standard output in the DOT format.
    """
    from how_much_work.app.depgraph.cli import build_depgraph
    from how_much_work.app.depgraph.options import DepgraphOptions

    options = DepgraphOptions(package=package,
                              from_repo=repo,
                              max_depth=max_depth)

    asyncio.run(build_depgraph(plugman, options))
