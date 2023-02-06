import datetime as dt

import intervals.dtintervals as dtints
import intervals.intervals as ints


def test_duration():
    assert dt.timedelta(days=1) == dtints.duration(
        ints.closed(dt.datetime(2018, 11, 29), dt.datetime(2018, 11, 30)),
    )
    assert dt.timedelta(days=1) == dtints.duration(
        ints.closed_open(dt.datetime(2018, 11, 29), dt.datetime(2018, 11, 30)),
    )


def test_total_duration():
    assert dt.timedelta(days=2) == dtints.total_duration(
        [
            ints.closed(dt.datetime(2018, 11, 29), dt.datetime(2018, 11, 30)),
            ints.closed(dt.datetime(2018, 12, 1), dt.datetime(2018, 12, 2)),
        ],
    )
