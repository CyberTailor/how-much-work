# SPDX-License-Identifier: WTFPL
# SPDX-FileCopyrightText: 2024 Anna <cyber@sysrq.in>
# No warranty

from collections.abc import AsyncIterator
from typing import TypeVar

T = TypeVar("T")


async def to_list(source: AsyncIterator[T]) -> list[T]:
    result: list[T] = []
    async for item in source:
        result.append(item)
    return result
