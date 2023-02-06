import datetime

import pytest

from taxi.util import ratelimit


@pytest.fixture
def mongodb_collections():
    return ['antifraud_ratelimit_tokens']


@pytest.mark.parametrize(
    'key,expected_result',
    [
        ('limit0', True),
        ('limit4', True),
        ('limit4+obsolete', True),
        ('limit5', False),
        ('limit5+ok', True),
    ],
)
@pytest.mark.now('2016-06-18T00:00:00')
async def test_ratelimit_limits(db, key, expected_result):
    limiter = ratelimit.RateLimiter(
        db.antifraud_ratelimit_tokens, key, limit=5, time=10, refill=1,
    )
    result = await limiter.reduce()
    assert result is expected_result


@pytest.mark.now('2016-06-18T00:00:00')
async def test_ratelimit_basic(monkeypatch, db):
    # 5 calls over 10 seconds == 0.5 calls per second, max 5 call bursts
    limiter = ratelimit.RateLimiter(
        db.antifraud_ratelimit_tokens, 'somekey', 5, 10, 5,
    )
    # starting with 5 tokens, 5 calls over 5 seconds
    for _ in range(5):
        result = await limiter.reduce()
        assert result
        _sleep(monkeypatch, 1)
    # here wet should
    # - hit zero
    # - refill with 2.5 tokens
    # - allow call, using 1 token
    # - leave 1.5 tokens
    result = await limiter.reduce()
    assert result
    # 1.5 tokens
    result = await limiter.reduce()
    assert result
    # 0.5 token - this call fails
    result = await limiter.reduce()
    assert not result
    # wait 1 second to refill 0.5 tokens
    _sleep(monkeypatch, 1)
    # one call succeeds
    result = await limiter.reduce()
    assert result
    # next fails
    result = await limiter.reduce()
    assert not result


def _sleep(monkeypatch, seconds):
    time = datetime.datetime.utcnow() + datetime.timedelta(seconds=seconds)
    monkeypatch.setattr(datetime.datetime, 'utcnow', lambda: time)
