import datetime

import pytest
import pytz
import shapely.geometry as shapely_geo

from operation_calculations.geosubventions.calculators import (
    experiment_transformer as exp_utils,
)
import operation_calculations.geosubventions.calculators.utils as utils

DOW_TEST_PAIRS = [['mon', 1], ['thu', 4], ['sun', 7]]


@pytest.mark.parametrize('name,num', DOW_TEST_PAIRS)
def test_dow_name_to_num(name, num):
    assert utils.dow_name_to_num(name) == num


@pytest.mark.parametrize('name,num', DOW_TEST_PAIRS)
def test_dow_num_to_name(name, num):
    assert utils.dow_num_to_name(num) == name


@pytest.mark.parametrize(
    'rate,weekshift, dtime',
    [
        [
            {'week_day': 'mon', 'start': '19:00'},
            0,
            datetime.datetime(year=1900, month=1, day=1, hour=19),
        ],
        [
            {'week_day': 'mon', 'start': '19:15'},
            1,
            datetime.datetime(year=1900, month=1, day=8, hour=19, minute=15),
        ],
        [
            {'week_day': 'thu', 'start': '19:00'},
            0,
            datetime.datetime(year=1900, month=1, day=4, hour=19),
        ],
        [
            {'week_day': 'thu', 'start': '00:00'},
            1,
            datetime.datetime(year=1900, month=1, day=11, hour=0),
        ],
    ],
)
def test_rate_to_datetime(rate, weekshift, dtime):
    assert utils.rate_to_datetime(rate, weekshift) == dtime


def test_rates_to_hours(load_json):
    hour_data = load_json('hours.json')
    rates_data = load_json('rates.json')
    for hours, rates in zip(hour_data, rates_data):
        current_result = utils.rates_to_hours(rates)
        assert current_result == hours


def test_rates_to_intervals(load_json):
    rates_data = load_json('rates.json')
    intervals = load_json('intervals_condense.json')

    def interval_tuple(interval):
        return [
            [
                [interval[0][0].weekday() + 1, interval[0][0].hour],
                [interval[0][1].weekday() + 1, interval[0][1].hour],
            ],
            float(interval[1]),
        ]

    for rates, intervals in zip(rates_data, intervals):
        current_intervals = [
            interval_tuple(interval)
            for interval in utils.rates_to_intervals(rates)
        ]
        assert intervals == current_intervals


def test_hours_to_rate_intervals(load_json):
    hour_data = load_json('hours.json')
    rates_data = load_json('rates.json')
    for hours, rates in zip(hour_data, rates_data):
        current_rates = utils.hours_to_rates(hours)
        assert current_rates == rates


def test_intervals_to_rates(load_json):
    intervals_data = load_json('intervals.json')
    rates_data = load_json('rates.json')
    for intervals, rates in zip(intervals_data, rates_data):
        parsed_intervals = [
            {
                'interval': (
                    make_dt(*interval[0][0]),
                    make_dt(*interval[0][1]),
                ),
                'bonus_amount': interval[1],
            }
            for interval in intervals
        ]
        assert rates == utils.intervals_to_rates(parsed_intervals)


def make_dt(day, hour, month=1, year=1900):
    return datetime.datetime(year=year, month=month, day=day, hour=hour)


def make_interval(start_day, start_hour, end_day, end_hour):
    return (make_dt(start_day, start_hour), make_dt(end_day, end_hour))


def test_get_all_hours_from_interval():
    intervals = [
        [
            datetime.datetime(year=1900, month=1, day=2, hour=22),
            datetime.datetime(year=1900, month=1, day=3, hour=2),
        ],
        [
            datetime.datetime(year=2020, month=2, day=28, hour=23),
            datetime.datetime(year=2020, month=3, day=1, hour=1),
        ],
        [
            datetime.datetime(year=1900, month=1, day=7, hour=23),
            datetime.datetime(year=1900, month=1, day=1, hour=1),
        ],
    ]
    expected_results = [
        [[22, 2], [23, 2], [0, 3], [1, 3]],
        [[23, 5]] + [[i, 6] for i in range(24)] + [[0, 7]],
        [[0, 1], [23, 7]],
    ]

    for interval, expected in zip(intervals, expected_results):
        expected = [{'hour': h[0], 'day': h[1]} for h in expected]
        current_result = utils.get_all_hours_from_interval(interval)
        assert current_result == expected


def test_split_interval_nonintersecting():

    intervals = [
        make_interval(1, 1, 1, 6),
        make_interval(1, 3, 1, 5),
        make_interval(1, 4, 1, 8),
        make_interval(7, 23, 1, 2),
        make_interval(1, 1, 1, 2),
    ]
    expected = {
        make_interval(1, 1, 1, 6): {
            make_interval(1, 1, 1, 2),
            make_interval(1, 2, 1, 3),
            make_interval(1, 3, 1, 4),
            make_interval(1, 4, 1, 5),
            make_interval(1, 5, 1, 6),
        },
        make_interval(1, 3, 1, 5): {
            make_interval(1, 3, 1, 4),
            make_interval(1, 4, 1, 5),
        },
        make_interval(1, 4, 1, 8): {
            make_interval(1, 4, 1, 5),
            make_interval(1, 5, 1, 6),
            make_interval(1, 6, 1, 8),
        },
        make_interval(7, 23, 1, 2): {
            make_interval(7, 23, 1, 1),
            make_interval(1, 1, 1, 2),
        },
        make_interval(1, 1, 1, 2): {make_interval(1, 1, 1, 2)},
    }
    splitted = utils.split_interval_nonintersecting(intervals)
    assert splitted == expected


