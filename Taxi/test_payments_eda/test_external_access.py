import asyncio

import aiohttp
import pytest

from payments_eda.utils import external_access


@pytest.mark.parametrize(
    'exc',
    [
        asyncio.TimeoutError,
        asyncio.CancelledError,
        aiohttp.ClientError,
        Exception,
    ],
)
async def test_exceptions(exc):
    async def meth():
        raise exc

    sentinel = object()
    fut = meth()
    assert (
        await external_access.wait_for_with_fallback(
            operation_name=f'test_{exc}',
            fut=fut,
            timeout_s=5,
            fallback_value=sentinel,
        )
        == sentinel
    )


async def test_timeout():
    async def slow_function():
        await asyncio.sleep(1)  # never fully-awaited in this test
        return 123

    sentinel = 456
    fut = slow_function()
    assert (
        await external_access.wait_for_with_fallback(
            operation_name=f'test_timeout',
            fut=fut,
            timeout_s=0,
            fallback_value=sentinel,
        )
        == sentinel
    )
