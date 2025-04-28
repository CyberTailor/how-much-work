# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2025 Anna <cyber@sysrq.in>
# No warranty

"""
Exceptions that can be used in various parts of the program.
"""

from how_much_work.core.types import Package


class PackageError(RuntimeError):
    """
    Base class for all package-scope errors.
    """

    def __init__(self, pkg: Package, message: str | None = None):
        if message is None:
            message = f"Exception occured while resolving {pkg!s}"
        super().__init__(message)
        self._pkg = pkg

    @property
    def pkg(self) -> Package:
        """
        Underlying :py:class:`Package` object.
        """
        return self._pkg


class PackageValidationError(PackageError):
    """
    Raised if package validation fails.
    """

    def __init__(self, pkg: Package):
        message = f"Validation failed for package {pkg!s}"
        super().__init__(pkg, message)


class PackageDependenciesFetchError(PackageError):
    """
    Raised if fetching package's dependencies fails.
    """

    def __init__(self, pkg: Package):
        message = f"Fetching dependencies failed for package {pkg!s}"
        super().__init__(pkg, message)
