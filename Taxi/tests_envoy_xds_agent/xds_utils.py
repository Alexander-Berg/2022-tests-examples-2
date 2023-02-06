import asyncio
from typing import Callable

RETRY_WAIT_TIME_INC = 0.2
WAIT_FOR_POLLING_END = 1.1


async def wait_for_new_version(
        new_version: str, async_job: Callable, reties: int = 10,
):
    # 10 reties give more than 11 seconds to retrieve new version
    retry_wait_time = RETRY_WAIT_TIME_INC
    for _ in range(reties):
        response = await async_job()
        if response.version_info == new_version:
            break
        await asyncio.sleep(retry_wait_time)
        retry_wait_time += RETRY_WAIT_TIME_INC

    assert response.version_info == new_version
    return response


async def check_polling_for_new_version(
        async_job: Callable, set_new_version: Callable,
):
    done, pending = await asyncio.wait(
        [async_job()],
        return_when=asyncio.FIRST_COMPLETED,
        timeout=WAIT_FOR_POLLING_END,
    )

    assert not done, 'Version has not changed, but the task returned'

    set_new_version()

    done, pending = await asyncio.wait(
        pending,
        return_when=asyncio.FIRST_COMPLETED,
        timeout=WAIT_FOR_POLLING_END,
    )

    assert done, 'Version has changed, but the task keeps polling'
