# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

"""
Exceptions that can be used in various parts of the program.
"""


class PackageValidationError(RuntimeError):
    """
    Raised if package validation fails.
    """
