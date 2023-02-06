from stall.model.event_lock import EventLock

async def test_lock(tap, uuid, mongo): # pylint: disable=unused-argument
    tap.plan(12)
    name = uuid()

    tap.ok(not await EventLock.load(name), 'нет блокировки в БД')

    lock = await EventLock.try_lock(name)
    tap.ok(lock, 'блокировка получена')

    loaded = await EventLock.load(name)
    tap.ok(loaded, 'загружено')

    tap.eq(loaded.name, name, 'name')
    tap.ok(loaded.locked, 'заблокировано')

    lock2 = await EventLock.try_lock(name)
    tap.ok(not lock2, 'вторая такая же не получается')

    tap.eq(lock.data, 0, 'data')

    tap.isa_ok(await lock.unlock(27), EventLock, 'unlock')
    tap.eq(lock.data, 27, 'данные в БД')

    dbload = await EventLock.load(name)
    tap.isa_ok(dbload, EventLock, 'загружено')
    tap.ok(not dbload, 'загружена блокировка, незаблокировано')
    tap.eq(dbload.data, 27, 'данные в БД')

    tap()
