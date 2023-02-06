import pytest

from taxi.internal import ratelimit


@pytest.mark.parametrize('key,expected_result', [
    ('limit0', True),
    ('limit4', True),
    ('limit4+obsolete', True),
    ('limit5', False),
    ('limit5+ok', True),
])
@pytest.mark.now('2016-06-18T00:00:00')
@pytest.inline_callbacks
def test_ratelimit_limits(key, expected_result, limit=5, seconds=10):
    limiter = ratelimit.RateLimiter(key, limit, seconds)
    result = yield limiter.ratelimit()
    assert result is expected_result


@pytest.mark.now('2016-06-18T00:00:00')
@pytest.inline_callbacks
def test_ratelimit_basic(sleep):
    limiter = ratelimit.RateLimiter('somekey', 5, 10)
    for _ in range(5):
        result = yield limiter.ratelimit()
        assert result
        sleep(1)
    result = yield limiter.ratelimit()
    assert not result
    sleep(6)
    result = yield limiter.ratelimit()
    assert result
