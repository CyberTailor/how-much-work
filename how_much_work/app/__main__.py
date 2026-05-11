# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>
# No warranty

import asyncio
import functools
import os
import tomllib
from pathlib import Path

import click
import pluggy
from click_aliases import ClickAliasedGroup

from how_much_work.core.constants import (
    DISTROMAP_PLUGINS_ENTRY_POINT,
    REGISTRY_PLUGINS_ENTRY_POINT,

    PACKAGE,
    VERSION,
)
from how_much_work.core.options import MainOptions
from how_much_work.core.plugin_api import (
    DistromapPluginSpec,
    PackageRegistryPluginSpec,
)


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


def load_config(basename: str) -> object:
    """
    Read a TOML file from the user's XDG config directory.

    :returns: parsed config
    """

    path = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser()
    path = path / PACKAGE / basename
    if path.is_file():
        with path.open("rb") as file:
            return tomllib.load(file)
    return {}


@click.group(cls=ClickAliasedGroup,
             context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-r", "--repo", metavar="REPO", required=True,
              help="Repository specification.")
@click.version_option(VERSION, "-V", "--version")
@click.pass_context
def cli(ctx: click.Context, repo: str) -> None:
    """
    Estimate the amount of work needed to package a project.

    See `man how-much-work` for the full help.
    """

    ctx.ensure_object(MainOptions)
    options: MainOptions = ctx.obj

    from_repo, *to_repo = repo.split(":", maxsplit=1)
    options.from_repo = from_repo
    if len(to_repo) != 0:
        options.to_repo = to_repo[0]

        plugman = get_plugin_manager()
        plugman.add_hookspecs(DistromapPluginSpec)
        plugman.load_setuptools_entrypoints(DISTROMAP_PLUGINS_ENTRY_POINT)
        plugman.hook.setup_distromap_plugin(
            options=options, config=load_config("distromap.toml")
        )


@click.argument("package")
@click.option("-D", "--max-depth", type=int, default=6,
              help="Maximum depth level (default: 6).")
@cli.command(aliases=["dep", "dg", "d"])
@click.pass_obj
def depgraph(options: MainOptions, package: str, max_depth: int) -> None:
    """
    Compute a dependency graph.

    The result will be printed to the standard output in the DOT format.
    """
    from how_much_work.app.depgraph.cli import build_depgraph
    from how_much_work.app.depgraph.options import DepgraphOptions

    plugman = get_plugin_manager()
    options.children["depgraph"] = DepgraphOptions(
        package=package, max_depth=max_depth
    )

    asyncio.run(build_depgraph(plugman, options))


get_plugin_manager().hook.setup_registry_plugin_options(click_group=cli)
