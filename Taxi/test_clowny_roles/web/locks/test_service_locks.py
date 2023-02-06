import datetime

import pytest

from clowny_roles.internal.models import service_lock as lock_models


@pytest.fixture(name='acquire')
def _acquire(taxi_clowny_roles_web):
    async def _wrapper(lock: lock_models.ServiceLock) -> bool:
        response = await taxi_clowny_roles_web.post(
            '/locks/v1/service/acquire/', json=lock.to_api().serialize(),
        )
        assert response.status == 200, await response.json()
        return (await response.json())['acquired']

    return _wrapper


@pytest.fixture(name='release')
def _release(taxi_clowny_roles_web):
    async def _wrapper(lock: lock_models.ServiceLock) -> None:
        response = await taxi_clowny_roles_web.post(
            '/locks/v1/service/release/', json=lock.to_api().serialize(),
        )
        assert response.status == 200, await response.json()

    return _wrapper


async def test_acquire_once(service_lock_fetch_all, acquire):
    lock = lock_models.ServiceLock(1, 'a', datetime.datetime.utcnow())
    assert await acquire(lock)
    assert await service_lock_fetch_all() == [lock]


async def test_acquire_twice_prolong(service_lock_fetch_all, acquire):
    now = datetime.datetime.utcnow()
    assert await acquire(lock_models.ServiceLock(1, 'a', now))
    assert await acquire(
        lock_models.ServiceLock(
            1, 'a', now + datetime.timedelta(minutes=100500),
        ),
    )
    assert await service_lock_fetch_all() == [
        lock_models.ServiceLock(
            1, 'a', now + datetime.timedelta(minutes=100500),
        ),
    ]


async def test_acquire_twice_conflict(service_lock_fetch_all, acquire):
    now = datetime.datetime.utcnow() + datetime.timedelta(minutes=100500)
    assert await acquire(lock_models.ServiceLock(1, 'a', now))
    assert not await acquire(lock_models.ServiceLock(1, 'b', now))
    assert await service_lock_fetch_all() == [
        lock_models.ServiceLock(1, 'a', now),
    ]


async def test_acquire_n_release(service_lock_fetch_all, acquire, release):
    lock = lock_models.ServiceLock(1, 'a', datetime.datetime.utcnow())
    assert await acquire(lock)
    await release(lock)
    assert not await service_lock_fetch_all()


async def test_lock_expires(service_lock_fetch_all, acquire):
    now = datetime.datetime.utcnow()
    assert await acquire(
        lock_models.ServiceLock(
            1, 'a', now - datetime.timedelta(minutes=100500),
        ),
    )
    assert await acquire(
        lock_models.ServiceLock(
            1, 'b', now + datetime.timedelta(minutes=100500),
        ),
    )
    assert await service_lock_fetch_all() == [
        lock_models.ServiceLock(
            1, 'b', now + datetime.timedelta(minutes=100500),
        ),
    ]
