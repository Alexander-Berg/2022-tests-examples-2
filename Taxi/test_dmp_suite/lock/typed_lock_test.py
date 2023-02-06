import datetime as dt
import time
import uuid

import pytest

from connection import pgaas
from dmp_suite.lock.typed_lock import lock as typed_lock
from dmp_suite.lock.typed_lock import entities
from dmp_suite.lock.typed_lock import errors
from dmp_suite.lock.typed_lock import lock_utils
from dmp_suite.lock.typed_lock import pg_dao


def _get_ctl_connection():
    return pgaas.get_pgaas_connection('ctl', writable=True)


def test_merge_locks():
    merged = lock_utils.merge_locks([
        entities.LockInfo('key', entities.LockMode.SHARED),
        entities.LockInfo('key', entities.LockMode.SHARED),
    ])
    assert merged == [entities.LockInfo('key', entities.LockMode.SHARED)]

    merged = lock_utils.merge_locks([
        entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
        entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
    ])
    assert merged == [entities.LockInfo('key', entities.LockMode.EXCLUSIVE)]

    merged = lock_utils.merge_locks([
        entities.LockInfo('key', entities.LockMode.SHARED),
        entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
    ])
    assert merged == [entities.LockInfo('key', entities.LockMode.EXCLUSIVE)]

    merged = lock_utils.merge_locks([
        entities.LockInfo('key', entities.LockMode.SHARED),
        entities.LockInfo('other_key', entities.LockMode.EXCLUSIVE),
    ])
    assert set(merged) == {
        entities.LockInfo('key', entities.LockMode.SHARED),
        entities.LockInfo('other_key', entities.LockMode.EXCLUSIVE),
    }

    merged = lock_utils.merge_locks([
        entities.LockInfo('key', entities.LockMode.SHARED),
        entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
        entities.LockInfo('other_key', entities.LockMode.EXCLUSIVE),
    ])
    assert set(merged) == {
        entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
        entities.LockInfo('other_key', entities.LockMode.EXCLUSIVE),
    }


def test_error_on_duplicate_keys():
    with pytest.raises(
            ValueError,
            match='Requested duplicate lock for key "key"',
    ):
        typed_lock.TypedBatchLock(
            entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
            entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
        )


def test_error_on_invalid_prolongation_interval():
    with pytest.raises(
            ValueError,
            match='prolongation_interval must be lesser than ttl',
    ):
        typed_lock.TypedBatchLock(
            entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
            ttl=dt.timedelta(minutes=1),
            prolongation_interval=dt.timedelta(minutes=1),
        )


def test_error_on_invalid_acquire_interval():
    with pytest.raises(
            ValueError,
            match='acquire_timeout must be greater than acquire_interval',
    ):
        typed_lock.TypedBatchLock(
            entities.LockInfo('key', entities.LockMode.EXCLUSIVE),
            acquire_timeout=dt.timedelta(minutes=1),
            acquire_interval=dt.timedelta(minutes=1),
        )


def test_error_on_release_not_acquired_lock():
    key = uuid.uuid4().hex

    lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
    )
    with pytest.raises(errors.NothingToReleaseError):
        lock.release()


def test_success_on_prolong_not_acquired_lock():
    key = uuid.uuid4().hex

    lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
    )

    assert lock.prolong() is True


@pytest.mark.slow
def test_simple_lock_flow():
    ttl = dt.timedelta(minutes=1)
    requested_locks = (
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.SHARED),
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.SHARED),
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.EXCLUSIVE),
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.EXCLUSIVE),
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.EXCLUSIVE),
    )

    requested_locks_by_keys = {rl.key: rl for rl in requested_locks}
    requested_keys = list(requested_locks_by_keys.keys())

    lock = typed_lock.TypedBatchLock(
        *requested_locks,
        ttl=ttl,
    )
    connection = _get_ctl_connection()
    dao = pg_dao.TypedLockDAO(connection)

    acquired_locks = dao.get_locks_debug_info(*requested_keys)
    assert not acquired_locks

    lock.acquire()

    acquired_locks = dao.get_locks_debug_info(*requested_keys)
    assert len(acquired_locks) == len(requested_locks)
    acquired_locks_by_keys = {al.key: al for al in acquired_locks}

    for prolonged_lock in acquired_locks:
        assert prolonged_lock.key in requested_locks_by_keys
        assert (
                prolonged_lock.mode
                == requested_locks_by_keys[prolonged_lock.key].mode
        )
        assert prolonged_lock.id is not None
        assert prolonged_lock.utc_expiration_dttm is not None
        assert prolonged_lock.utc_created_dttm is not None
        assert prolonged_lock.utc_updated_dttm is not None
        assert (
                prolonged_lock.utc_expiration_dttm
                == prolonged_lock.utc_created_dttm + ttl
        )

    lock.prolong()

    prolonged_locks = dao.get_locks_debug_info(*requested_keys)
    assert len(prolonged_locks) == len(prolonged_locks)

    for prolonged_lock in prolonged_locks:
        key = prolonged_lock.key
        assert key in acquired_locks_by_keys
        assert prolonged_lock.mode == acquired_locks_by_keys[key].mode
        assert prolonged_lock.id == acquired_locks_by_keys[key].id
        assert (
                prolonged_lock.utc_expiration_dttm
                > acquired_locks_by_keys[key].utc_expiration_dttm
        )
        assert (
                prolonged_lock.utc_created_dttm
                == acquired_locks_by_keys[key].utc_created_dttm
        )
        assert (
                prolonged_lock.utc_updated_dttm
                > acquired_locks_by_keys[key].utc_updated_dttm
        )

    lock.release()

    prolonged_locks = dao.get_locks_debug_info(*requested_keys)
    assert not prolonged_locks


