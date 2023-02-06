import asyncio
import os
import signal

import pymongo
import pytest

from taxi import distlock
from taxi.clients import crons
from taxi.distlock import service


@pytest.fixture
def mongodb_collections():
    return ['distlock']


def create_lock(owner='owner', key='unique-key', timeout=100):
    return distlock.DistributedLock(key, timeout, owner)


async def test_acquire(db):
    first_lock = create_lock(owner='first')
    second_lock = create_lock(owner='second')
    assert await first_lock.acquire(db)
    assert not await second_lock.acquire(db)


async def test_release(db):
    first_lock = create_lock(owner='first')
    second_lock = create_lock(owner='second')
    assert await first_lock.acquire(db)
    assert await first_lock.release(db)
    assert await second_lock.acquire(db)


async def test_fails_after_release(db):
    first_lock = create_lock(owner='first')
    assert await first_lock.acquire(db)
    assert await first_lock.release(db)
    assert not await first_lock.prolong(db)
    assert not await first_lock.release(db)


# pylint: disable=protected-access
async def test_prolong(db):
    lock = create_lock()
    assert await lock.acquire(db)
    doc = await db.distlock.find_one({'_id': lock.key})
    assert await lock.prolong(db, 1000)
    new_doc = await db.distlock.find_one({'_id': lock.key})
    prolong_diff = new_doc[lock._LOCKED_TILL] - doc[lock._LOCKED_TILL]
    assert prolong_diff.total_seconds() >= 900


@pytest.mark.parametrize('exception', [None, pymongo.errors.NetworkTimeout])
@pytest.mark.parametrize('error', [True, False])
async def test_autoprolong(error, exception, db, loop, patch):
    pid = os.getpid()
    max_count = 2
    sleep_max_count = max_count + 1  # sleep is made before prolong, so +1
    if exception:
        # if there is an exception, need one more iteration to retry
        sleep_max_count += 1

    @patch('os.kill')
    def kill(pid, sig):
        return

    _shutdown_signals = distlock.base._shutdown_signals

    @patch('taxi.distlock.base._shutdown_signals')
    def _patched_shutdown_signals(sigint_count=3, sigkill_count=None):
        return _shutdown_signals(sigint_count=1, sigkill_count=0)

    class LockMock:
        def __init__(self, timeout):
            self.key = 'key'
            self.count = 0
            self.max_count = max_count
            self.timeout = timeout
            self.error = False
            self.exception_raised = False

        @property
        def network_error_class(self):
            return pymongo.errors.NetworkTimeout

        async def prolong(self, db):
            if self.count < self.max_count:
                self.count += 1
            else:
                if exception and not self.exception_raised:
                    self.exception_raised = True
                    raise exception
                if error:
                    self.error = True
                    return False
            return True

    lock = LockMock(0.1)
    task = loop.create_task(distlock.autoprolong(lock, db, 10))

    sleep_count = 0

    real_sleep = asyncio.sleep

    @patch('asyncio.sleep')
    async def _sleep(amount: int) -> None:
        nonlocal sleep_count
        if sleep_count < sleep_max_count:
            sleep_count += 1
        else:
            task.cancel()
        await real_sleep(0)  # for coroutine switch, provides task cancellation

    await task
    if error:
        assert kill.calls == [{'pid': pid, 'sig': signal.SIGINT}]
    else:
        assert kill.call is None

    assert lock.count == max_count
    assert lock.error == error


@pytest.mark.parametrize('prolong_failed', [True, False])
@pytest.mark.parametrize('reties_exceeded', [True, False])
async def test_service_distlock_autoprolong_fail(
        loop, patch, response_mock, prolong_failed, reties_exceeded,
):
    @patch('os.kill')
    def kill(pid, sig):
        return

    _shutdown_signals = distlock.base._shutdown_signals

    @patch('taxi.distlock.base._shutdown_signals')
    def _patched_shutdown_signals(sigint_count=3, sigkill_count=None):
        return _shutdown_signals(sigint_count=1, sigkill_count=0)

    @patch('taxi.clients.crons.CronsClient._request')
    async def _request_mock(*args, **kwargs):
        if prolong_failed:
            return response_mock(status=404)
        if reties_exceeded:
            raise crons.RequestRetriesExceeded
        return response_mock()

    crons_client = crons.CronsClient('', None)

    lock = service.DistributedLock('key', 0.1)
    task = loop.create_task(distlock.autoprolong(lock, crons_client, 10))

    max_sleep_count = 2
    sleep_count = 0
    real_sleep = asyncio.sleep

    @patch('asyncio.sleep')
    async def _sleep(amount: int) -> None:
        nonlocal sleep_count
        if sleep_count < max_sleep_count:
            sleep_count += 1
        else:
            task.cancel()
        await real_sleep(0)  # for coroutine switch, provides task cancellation

    await task

    if prolong_failed:
        assert kill.calls == [{'pid': os.getpid(), 'sig': signal.SIGINT}]
    else:
        assert kill.call is None