def test_hour_to_interval():
    assert make_interval(4, 1, 4, 2) == utils.hour_to_interval(1, 4)
    assert make_interval(7, 23, 1, 0) == utils.hour_to_interval(23, 7)


@pytest.mark.parametrize(
    'date_str, time_zone_str, drop_seconds, expected',
    [
        [
            '2020-11-24T12:16:12',
            'Europe/Moscow',
            True,
            datetime.datetime(
                year=2020,
                month=11,
                day=24,
                hour=12,
                minute=16,
                second=0,
                microsecond=0,
            ),
        ],
        [
            '2020-11-24T12:16:12',
            'Europe/Moscow',
            False,
            datetime.datetime(
                year=2020,
                month=11,
                day=24,
                hour=12,
                minute=16,
                second=12,
                microsecond=0,
            ),
        ],
    ],
)
def test_make_localized_date(date_str, time_zone_str, drop_seconds, expected):
    time_zone = pytz.timezone('Europe/Moscow')
    expected = time_zone.localize(expected)
    result = utils.make_localized_date(
        date_str, time_zone, drop_seconds=drop_seconds,
    )
    assert result == expected


def test_smooth_polygon():
    poly = shapely_geo.Polygon([(0, 0), (3, 3), (4, 2), (5, 3), (12, 0)])

    smoothed = utils.smooth_polygons({'pol1': poly}, 4)
    assert smoothed == {
        'pol1': shapely_geo.Polygon(
            [[0.0, 0.0], [3.0, 3.0], [5.0, 3.0], [12.0, 0.0], [0.0, 0.0]],
        ),
    }
    smoothed = utils.smooth_polygons({'pol1': poly}, 3)
    assert smoothed == {
        'pol1': shapely_geo.Polygon(
            [[0.0, 0.0], [5.0, 3.0], [12.0, 0.0], [0.0, 0.0]],
        ),
    }
    neighbour = shapely_geo.Polygon(
        [[3.5, 2.7], [3.5, 3.5], [4.5, 3.5], [4.5, 2.7], [3.5, 2.7]],
    )
    smoothed = utils.smooth_polygons({'pol1': poly, 'pol2': neighbour}, 4)
    assert smoothed == {
        'pol1': shapely_geo.Polygon(
            [[0.0, 0.0], [4.0, 2.0], [5.0, 3.0], [12.0, 0.0], [0.0, 0.0]],
        ),
        'pol2': neighbour,
    }


def test_split_interval_daily(load_json):
    samples = load_json('split_intervals_data.json')
    for sample in samples:
        split_intervals = utils.split_interval_daily(
            make_interval(*sample['interval']),
        )
        expected = [
            make_interval(*interval) for interval in sample['splitted']
        ]
        assert split_intervals == expected


def test_multiday_interval():
    assert not utils.is_multiday_interval(
        (
            datetime.datetime(1900, 1, 3, 0, 0),
            datetime.datetime(1900, 1, 4, 0, 0),
        ),
    )
    assert not utils.is_multiday_interval(
        (
            datetime.datetime(1900, 1, 3, 2, 0),
            datetime.datetime(1900, 1, 3, 9, 0),
        ),
    )
    assert not utils.is_multiday_interval(
        (
            datetime.datetime(1900, 1, 7, 0, 0),
            datetime.datetime(1900, 1, 1, 0, 0),
        ),
    )
    assert not utils.is_multiday_interval(
        (
            datetime.datetime(1900, 1, 7, 0, 0),
            datetime.datetime(1900, 1, 1, 0, 0),
        ),
    )
    assert utils.is_multiday_interval(
        (
            datetime.datetime(1900, 1, 7, 0, 0),
            datetime.datetime(1900, 1, 1, 2, 0),
        ),
    )
    assert utils.is_multiday_interval(
        (
            datetime.datetime(1900, 1, 7, 0, 0),
            datetime.datetime(1900, 1, 7, 0, 0),
        ),
    )
    assert utils.is_multiday_interval(
        (
            datetime.datetime(1900, 1, 1, 1, 0),
            datetime.datetime(1900, 1, 1, 1, 0),
        ),
    )


@pytest.mark.parametrize(
    'dtime, delta, expected',
    [
        [
            datetime.datetime(year=1900, month=1, day=1, hour=0, minute=10),
            -30,
            datetime.datetime(year=1900, month=1, day=7, hour=23, minute=40),
        ],
        [
            datetime.datetime(year=1900, month=1, day=7, hour=23, minute=50),
            30,
            datetime.datetime(year=1900, month=1, day=1, hour=0, minute=20),
        ],
    ],
)
def test_shift_interval(dtime, delta, expected):
    result = exp_utils.shift_datetime(dtime, delta)
    assert expected == result


def test_smooth_polygon_with_allowed():
    pol = shapely_geo.Polygon(
        [(0, 0), (0, 3), (4, 3), (4, 1), (3, 1), (3, 0), (0, 0)],
    )
    smoothed = utils.smooth_polygons(
        {'pol1': pol}, max_edges_cnt=5, allowed_geo=pol,
    )
    smoothed_coords = {
        name: utils.get_coords(pol) for name, pol in smoothed.items()
    }
    assert smoothed_coords == {
        'pol1': [
            [
                [0.0, 0.0],
                [0.0, 3.0],
                [4.0, 3.0],
                [3.0, 1.0],
                [3.0, 0.0],
                [0.0, 0.0],
            ],
        ],
    }
