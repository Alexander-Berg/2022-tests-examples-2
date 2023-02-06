import datetime as dt

import pytest
import pytz

from taxi_billing_subventions.common import dtintervals as dtints
from taxi_billing_subventions.common import intervals as ints


_MOSCOW_TZ = pytz.timezone('Europe/Moscow')
_LONDON_TZ = pytz.timezone('Europe/London')


@pytest.mark.parametrize(
    'interval, zone, expected',
    [
        (
            ints.closed(
                dt.datetime(2018, 11, 28, tzinfo=pytz.utc),
                dt.datetime(2018, 11, 29, tzinfo=pytz.utc),
            ),
            _MOSCOW_TZ,
            ints.closed(
                _MOSCOW_TZ.localize(dt.datetime(2018, 11, 28, 3)),
                _MOSCOW_TZ.localize(dt.datetime(2018, 11, 29, 3)),
            ),
        ),
    ],
)
def test_astimezone(interval, zone, expected):
    assert expected == dtints.astimezone(interval, zone)


@pytest.mark.parametrize(
    'interval, expected',
    [
        (
            ints.closed(
                _MOSCOW_TZ.localize(dt.datetime(2018, 11, 28, 3)),
                _MOSCOW_TZ.localize(dt.datetime(2018, 11, 29, 3)),
            ),
            ints.closed(
                dt.datetime(2018, 11, 28, tzinfo=pytz.utc),
                dt.datetime(2018, 11, 29, tzinfo=pytz.utc),
            ),
        ),
    ],
)
def test_as_utc(interval, expected):
    assert expected == dtints.as_utc(interval)


@pytest.mark.parametrize(
    'interval, zone, expected',
    [
        (
            ints.closed(dt.datetime(2018, 11, 28), dt.datetime(2018, 11, 29)),
            pytz.utc,
            ints.closed(
                dt.datetime(2018, 11, 28, tzinfo=pytz.utc),
                dt.datetime(2018, 11, 29, tzinfo=pytz.utc),
            ),
        ),
    ],
)
def test_localize(interval, zone, expected):
    assert expected == dtints.localize(interval, zone)


@pytest.mark.parametrize(
    'interval, expected',
    [
        (
            ints.closed(
                dt.datetime(2018, 11, 28, 12), dt.datetime(2018, 11, 28, 15),
            ),
            [
                ints.closed(
                    dt.datetime(2018, 11, 28, 12),
                    dt.datetime(2018, 11, 28, 15),
                ),
            ],
        ),
        (
            ints.closed(
                dt.datetime(2018, 11, 28, 12), dt.datetime(2018, 11, 29, 0),
            ),
            [
                ints.closed_open(
                    dt.datetime(2018, 11, 28, 12),
                    dt.datetime(2018, 11, 29, 0),
                ),
                ints.singleton(dt.datetime(2018, 11, 29, 0)),
            ],
        ),
        (
            ints.closed_open(
                dt.datetime(2018, 11, 28, 12), dt.datetime(2018, 11, 29, 0),
            ),
            [
                ints.closed_open(
                    dt.datetime(2018, 11, 28, 12),
                    dt.datetime(2018, 11, 29, 0),
                ),
            ],
        ),
        (
            ints.closed_open(
                dt.datetime(2018, 11, 28, 12), dt.datetime(2018, 11, 30, 0),
            ),
            [
                ints.closed_open(
                    dt.datetime(2018, 11, 28, 12),
                    dt.datetime(2018, 11, 29, 0),
                ),
                ints.closed_open(
                    dt.datetime(2018, 11, 29, 0), dt.datetime(2018, 11, 30, 0),
                ),
            ],
        ),
        (
            ints.closed(
                dt.datetime(2018, 11, 28, 12), dt.datetime(2018, 11, 30, 15),
            ),
            [
                ints.closed_open(
                    dt.datetime(2018, 11, 28, 12),
                    dt.datetime(2018, 11, 29, 0),
                ),
                ints.closed_open(
                    dt.datetime(2018, 11, 29, 0), dt.datetime(2018, 11, 30, 0),
                ),
                ints.closed(
                    dt.datetime(2018, 11, 30, 0),
                    dt.datetime(2018, 11, 30, 15),
                ),
            ],
        ),
        (
            ints.closed(
                _LONDON_TZ.localize(dt.datetime(2018, 10, 28)),
                _LONDON_TZ.localize(dt.datetime(2018, 10, 30)),
            ),
            [
                ints.closed_open(
                    _LONDON_TZ.localize(dt.datetime(2018, 10, 28)),
                    _LONDON_TZ.localize(dt.datetime(2018, 10, 29)),
                ),
                ints.closed_open(
                    _LONDON_TZ.localize(dt.datetime(2018, 10, 29)),
                    _LONDON_TZ.localize(dt.datetime(2018, 10, 30)),
                ),
                ints.singleton(_LONDON_TZ.localize(dt.datetime(2018, 10, 30))),
            ],
        ),
    ],
)
def test_split_by_midnight(interval, expected):
    assert expected == dtints.split_by_midnight(interval)


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
