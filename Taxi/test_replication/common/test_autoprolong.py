import datetime
import time

import pytest

from taxi.distlock import base

from replication.common import autoprolong


class NetworkError(Exception):
    pass


class Lock(base.DistributedLock):
    def __init__(self):
        super().__init__('key', 1)
        self.prolong_count = 0

    async def _do_prolong(self, db, till: datetime.datetime) -> bool:
        self.prolong_count += 1
        return True

    async def _do_acquire(
            self, db, now: datetime.datetime, till: datetime.datetime,
    ) -> bool:
        pass

    async def release(self, db) -> bool:
        return True

    @property
    def network_error_class(self):
        raise NetworkError


@pytest.mark.nofilldb
async def test_autoprolong():
    lock = Lock()
    with autoprolong.autoprolong(lock, frequency=100):
        time.sleep(1)
    assert lock.prolong_count > 1