@pytest.mark.slow
def test_batch_is_atomic():
    key = uuid.uuid4().hex
    requested_locks = (
        entities.LockInfo(key, entities.LockMode.SHARED),
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.SHARED),
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.EXCLUSIVE),
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.EXCLUSIVE),
        entities.LockInfo(uuid.uuid4().hex, entities.LockMode.EXCLUSIVE),
    )

    single_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
    )

    batch_lock = typed_lock.TypedBatchLock(
        *requested_locks,
    )

    with single_lock:
        with pytest.raises(errors.LockConflictError):
            batch_lock.acquire()


@pytest.mark.slow
def test_lock_flow_ctx_manager():
    key = uuid.uuid4().hex
    lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
        prolongation_interval=dt.timedelta(seconds=1),
    )
    with lock:
        pass


@pytest.mark.slow
def test_exclusive_lock_flow():
    key = uuid.uuid4().hex
    first_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
    )
    second_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
    )
    first_lock.acquire()

    with pytest.raises(errors.LockConflictError):
        second_lock.acquire()

    first_lock.release()

    second_lock.acquire()
    second_lock.release()


@pytest.mark.slow
def test_shared_lock_flow():
    key = uuid.uuid4().hex
    first_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.SHARED),
    )
    second_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.SHARED),
    )
    first_lock.acquire()
    second_lock.acquire()
    first_lock.release()
    second_lock.release()


@pytest.mark.slow
def test_conflict_shared_exclusive():
    key = uuid.uuid4().hex
    first_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.SHARED),
    )
    second_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
    )
    first_lock.acquire()
    with pytest.raises(errors.LockConflictError):
        second_lock.acquire()
    first_lock.release()

    second_lock.acquire()
    second_lock.release()


@pytest.mark.slow
def test_conflict_exclusive_shared():
    key = uuid.uuid4().hex
    first_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
    )
    second_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.SHARED),
    )
    first_lock.acquire()
    with pytest.raises(errors.LockConflictError):
        second_lock.acquire()
    first_lock.release()

    second_lock.acquire()
    second_lock.release()


@pytest.mark.slow
def test_prolongation():
    connection = _get_ctl_connection()
    dao = pg_dao.TypedLockDAO(connection)

    key = uuid.uuid4().hex
    lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.SHARED),
        connection_factory=_get_ctl_connection,
        prolongation_interval=dt.timedelta(milliseconds=200),
    )

    with lock:
        acquired_locks_at_start = dao.get_locks_debug_info(key)
        assert len(acquired_locks_at_start) == 1
        expiration_at_start = acquired_locks_at_start[0].utc_expiration_dttm
        time.sleep(2)
        acquired_locks_at_end = dao.get_locks_debug_info(key)
        expiration_at_end = acquired_locks_at_end[0].utc_expiration_dttm
        assert expiration_at_end > expiration_at_start


@pytest.mark.slow
def test_acquire_expired_key():
    connection = _get_ctl_connection()
    dao = pg_dao.TypedLockDAO(connection)

    key = uuid.uuid4().hex
    dao.acquire(
        dt.timedelta(seconds=0),
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
    )

    lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
        connection_factory=_get_ctl_connection,
    )

    lock.acquire()
    lock.release()


@pytest.mark.slow
def test_error_on_release_non_existed_lock():
    key = uuid.uuid4().hex
    connection = _get_ctl_connection()
    dao = pg_dao.TypedLockDAO(connection)

    lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
        connection_factory=_get_ctl_connection,
    )

    lock.acquire()
    dao.release(*lock._acquired_locks)

    with pytest.raises(errors.LockNotFoundError):
        lock.release()


@pytest.mark.slow
def test_error_on_prolong_non_existed_lock():
    key = uuid.uuid4().hex
    connection = _get_ctl_connection()
    dao = pg_dao.TypedLockDAO(connection)

    lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
        connection_factory=_get_ctl_connection,
    )

    lock.acquire()
    dao.release(*lock._acquired_locks)

    with pytest.raises(errors.LockNotFoundError):
        lock.prolong()


@pytest.mark.slow
def test_lock_acquire_timeout():
    key = uuid.uuid4().hex
    ttl = dt.timedelta(seconds=2)
    timeout = dt.timedelta(seconds=5)

    first_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
        connection_factory=_get_ctl_connection,
        ttl=ttl,
        prolongation_interval=dt.timedelta(milliseconds=100),
    )

    second_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
        connection_factory=_get_ctl_connection,
        acquire_timeout=timeout,
        acquire_interval=dt.timedelta(seconds=0.5),
    )

    first_lock.acquire()

    start = time.monotonic()
    second_lock.acquire()  # will be acquired due to first lock expiration
    end = time.monotonic()

    assert end - start > ttl.total_seconds()

    # key is same for first and second
    second_lock.release()


@pytest.mark.slow
def test_lock_acquire_timeout_error():
    key = uuid.uuid4().hex
    timeout = dt.timedelta(seconds=3)

    first_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
        connection_factory=_get_ctl_connection,
    )

    second_lock = typed_lock.TypedBatchLock(
        entities.LockInfo(key, entities.LockMode.EXCLUSIVE),
        connection_factory=_get_ctl_connection,
        acquire_timeout=timeout,
        acquire_interval=dt.timedelta(seconds=0.5),
    )

    with first_lock:
        start = time.monotonic()
        with pytest.raises(errors.LockAcquireTimeoutError):
            second_lock.acquire()
        end = time.monotonic()

    assert end - start > timeout.total_seconds()
