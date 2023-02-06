import asyncio

from taxi.robowarehouse.lib.misc import coroutines


def test_run_sync():
    @coroutines.run_sync
    async def coro():
        await asyncio.sleep(.1)
        return 1, 2, 3

    result = coro()
    assert result == (1, 2, 3)
