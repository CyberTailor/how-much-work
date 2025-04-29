# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>
# No warranty

"""
Package filters for PyPI packages.
"""

from collections.abc import Callable, Iterator
from fnmatch import fnmatch

from poetry.core.version.markers import (
    BaseMarker,
    SingleMarker,
    parse_marker,
)

from how_much_work.core.types import Package


def _walk_marker(marker: BaseMarker) -> Iterator[SingleMarker]:
    """
    Break down a compound marker into individual components.
    """

    if hasattr(marker, "markers"):
        for submarker in marker.markers:
            yield from _walk_marker(submarker)
    elif isinstance(marker, SingleMarker):
        yield marker


def exclude_python_extras(*extras: str) -> Callable[[Package], bool]:
    """
    Generate a filter to exclude dependencies pulled in by the given extras.

    :param extras: glob(7) wildcards are allowed

    :returns: package filter function
    """

    def pkg_filter(pkg: Package) -> bool:
        if not pkg.condition:
            return True

        for marker in _walk_marker(parse_marker(pkg.condition)):
            if (
                marker.name == "extra"
                and marker.operator == "=="
                and any(fnmatch(marker.value, glob) for glob in extras)
            ):
                return False
        return True

    return pkg_filter
