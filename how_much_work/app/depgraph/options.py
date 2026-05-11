# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024-2026 Anna <cyber@sysrq.in>
# No warranty

"""
Depgraph subcommand options.
"""

from pydantic import Field

from how_much_work.core.options import OptionsBase


class DepgraphOptions(OptionsBase):
    """
    Depgraph subcommand options.
    """

    #: Package name.
    package: str = Field(min_length=1)

    #: Maximum depth level.
    max_depth: int = Field(gt=0)
