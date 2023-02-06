import datetime

from clowny_roles.internal.models import service_lock as lock_models


async def test_acquire_once(service_lock_acquire, service_lock_fetch_all):
    lock = lock_models.ServiceLock(1, 'a', datetime.datetime.utcnow())
    assert await service_lock_acquire(lock)
    assert await service_lock_fetch_all() == [lock]


async def test_acquire_twice_prolong(
        service_lock_acquire, service_lock_fetch_all,
):
    now = datetime.datetime.utcnow()
    assert await service_lock_acquire(lock_models.ServiceLock(1, 'a', now))
    assert await service_lock_acquire(
        lock_models.ServiceLock(
            1, 'a', now + datetime.timedelta(minutes=100500),
        ),
    )
    assert await service_lock_fetch_all() == [
        lock_models.ServiceLock(
            1, 'a', now + datetime.timedelta(minutes=100500),
        ),
    ]


async def test_acquire_twice_conflict(
        service_lock_acquire, service_lock_fetch_all,
):
    now = datetime.datetime.utcnow() + datetime.timedelta(minutes=100500)
    assert await service_lock_acquire(lock_models.ServiceLock(1, 'a', now))
    assert not await service_lock_acquire(lock_models.ServiceLock(1, 'b', now))
    assert await service_lock_fetch_all() == [
        lock_models.ServiceLock(1, 'a', now),
    ]


async def test_acquire_n_release(
        service_lock_acquire, service_lock_release, service_lock_fetch_all,
):
    lock = lock_models.ServiceLock(1, 'a', datetime.datetime.utcnow())
    assert await service_lock_acquire(lock)
    await service_lock_release(lock)
    assert not await service_lock_fetch_all()


async def test_lock_expires(service_lock_acquire, service_lock_fetch_all):
    now = datetime.datetime.utcnow()
    assert await service_lock_acquire(
        lock_models.ServiceLock(
            1, 'a', now - datetime.timedelta(minutes=100500),
        ),
    )
    assert await service_lock_acquire(
        lock_models.ServiceLock(
            1, 'b', now + datetime.timedelta(minutes=100500),
        ),
    )
    assert await service_lock_fetch_all() == [
        lock_models.ServiceLock(
            1, 'b', now + datetime.timedelta(minutes=100500),
        ),
    ]
