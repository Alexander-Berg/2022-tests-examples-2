import asyncio
from datetime import datetime

from stall.model.event import Event, LOCK_NAME
from stall.model.event_lock import EventLock

async def test_push(tap, mongo):    # pylint: disable=unused-argument
    tap.plan(5)

    ev1 = Event({'key': ['hello'], 'data': {'foo': 'bar'}})

    last_id = await Event.push(ev1)
    tap.isa_ok(last_id, int, 'type last_id')
    tap.ok(last_id > 0, 'last_id')

    tap.eq(ev1.keystr, '["hello"]', 'keystr')
    tap.eq(ev1.data, {'foo': 'bar'}, 'data')


    last_id2 = await Event.push(ev1)
    tap.ok(last_id2 > last_id, 'last_id инкрементируется')
    tap()


async def unlock_after(interval):
    await asyncio.sleep(interval)

    lock = await EventLock.load(LOCK_NAME)

    if lock:
        await lock.unlock()


async def test_race(tap, mongo):    # pylint: disable=unused-argument
    tap.plan(3)
    lock = await EventLock.try_lock(LOCK_NAME)

    tap.ok(lock, 'Блокировка взята')

    task = asyncio.ensure_future(unlock_after(0.5))

    started = datetime.now().timestamp()

    ev1 = Event({'key': ['hello'], 'data': {'foo': 'bar'}})
    last_id = await Event.push(ev1)

    tap.ok(last_id, 'вставлено')

    finished = datetime.now().timestamp()

    tap.ok(finished - started >= 0.5, 'пауза выдержана')
    await task
    tap()
