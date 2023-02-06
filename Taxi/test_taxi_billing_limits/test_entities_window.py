import datetime
import decimal

import pytest

from taxi_billing_limits import limits


@pytest.mark.now('2019-11-10T15:00:00.000000+00:00')
@pytest.mark.parametrize(
    'size,expected',
    (
        (86400, '2019-11-09T21:00:00+00:00'),
        (432000, '2019-11-06T21:00:00+00:00'),
        (604800, '2019-11-08T21:00:00+00:00'),
        (864000, '2019-11-01T21:00:00+00:00'),
    ),
)
def test_tumbling_window(size, expected):
    start = '2019-11-01T21:00:00.000000+00:00'
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    window = limits.TumblingWindow(
        start=datetime.datetime.fromisoformat(start),
        value=decimal.Decimal(1),
        threshold=1,
        label='',
        size=size,
    )
    assert window.begin(now).isoformat() == expected
    assert window.end(now) == now


@pytest.mark.now('2019-11-10T15:00:00.000000+00:00')
@pytest.mark.parametrize(
    'size,expected',
    (
        (86400, '2019-11-09T15:00:00+00:00'),
        (432000, '2019-11-05T15:00:00+00:00'),
        (604800, '2019-11-03T15:00:00+00:00'),
        (864000, '2019-10-31T15:00:00+00:00'),
    ),
)
def test_sliding_window(size, expected):
    now = datetime.datetime.now(tz=datetime.timezone.utc)
    window = limits.SlidingWindow(
        size=size, value=decimal.Decimal(1), threshold=1, label='',
    )
    assert window.begin(now).isoformat() == expected
    assert window.end(now) == now
