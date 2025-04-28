# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty.

"""
PyPI (Python Package Index) registry.
"""

import asyncio
import re
from collections.abc import AsyncIterator, Iterator

import aiohttp
from lru import LRU
from poetry.core.version.markers import (
    SingleMarker,
    parse_marker,
)
from poetry.core.version.requirements import Requirement

from how_much_work.core.exceptions import (
    PackageDependenciesFetchError,
    PackageValidationError,
)
from how_much_work.core.types import Package

from how_much_work.plugins.pypi.constants import (
    PYPI_URL,
    REPO_NAME,
)
from how_much_work.plugins.pypi._types import (
    JsonProject,
    JsonProjectInfo,
)

# Acceptable project name separator regex.
_name_separator_re = re.compile(r"[-_.]+")

# Static variable, modifications are shared between all instances.
# Dictionary is LRU so it doesn't grow to infinite size.
_projects: "LRU[str, JsonProjectInfo]" = LRU(100)

# Another static variable, used to track if the same project was
# requested simultaneously.
_in_processing: dict[str, asyncio.Event] = {}


async def _get_project_info(pkg_name: str, *,
                            session: aiohttp.ClientSession) -> JsonProjectInfo:

    def _finish_processing() -> None:
        # Notify waiting coroutines that they can grab project info from cache.
        if key in _in_processing:
            _in_processing[key].set()
            del _in_processing[key]

    # Perform package name "normalization" as defined in PEP 503.
    key = _name_separator_re.sub("-", pkg_name).lower()

    if key not in _in_processing:
        # Start a new "processing session" for this package.
        _in_processing[key] = asyncio.Event()
    else:
        # Wait for the "processing session" to finish, then grab from the cache.
        await _in_processing[key].wait()

    if key in _projects:
        _finish_processing()
        return _projects[key]

    url = PYPI_URL + f"/pypi/{pkg_name}/json"
    async with session.get(url, raise_for_status=True) as response:
        raw_data = await response.read()

    try:
        result = JsonProject.model_validate_json(raw_data).info
    except ValueError as err:
        # JSON decode error
        pkg = Package(name=pkg_name, repo_name=REPO_NAME)
        raise PackageValidationError(pkg) from err
    finally:
        _finish_processing()

    _projects[key] = result
    return result


async def normalize(pkg: Package, *,
                    session: aiohttp.ClientSession) -> Package:
    """
    Normalize a PyPI package.

    Makes sure the canonical variants of properties are used.

    Important notes:

    - Canonical project name is used instead of :pep:`503`: "normalized"
      project name.

    - Logically same conditions can be recognized as different, potentially
      resulting in duplicate nodes.

    :param pkg: PyPI package
    :param session: :external+aiohttp:py:mod:`aiohttp` client session

    :raises PackageValidationError: on invalid or nonexistent packages

    :returns: normalized package
    """

    try:
        project = await _get_project_info(pkg.name, session=session)
    except (aiohttp.ClientResponseError, asyncio.TimeoutError) as err:
        # Usually "Project Not Found"
        raise PackageValidationError(pkg) from err

    if (condition := pkg.condition) is not None:
        try:
            # do a roundtrip
            condition = str(parse_marker(condition))
        except Exception as err:
            raise PackageValidationError(pkg) from err

    return pkg.model_copy(
        update={
            "name": project.name,
            "repo_name": REPO_NAME,
            "condition": condition,
        }
    )


async def get_children(pkg: Package, *,
                       session: aiohttp.ClientSession) -> AsyncIterator[Package]:
    """
    Get direct children of the given PyPI package in its dependency graph.

    If the package has a condition, only dependencies pulled by this
    condition will be returned.

    Otherwise this method returns all variants of the package with
    dependency-defining conditions as well as unconditional dependencies.

    Important notes:

    - This method will *not* normalize packages, detect duplicates or tell
      apart different types of children for you.

    - Children are returned in order they encountered.

    - Conditions are represented as :pep:`508` Environment Markers.

    - Build dependencies are *not* returned by PyPI JSON API.

    :param pkg: PyPI package
    :param session: :external+aiohttp:py:mod:`aiohttp` client session

    :raises aiohttp.ClientResponseError: on HTTP errors
    :raises ValueError: on JSON decode failure

    :returns: package's direct children
    """

    def _dependency_with_extras(req: Requirement) -> Iterator[Package]:
        yield Package(name=req.name, repo_name=REPO_NAME)
        for selected_feature in req.extras:
            marker = SingleMarker("extra", selected_feature)
            yield Package(name=req.name, repo_name=REPO_NAME,
                          condition=str(marker))

    try:
        project = await _get_project_info(pkg.name, session=session)
    except (aiohttp.ClientResponseError, asyncio.TimeoutError) as err:
        raise PackageDependenciesFetchError(pkg) from err
    if not project.requires_dist:
        # No dependencies defined.
        return

    if pkg.condition:
        # Select only dependencies pulled by this condition.
        pkg_marker = parse_marker(pkg.condition)
        for req in map(Requirement, project.requires_dist):
            if req.marker == pkg_marker:
                for child_pkg in _dependency_with_extras(req):
                    yield child_pkg
    else:
        # Select all variants of the package with dependency-defining
        # conditions as well as unconditional dependencies.
        for req in map(Requirement, project.requires_dist):
            if req.marker:
                yield Package(name=pkg.name, repo_name=REPO_NAME,
                              condition=str(req.marker))
            else:
                for child_pkg in _dependency_with_extras(req):
                    yield child_pkg
