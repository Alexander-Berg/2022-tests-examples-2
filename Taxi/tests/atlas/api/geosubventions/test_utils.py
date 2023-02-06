import datetime

import pytest
import pytz
from shapely.geometry import Polygon

from atlas.service_utils.geosubventions.core.utils import (dow_name_to_num, dow_num_to_name, rate_to_datetime,
                                                           rates_to_hours, hours_to_rates, get_all_hours_from_interval,
                                                           split_interval_nonintersecting, hour_to_interval,
                                                           intervals_to_rates, smooth_polygons, get_coords,
                                                           make_localized_date)
from .common import load_test_json

hours = load_test_json('hours.json')
rates = load_test_json('rates.json')
intervals = load_test_json('intervals.json')

dow_test_pairs = [['mon', 1], ['thu', 4], ['sun', 7]]


@pytest.mark.parametrize(
    "name,num",
    dow_test_pairs
)
def test_dow_name_to_num(name,num):
    assert dow_name_to_num(name) == num

@pytest.mark.parametrize(
    "name,num",
    dow_test_pairs
)
def test_dow_num_to_name(name,num):
    assert dow_num_to_name(num) == name


@pytest.mark.parametrize(
    "rate,weekshift,datetime",
    [
        [{'week_day': 'mon', 'start': '19:00'}, 0, datetime.datetime(year=1900, month=1, day=1, hour=19)],
        [{'week_day': 'mon', 'start': '19:15'}, 1, datetime.datetime(year=1900, month=1, day=8, hour=19, minute=15)],
        [{'week_day': 'thu', 'start': '19:00'}, 0, datetime.datetime(year=1900, month=1, day=4, hour=19)],
        [{'week_day': 'thu', 'start': '00:00'}, 1, datetime.datetime(year=1900, month=1, day=11, hour=0)]
    ]
)
def test_rate_to_datetime(rate, weekshift, datetime):
    assert rate_to_datetime(rate, weekshift) == datetime

@pytest.mark.parametrize(
    'hours,rates',
    zip(hours, rates)
)
def test_rates_to_hours(hours, rates):
    current_result = rates_to_hours(rates)
    assert current_result == hours

@pytest.mark.parametrize(
    'hours,expected_rates',
    zip(hours, rates)
)
def test_hours_to_rate_intervals(hours, expected_rates):
    rates = hours_to_rates(hours)
    assert expected_rates == rates


def make_dt(day, hour, month=1, year=1900):
    return datetime.datetime(year=year, month=month, day=day, hour=hour)

def make_interval(start_day, start_hour, end_day, end_hour):
    return (make_dt(start_day, start_hour), make_dt(end_day, end_hour))

def test_get_all_hours_from_interval():
    intervals = [
        [datetime.datetime(year=1900, month=1, day=2, hour=22), datetime.datetime(year=1900, month=1, day=3, hour=2)],
        [datetime.datetime(year=2020, month=2, day=28, hour=23), datetime.datetime(year=2020, month=3, day=1, hour=1)],
        [datetime.datetime(year=1900, month=1, day=7, hour=23), datetime.datetime(year=1900, month=1, day=1, hour=1)],
    ]
    expected_results = [
        [[22, 2], [23, 2], [0, 3], [1, 3]],
        [[23, 5]] + [[i, 6] for i in range(24)] + [[0, 7]],
        [[0, 1], [23, 7]]
    ]


    for interval, expected in zip(intervals, expected_results):
        expected = [{'hour': h[0],'day': h[1]} for h in expected]
        current_result = get_all_hours_from_interval(interval)
        assert current_result == expected



def test_split_interval_nonintersecting():

    intervals = [
        make_interval(1, 1, 1, 6),
        make_interval(1, 3, 1, 5),
        make_interval(1, 4, 1, 8),
        make_interval(7, 23, 1, 2),
        make_interval(1, 1, 1, 2)
    ]
    expected = {
        make_interval(1, 1, 1, 6): [make_interval(1, 1, 1, 2), make_interval(1, 2, 1, 3), make_interval(1, 3, 1, 4),
                                    make_interval(1, 4, 1, 5), make_interval(1, 5, 1, 6)],
        make_interval(1, 3, 1, 5): [make_interval(1, 3, 1, 4), make_interval(1, 4, 1, 5)],
        make_interval(1, 4, 1, 8): [make_interval(1, 4, 1, 5), make_interval(1, 5, 1, 6), make_interval(1, 6, 1 , 8)],
        make_interval(7, 23, 1, 2): [make_interval(7, 23, 1, 1), make_interval(1, 1, 1, 2)],
        make_interval(1, 1, 1, 2): [make_interval(1, 1, 1, 2)]
    }
    splitted = split_interval_nonintersecting(intervals)
    assert splitted == expected


def test_hour_to_interval():
    assert make_interval(4, 1, 4, 2) == hour_to_interval(1, 4)
    assert make_interval(7, 23, 1, 0) == hour_to_interval(23, 7)


@pytest.mark.parametrize(
    'intervals,expected_rates',
    zip(intervals, rates)
)
def test_intervals_to_rates(intervals, expected_rates):
    parsed_intervals = [
        {
            'interval': (make_dt(*interval[0][0]), make_dt(*interval[0][1])),
            'bonus_amount': interval[1]
        }
        for interval in intervals]
    assert expected_rates == intervals_to_rates(parsed_intervals)


@pytest.mark.parametrize(
    "date_str, time_zone_str, drop_seconds, expected",
    [
        [
            "2020-11-24T12:16:12",
            "Europe/Moscow",
            True,
            datetime.datetime(year=2020, month=11, day=24, hour=12, minute=16, second=0, microsecond=0)
        ],
        [
            "2020-11-24T12:16:12",
            "Europe/Moscow",
            False,
            datetime.datetime(year=2020, month=11, day=24, hour=12, minute=16, second=12, microsecond=0)
        ],
    ]
)
def test_make_localized_date(date_str, time_zone_str, drop_seconds, expected):
    time_zone = pytz.timezone('Europe/Moscow')
    expected = time_zone.localize(expected)
    result = make_localized_date(date_str, time_zone, drop_seconds=drop_seconds)
    assert result == expected


def test_smooth_polygon():
    p = Polygon([(0, 0), (3, 3), (4, 2), (5, 3), (12, 0)])

    smoothed = smooth_polygons({'pol1': p}, 4)
    assert smoothed == {'pol1': Polygon([[0.0, 0.0], [3.0, 3.0], [5.0, 3.0], [12.0, 0.0], [0.0, 0.0]])}
    smoothed = smooth_polygons({'pol1': p}, 3)
    assert smoothed == {'pol1': Polygon([[0.0, 0.0], [5.0, 3.0], [12.0, 0.0], [0.0, 0.0]])}
    neighbour = Polygon([[3.5, 2.7], [3.5, 3.5], [4.5, 3.5], [4.5, 2.7], [3.5, 2.7]])
    smoothed = smooth_polygons({'pol1': p, 'pol2': neighbour}, 4)
    assert smoothed == {'pol1': Polygon([[0.0, 0.0], [4.0, 2.0], [5.0, 3.0], [12.0, 0.0], [0.0, 0.0]]),
                        'pol2': neighbour}

