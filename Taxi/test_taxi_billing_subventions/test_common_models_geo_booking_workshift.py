import datetime as dt

import pytest

from taxi_billing_subventions.common import intervals
from taxi_billing_subventions.common import models


@pytest.mark.parametrize(
    'quarter_hour_index, duration_in_quarters',
    [(0, 0), (-1, 0), (0, -1), (96, 0), (0, 97), (95, 2)],
)
@pytest.mark.nofilldb()
def test_invalid_ctor_args(quarter_hour_index, duration_in_quarters):
    with pytest.raises(ValueError) as exc:
        models.GeoBookingWorkshift(quarter_hour_index, duration_in_quarters)
    assert exc.type is ValueError


@pytest.mark.parametrize(
    'quarter_hour_index, duration_in_quarters',
    [(0, 1), (0, 96), (40, 56), (95, 1), (1, 95)],
)
@pytest.mark.nofilldb()
def test_valid_ctor_args(quarter_hour_index, duration_in_quarters):
    models.GeoBookingWorkshift(quarter_hour_index, duration_in_quarters)


@pytest.mark.parametrize(
    'quarter_hour_index, duration_in_quarters, expected_start_time, '
    'expected_duration, expected_duration_minutes',
    [
        (0, 96, dt.time(), dt.timedelta(days=1), 1440),
        (95, 1, dt.time(hour=23, minute=45), dt.timedelta(minutes=15), 15),
        (41, 2, dt.time(hour=10, minute=15), dt.timedelta(minutes=30), 30),
        (30, 10, dt.time(hour=7, minute=30), dt.timedelta(minutes=150), 150),
    ],
)
@pytest.mark.nofilldb()
def test_interval(
        quarter_hour_index,
        duration_in_quarters,
        expected_start_time,
        expected_duration,
        expected_duration_minutes,
):
    shift = models.GeoBookingWorkshift(
        quarter_hour_index, duration_in_quarters,
    )
    assert expected_start_time == shift.start_time


@pytest.mark.parametrize(
    'date, workshift, expected',
    [
        (
            dt.date(2018, 12, 10),
            models.GeoBookingWorkshift(5, 10),
            intervals.closed_open(
                dt.datetime(2018, 12, 10, 1, 15),
                dt.datetime(2018, 12, 10, 3, 45),
            ),
        ),
        (
            dt.date(2018, 12, 10),
            models.GeoBookingWorkshift(0, 96),
            intervals.closed_open(
                dt.datetime(2018, 12, 10, 0, 0),
                dt.datetime(2018, 12, 11, 0, 0),
            ),
        ),
    ],
)
def test_on_date(date, workshift, expected):
    assert expected == workshift.on_date(date)


@pytest.mark.parametrize(
    'workshift, expected',
    [
        (models.GeoBookingWorkshift(5, 10), dt.time(3, 45)),
        (models.GeoBookingWorkshift(0, 96), dt.time(0, 0)),
    ],
)
def test_end_time(workshift, expected):
    assert expected == workshift.end_time


@pytest.mark.parametrize(
    'input_dict, expected',
    [
        (
            {'start': '12:45', 'end': '23:45'},
            models.GeoBookingWorkshift(51, 44),
        ),
        (
            {'start': '12:45', 'end': '23:15'},
            models.GeoBookingWorkshift(51, 42),
        ),
        (
            {'start': '00:00', 'end': '00:00'},
            models.GeoBookingWorkshift(0, 96),
        ),
        (
            {'start': '03:15', 'duration': '02:00'},
            models.GeoBookingWorkshift(13, 8),
        ),
        (
            {'start': '07:30', 'duration': '16:30'},
            models.GeoBookingWorkshift(30, 66),
        ),
    ],
)
def test_from_dict(input_dict, expected):
    assert expected == models.GeoBookingWorkshift.from_dict(input_dict)


@pytest.mark.parametrize(
    'input_dict',
    [
        ({'start': '12:45', 'end': '11:45'}),
        ({'start': '07:30', 'duration': '16:45'}),
        ({'start': '07:30', 'duration': '00:00'}),
    ],
)
def test_from_invalid_dict(input_dict):
    with pytest.raises(ValueError) as exc:
        models.GeoBookingWorkshift.from_dict(input_dict)
    assert exc.type is ValueError


@pytest.mark.parametrize(
    'workshift, expected',
    [
        (
            models.GeoBookingWorkshift(0, 96),
            {'start': '00:00', 'end': '00:00'},
        ),
        (
            models.GeoBookingWorkshift(4, 20),
            {'start': '01:00', 'end': '06:00'},
        ),
    ],
)
def test_to_dict(workshift, expected):
    assert expected == workshift.to_dict()
