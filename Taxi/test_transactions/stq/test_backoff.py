# pylint: disable=redefined-outer-name,unused-variable
import pytest

from transactions.stq import backoff


@pytest.mark.nofilldb
@pytest.mark.parametrize(
    'count, max_count, expected', [(0, 10, 150), (11, 10, 450)],
)
def test_for_trust_error(patch_random, count, max_count, expected):
    actual = backoff.for_trust_error(
        count=count, max_count=max_count, min_interval=300, max_interval=900,
    )
    assert actual == pytest.approx(expected)


@pytest.mark.nofilldb
@pytest.mark.parametrize('delay, expected', [(100, 50)])
def test_for_rate_limit_exceeded(patch_random, delay, expected):
    actual = backoff.for_trust_rate_limit_exceeded(delay)
    assert actual == pytest.approx(expected)


@pytest.fixture
def patch_random(patch):
    @patch('random.random')
    def random():
        return 0
