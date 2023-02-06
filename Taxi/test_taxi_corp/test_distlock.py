import asyncio
import os
import signal

import pymongo
import pytest

from taxi_corp.api.common import distlock

CUSTOM_LOCK_COLLECTION = 'corp_clients'


def create_lock(
        db,
        owner='owner',
        key='unique-key',
        timeout=100,
        lock_collection_name=None,
):
    return distlock.DistributedLock(
        key, timeout, db, owner, lock_collection_name=lock_collection_name,
    )


@pytest.mark.parametrize(
    'lock_collection_name', [None, CUSTOM_LOCK_COLLECTION],
)
async def test_acquire(db, lock_collection_name):
    first_lock = create_lock(
        db, owner='first', lock_collection_name=lock_collection_name,
    )
    second_lock = create_lock(
        db, owner='second', lock_collection_name=lock_collection_name,
    )
    assert await first_lock.acquire()
    assert not await second_lock.acquire()


@pytest.mark.parametrize(
    'lock_collection1, lock_collection2', [(None, CUSTOM_LOCK_COLLECTION)],
)
async def test_acquire_diff_collections(
        db, lock_collection1, lock_collection2,
):
    first_lock = create_lock(
        db, owner='first', lock_collection_name=lock_collection1,
    )
    second_lock = create_lock(
        db, owner='second', lock_collection_name=lock_collection2,
    )
    assert await first_lock.acquire()
    assert await second_lock.acquire()


@pytest.mark.parametrize(
    'lock_collection_name', [None, CUSTOM_LOCK_COLLECTION],
)
async def test_release(db, lock_collection_name):
    first_lock = create_lock(
        db, owner='first', lock_collection_name=lock_collection_name,
    )
    second_lock = create_lock(
        db, owner='second', lock_collection_name=lock_collection_name,
    )
    assert await first_lock.acquire()
    assert await first_lock.release()
    assert await second_lock.acquire()
    assert await second_lock.release()


@pytest.mark.parametrize(
    'lock_collection_name', [None, CUSTOM_LOCK_COLLECTION],
)
async def test_fails_after_release(db, lock_collection_name):
    first_lock = create_lock(
        db, owner='first', lock_collection_name=lock_collection_name,
    )
    assert await first_lock.acquire()
    assert await first_lock.release()
    assert not await first_lock.prolong()
    assert not await first_lock.release()


# pylint: disable=protected-access
@pytest.mark.parametrize(
    'lock_collection_name', [None, CUSTOM_LOCK_COLLECTION],
)
async def test_prolong(db, lock_collection_name):
    lock = create_lock(db, lock_collection_name=lock_collection_name)
    lock_collection = lock._get_lock_collection()

    assert await lock.acquire()
    doc = await lock_collection.find_one({'_id': lock.key})
    assert await lock.prolong(1000)
    new_doc = await lock_collection.find_one({'_id': lock.key})
    prolong_diff = new_doc[lock._LOCKED_TILL] - doc[lock._LOCKED_TILL]
    assert prolong_diff.total_seconds() >= 900


@pytest.mark.parametrize('exception', [None, pymongo.errors.NetworkTimeout])
@pytest.mark.parametrize('error', [True, False])
async def test_autoprolong(error, exception, db, loop, patch):
    pid = os.getpid()
    max_count = 2

    @patch('os.kill')
    def kill(pid, sig):
        return

    class LockMock:
        def __init__(self, timeout):
            self.key = 'key'
            self.count = 0
            self.max_count = max_count
            self.timeout = timeout
            self.db = db
            self.error = False
            self.exception_raised = False

        @property
        def network_error_class(self):
            return pymongo.errors.NetworkTimeout

        async def prolong(self):
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
    task = loop.create_task(distlock.autoprolong(lock, 10))

    await asyncio.sleep(0.5)
    task.cancel()
    await task
    if error:
        assert kill.calls == [{'pid': pid, 'sig': signal.SIGINT}]
    else:
        assert kill.call is None

    assert lock.count == max_count
    assert lock.error == error
