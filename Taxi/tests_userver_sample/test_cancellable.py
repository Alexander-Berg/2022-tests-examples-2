import asyncio

import pytest


async def test_cancellable(taxi_userver_sample, testpoint):
    @testpoint('cancelled')
    def cancel_testpoint(data):
        pass

    with pytest.raises(asyncio.TimeoutError):
        await taxi_userver_sample.get('cancellable', timeout=0.1)
    await cancel_testpoint.wait_call()
