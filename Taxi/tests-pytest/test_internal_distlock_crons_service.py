import pytest

from taxi.core import arequests
from taxi.core import async
from taxi.internal import distlock_crons_service as distlock
from taxi.util import dates


@pytest.fixture(autouse=True)
def crons_service_mock(request, areq_request):
    locks = {}

    service_network_error = bool(
        request.node.get_marker('distlock_service_error')
    )

    @areq_request
    def requests_mock(method, url, *args, **kwargs):
        if service_network_error:
            raise arequests.BaseError
        data = kwargs['json']
        lock_key = (data['key'],)
        now = data.get('now')
        till = data.get('till')
        if now and till:
            assert dates.parse_timestring(now) < dates.parse_timestring(till)

        if 'aquire' in url:
            if lock_key not in locks:
                locks[lock_key] = data.copy()
                return areq_request.response(200)
            lock = locks[lock_key]
            lock_expires = (
                dates.parse_timestring(lock['till']) <=
                dates.parse_timestring(now)
            )
            if lock['owner'] == data['owner'] or lock_expires:
                lock['till'] = till
                lock['owner'] = data['owner']
                return areq_request.response(200)
            return areq_request.response(423)

        if 'release' in url:
            if lock_key not in locks:
                return areq_request.response(404)
            lock = locks[lock_key]
            if lock['owner'] != data['owner']:
                return areq_request.response(404)
            locks.pop(lock_key)
            return areq_request.response(200)

        if 'prolong' in url:
            if lock_key not in locks:
                return areq_request.response(404)
            lock = locks[lock_key]
            if lock['owner'] != data['owner']:
                return areq_request.response(404)
            lock['till'] = till
            return areq_request.response(200)


@pytest.inline_callbacks
def test_usage():
    first_owner = 'first_owner'
    second_owner = 'second_owner'
    key = 'unique-key'
    timeout = 100

    lock = distlock.Distlock('task_name')

    # First lock is acquired successfully while others fail
    assert (yield lock.acquire(key, timeout, first_owner))
    assert not (yield lock.acquire(key, timeout, second_owner))

    # After releasing lock can be acquired again
    yield lock.release(key, first_owner)
    assert (yield lock.acquire(key, timeout, second_owner))


@pytest.inline_callbacks
def test_errors_when_acquired_by_another():
    first_owner = 'first_owner'
    second_owner = 'second_owner'
    key = 'unique-key'
    timeout = 100

    lock = distlock.Distlock('task_name')

    assert (yield lock.acquire(key, timeout, first_owner))

    # cant prolong lock, if ur not the owner
    with pytest.raises(distlock.distlock.ProlongationError):
        yield lock.prolong(key, timeout, second_owner)

    # cant release lock, if ur not the owner
    with pytest.raises(distlock.distlock.ReleaseError):
        yield lock.release(key, second_owner)


@pytest.inline_callbacks
def test_errors_after_release():
    owner = 'owner'
    key = 'unique-key'
    timeout = 100

    lock = distlock.Distlock('task_name')

    assert (yield lock.acquire(key, timeout, owner))
    yield lock.release(key, owner)

    with pytest.raises(distlock.distlock.ProlongationError):
        yield lock.prolong(key, timeout, owner)

    with pytest.raises(distlock.distlock.ReleaseError):
        yield lock.release(key, owner)


@pytest.inline_callbacks
@pytest.mark.distlock_service_error
def test_network_error_fallback(patch):
    @patch('taxi.internal.distlock.acquire')
    @async.inline_callbacks
    def acquire(key, timeout, owner=None):
        yield
        async.return_value(True)

    @patch('taxi.internal.distlock.prolong')
    @async.inline_callbacks
    def prolong(key, timeout, owner=None):
        yield

    @patch('taxi.internal.distlock.release')
    @async.inline_callbacks
    def release(key, owner=None):
        yield

    owner = 'owner'
    key = 'unique-key'
    timeout = 100

    lock = distlock.Distlock('task_name', log_extra={})
    assert (yield lock.acquire(key, timeout, owner))
    yield lock.prolong(key, timeout, owner)
    yield lock.release(key, owner)

    assert acquire.call is not None
    assert prolong.call is not None
    assert release.call is not None
