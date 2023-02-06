import pytest


@pytest.mark.parametrize(
    'intervals, begin, coef, expected',
    [
        ([], 100, 1, []),
        ([{'begin': 0, 'price': 2}], 30, 2, [{'begin': 30, 'price': 4}]),
        ([{'begin': 40, 'price': 1.5}], 30, 2, [{'begin': 30, 'price': 3}]),
        (
            [{'begin': 0, 'price': 1.5, 'e': 25}, {'begin': 25, 'price': 1.5}],
            30,
            1,
            [{'begin': 30, 'price': 1.5}],
        ),
        (
            [{'begin': 0, 'price': 2, 'e': 35}, {'begin': 35, 'price': 2}],
            30,
            2,
            [{'begin': 30, 'price': 4, 'e': 35}, {'begin': 35, 'price': 4}],
        ),
        (
            [{'begin': 35, 'price': 2, 'e': 40}, {'begin': 40, 'price': 2}],
            35,
            2,
            [{'begin': 35, 'price': 4, 'e': 40}, {'begin': 40, 'price': 4}],
        ),
    ],
)
def test_compute_requirement_intervals(intervals, begin, coef, expected):
    from taxi_tariffs.api.common import requirement_manager as rm

    res = rm._compute_requirement_intervals(  # pylint: disable=W0212
        intervals, begin, coef,
    )
    assert res == expected


@pytest.mark.parametrize(
    [
        'time_begin',
        'distance_begin',
        'multiplier',
        'tpi',
        'dpi',
        'expected_tpi',
        'expected_dpi',
    ],
    [
        (
            30,
            None,
            1,
            [{'begin': 0, 'price': 2}],
            [{'begin': 0, 'price': 2}],
            [{'begin': 30, 'price': 2}],
            [{'begin': 0, 'price': 2}],
        ),
        (
            None,
            30,
            1,
            [{'begin': 0, 'price': 2}],
            [{'begin': 0, 'price': 2}],
            [{'begin': 0, 'price': 2}],
            [{'begin': 30, 'price': 2}],
        ),
        (
            0,
            0,
            2,
            [{'begin': 10, 'price': 2}],
            [{'begin': 20, 'price': 2}],
            [{'begin': 0, 'price': 4}],
            [{'begin': 0, 'price': 4}],
        ),
        (
            0,
            0,
            None,  # multipliers are not set (use 1.0)
            [{'begin': 10, 'price': 2}],
            [{'begin': 20, 'price': 2}],
            [{'begin': 0, 'price': 2}],
            [{'begin': 0, 'price': 2}],
        ),
        (
            None,
            None,
            1,
            [{'begin': 10, 'price': 2}],
            [{'begin': 20, 'price': 2}],
            [{'begin': 10, 'price': 2}],
            [{'begin': 20, 'price': 2}],
        ),
    ],
)
def test_prepare_requirement(
        time_begin,
        distance_begin,
        multiplier,
        tpi,
        dpi,
        expected_tpi,
        expected_dpi,
):
    from taxi_tariffs.api.common import requirement_manager as rm

    zone_name = 'moscow'
    source_special_taximeters = [
        {
            'zone_name': zone_name,
            'price': {
                'time_price_intervals': tpi,
                'distance_price_intervals': dpi,
            },
        },
    ]
    requirement_price = {
        'included_time': time_begin,
        'time_multiplier': multiplier,
        'included_distance': distance_begin,
        'distance_multiplier': multiplier,
    }

    results = rm.requirement_special_taximeters(
        source_special_taximeters, requirement_price,
    )
    assert len(results) == 1
    result = results[0]
    assert result['zone_name'] == zone_name
    assert result['price']['time_price_intervals'] == expected_tpi
    assert result['price']['distance_price_intervals'] == expected_dpi
