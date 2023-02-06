import pytest

from taxi.internal import distlock


@pytest.inline_callbacks
def test_usage():
    first_owner = 'first_owner'
    second_owner = 'second_owner'
    key = 'unique-key'
    timeout = 100

    # First lock is acquired successfully while others fail
    assert (yield distlock.acquire(key, timeout, first_owner))
    assert not (yield distlock.acquire(key, timeout, second_owner))

    # After releasing lock can be acquired again
    yield distlock.release(key, first_owner)
    assert (yield distlock.acquire(key, timeout, second_owner))


@pytest.inline_callbacks
def test_errors_when_acquired_by_another():
    first_owner = 'first_owner'
    second_owner = 'second_owner'
    key = 'unique-key'
    timeout = 100

    assert (yield distlock.acquire(key, timeout, first_owner))

    with pytest.raises(distlock.ProlongationError):
        yield distlock.prolong(key, timeout, second_owner)

    with pytest.raises(distlock.ReleaseError):
        yield distlock.release(key, second_owner)


@pytest.inline_callbacks
def test_errors_when_removed_by_timeout():
    owner = 'owner'
    key = 'unique-key'
    timeout = 100

    assert (yield distlock.acquire(key, timeout, owner))
    yield distlock.release(key, owner)

    with pytest.raises(distlock.ProlongationError):
        yield distlock.prolong(key, timeout, owner)

    with pytest.raises(distlock.ReleaseError):
        yield distlock.release(key, owner)


def test_default_owner(patch):
    host = 'host'
    pid = 'pid'

    @patch('socket.gethostname')
    def gethostname():
        return host

    @patch('os.getpid')
    def getpid():
        return pid

    expected = '%s-%s' % (host, pid)
    assert distlock.get_default_owner() == expected
