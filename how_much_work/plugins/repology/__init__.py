# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2026 Anna <cyber@sysrq.in>
# No warranty

from collections.abc import Collection, Sequence
from typing import Awaitable, Callable
import warnings

import aiohttp
import repology_client
from pydantic import TypeAdapter, ValidationError
from repology_client.exceptions.resolve import ProjectNotFound

from how_much_work.core.options import MainOptions
from how_much_work.core.plugin_api import hook_impl
from how_much_work.core.types import Package

from how_much_work.plugins.repology.types import DistromapConfig


def make_distromap_func(
    from_repo: str, target_repos: Sequence[str]
) -> Callable[..., Awaitable[Collection[Package]]]:

    async def callback(
        pkg: Package, *, aiohttp_session: aiohttp.ClientSession
    ) -> Collection[Package]:
        try:
            pkg_list = await repology_client.resolve_package(
                from_repo, pkg.name, session=aiohttp_session
            )
        except ProjectNotFound:
            return {}

        return {Package(name=other.visiblename, repo_name=other.repo)
                for other in pkg_list
                if other.repo in target_repos}

    return callback


@hook_impl
def setup_distromap_plugin(options: MainOptions, config: object) -> None:
    try:
        config = TypeAdapter(DistromapConfig).validate_python(config)
    except ValidationError:
        warnings.warn("Parsing Repology configuration failed")
        return

    if (plugin_config := config.get("repology")) is not None:
        repo_config = plugin_config["from_repo"].get(options.from_repo)
        if repo_config is not None:
            target_repos = repo_config["to_repo"].get(options.to_repo, [])
            if len(target_repos) != 0:
                options.add_pkg_distromap(
                    make_distromap_func(repo_config["repo_name"], target_repos)
                )
