# -*- coding: utf-8 -*-

import pytest

from taxi.core import async
from taxi.internal import dbh
from taxi.internal import requirement_manager


@pytest.mark.parametrize('req_name,req_type', [
    ('nosmoking', requirement_manager.REQUIREMENT_TYPE_BOOL),
    ('coupon', requirement_manager.REQUIREMENT_TYPE_SPECIAL),
    ('artificial', None)
])
@pytest.inline_callbacks
def test_get_all_requirements(req_name, req_type):
    all_reqs = dict(
        (req['name'], req)
        for req in (yield requirement_manager.get_all_requirements())
    )
    if req_type is not None:
        assert req_name in all_reqs
        assert all_reqs[req_name]['type'] == req_type


@pytest.inline_callbacks
def test_get_all_requirements_position_and_id():
    all_reqs = yield requirement_manager.get_all_requirements()

    assert all_reqs[0]['name'] == 'yellowcarnumber'

    for req in all_reqs:
        assert 'position' not in req
        assert '_id' not in req


@pytest.mark.parametrize('intervals,begin,coef,expected', [
    (
        [],
        100,
        1,
        []
    ),
    (
        [{'begin': 0, 'price': 2}],
        30,
        2,
        [{'begin': 30, 'price': 4}],
    ),
    (
        [{'begin': 40, 'price': 1.5}],
        30,
        2,
        [{'begin': 30, 'price': 3}],
    ),
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
    )
])
@pytest.mark.asyncenv('blocking')
def test_compute_requirement_intervals(intervals, begin, coef, expected):
    res = requirement_manager._compute_requirement_intervals(
        intervals, begin, coef
    )
    assert res == expected


@pytest.mark.parametrize(
    'time_begin,distance_begin,multiplier,tpi,dpi,expected_tpi,expected_dpi',
    [
        (
            30, None, 1,
            [{'begin': 0, 'price': 2}], [{'begin': 0, 'price': 2}],
            [{'begin': 30, 'price': 2}], [{'begin': 0, 'price': 2}]
        ),
        (
            None, 30, 1,
            [{'begin': 0, 'price': 2}], [{'begin': 0, 'price': 2}],
            [{'begin': 0, 'price': 2}], [{'begin': 30, 'price': 2}]
        ),
        (
            0, 0, 2,
            [{'begin': 10, 'price': 2}], [{'begin': 20, 'price': 2}],
            [{'begin': 0, 'price': 4}], [{'begin': 0, 'price': 4}]
        ),
        (
            0, 0, None,  # multipliers are not set (use 1.0)
            [{'begin': 10, 'price': 2}], [{'begin': 20, 'price': 2}],
            [{'begin': 0, 'price': 2}], [{'begin': 0, 'price': 2}]
        ),
        (
            {}, {}, 1,  # dbh
            [{'begin': 10, 'price': 2}], [{'begin': 20, 'price': 2}],
            [{'begin': 10, 'price': 2}], [{'begin': 20, 'price': 2}]
        ),
        (
            None, None, 1,
            [{'begin': 10, 'price': 2}], [{'begin': 20, 'price': 2}],
            [{'begin': 10, 'price': 2}], [{'begin': 20, 'price': 2}]
        )
    ]
)
@pytest.mark.asyncenv('blocking')
def test_prepare_requirement(
        time_begin, distance_begin, multiplier, tpi, dpi, expected_tpi, expected_dpi
):
    zone_name = 'moscow'
    category = {
        'special_taximeters': [
            {
                'zone_name': zone_name,
                'price': {
                    'time_price_intervals': tpi,
                    'distance_price_intervals': dpi
                }
            }
        ]
    }
    requirement = {
        'type': 'type',
        'price': {
            'included_time': time_begin,
            'time_multiplier': multiplier,
            'included_distance': distance_begin,
            'distance_multiplier': multiplier
        }
    }

    requirement_manager.prepare_requirement(category, requirement)
    assert len(requirement['price']['special_taximeters']) == 1
    special_taximeters = requirement['price']['special_taximeters'][0]
    assert special_taximeters['zone_name'] == zone_name
    assert special_taximeters['price']['time_price_intervals'] == expected_tpi
    assert special_taximeters['price']['distance_price_intervals'] == expected_dpi
    assert dbh.tariffs.SpecialTaximeter.obj.zone_name.key == 'z'


@pytest.mark.filldb(_fill=False)
@pytest.mark.parametrize('requirements,client_requirements,expected', [
    (
            [
                {
                    'name': 'childchair_moscow',
                    'select': {
                        'options': [],
                    },
                    'type': u'select'
                },
                {
                    'name': 'animaltransport',
                    'type': 'boolean',
                }
            ],
            {'childchair_moscow': 7, 'animaltransport': True},
            ['animaltransport', 'childchair_moscow'],
    ),
    (
            [
                {
                    'name': 'childchair_moscow',
                    'select': {
                        'options': [
                            {'name': 'booster', 'value': 7}
                        ],
                    },
                    'type': u'select'
                },
                {
                    'name': 'animaltransport',
                    'type': 'boolean',
                }
            ],
            {'childchair_moscow': 7, 'animaltransport': True},
            ['animaltransport', 'childchair_moscow'],
    ),
    (
            [
                {
                    'name': 'childchair_moscow',
                    'select': {
                        'options': [
                            {
                                'name': 'booster',
                                'value': 7,
                                'independent_tariffication': True
                            }
                        ],
                    },
                    'type': u'select'
                },
                {
                    'name': 'animaltransport',
                    'type': 'boolean',
                }
            ],
            {'childchair_moscow': 7, 'animaltransport': True},
            ['animaltransport', 'childchair_moscow.booster'],
    ),
    (
            [
                {
                    'name': 'childchair_moscow',
                    'select': {
                        'options': [
                            {
                                'name': 'seat',
                                'value': 3,
                            },
                            {
                                'name': 'booster',
                                'value': 7,
                                'independent_tariffication': True
                            }
                        ],
                    },
                    'type': u'select'
                },
                {
                    'name': 'animaltransport',
                    'type': 'boolean',
                }
            ],
            {'childchair_moscow': [3, 7, 3, 7, 7], 'animaltransport': True},
            ['animaltransport',
             'childchair_moscow',
             'childchair_moscow',
             'childchair_moscow.booster',
             'childchair_moscow.booster',
             'childchair_moscow.booster',
             ],
    ),
])
@pytest.inline_callbacks
def test_get_requirements_identifiers(requirements, client_requirements,
                                      expected, patch):
    @patch('taxi.internal.requirement_manager.get_all_requirements')
    @async.inline_callbacks
    def _get_all_requirements():
        yield
        async.return_value(requirements)

    got = yield requirement_manager.get_identifiers(client_requirements)
    assert sorted(got) == sorted(expected)
