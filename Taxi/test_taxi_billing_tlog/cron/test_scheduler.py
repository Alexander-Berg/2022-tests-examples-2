import datetime as dt

from dateutil import tz
import pytest

from taxi_billing_tlog import scheduler


@pytest.mark.parametrize(
    'event_at, offsets, expected_shift_end',
    [
        # next day
        pytest.param(
            dt.datetime(2020, 3, 17, 12, 0, tzinfo=tz.tzutc()),
            [dt.timedelta(hours=2)],
            dt.datetime(2020, 3, 18, 2, 0, tzinfo=tz.tzutc()),
        ),
        # same day
        pytest.param(
            dt.datetime(2020, 3, 17, 1, 0, tzinfo=tz.tzutc()),
            [dt.timedelta(hours=2)],
            dt.datetime(2020, 3, 17, 2, 0, tzinfo=tz.tzutc()),
        ),
        # first shift
        pytest.param(
            dt.datetime(2020, 3, 17, 1, 0, tzinfo=tz.tzutc()),
            [dt.timedelta(hours=2), dt.timedelta(hours=10)],
            dt.datetime(2020, 3, 17, 2, 0, tzinfo=tz.tzutc()),
        ),
        # second shift
        pytest.param(
            dt.datetime(2020, 3, 17, 3, 0, tzinfo=tz.tzutc()),
            [dt.timedelta(hours=2), dt.timedelta(hours=10)],
            dt.datetime(2020, 3, 17, 10, 0, tzinfo=tz.tzutc()),
        ),
    ],
)
def test_get_shift_end(event_at, offsets, expected_shift_end):
    assert scheduler.get_shift_end(event_at, offsets) == expected_shift_end
