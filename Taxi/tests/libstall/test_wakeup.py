import asyncio
from libstall.wakeup import WakeupTimeout


async def test_sleep(tap):

    tap.plan(2)

    loop = asyncio.get_event_loop()

    started = loop.time()

    wakeup = WakeupTimeout()

    tap.eq(await wakeup.sleep(0.3), None, 'таймаут достигнут')

    finished = loop.time()

    tap.ok(finished - started >= 0.3, 'время ожидания')

    tap()


async def test_wakeup(tap):
    tap.plan(4)
    loop = asyncio.get_event_loop()
    started = loop.time()

    async def wakeup_after(timeout, wakeup):
        await asyncio.sleep(timeout)
        wakeup()

    wakeup = WakeupTimeout()
    asyncio.ensure_future(wakeup_after(0.3, wakeup))

    tap.eq(await wakeup.sleep(3.1), True, 'побудка продетектирована')

    finished = loop.time()

    tap.ok(finished - started >= 0.3, 'время ожидания > 0.3')
    tap.ok(finished - started <= 1, 'время ожидания < 1')

    await wakeup.sleep(3.1)
    finished2 = loop.time()

    tap.ok(finished2 - finished < 0.1, 'второй sleep не работает')
    tap()
