# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2026 Anna <cyber@sysrq.in>
# No warranty

from typing import TypedDict


class SourceRepoConfig(TypedDict):
    repo_name: str
    to_repo: dict[str, list[str]]


class RepologyDistromapConfig(TypedDict):
    from_repo: dict[str, SourceRepoConfig]


class DistromapConfig(TypedDict, total=False):
    repology: RepologyDistromapConfig
