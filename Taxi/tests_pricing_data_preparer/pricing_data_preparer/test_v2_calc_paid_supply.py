# pylint: disable=redefined-outer-name, import-only-modules, too-many-lines
# flake8: noqa F401
import decimal
import pytest
import copy
from math import ceil
from .plugins import utils_request
from .plugins import utils_response
from .plugins.mock_decoupling import decoupling
from .plugins.mock_decoupling import mock_decoupling_corp_tariffs
from .round_values import round_values


def _reset_calc_paid_supply_link(response):
    for category in response['categories'].values():
        if 'links' in category and 'calc_paid_supply' in category['links']:
            category['links']['calc_paid_supply'] = '__default__'
    return response


async def test_v2_calc_paid_supply_no_categories(taxi_pricing_data_preparer):
    response = await taxi_pricing_data_preparer.post(
        'v2/calc_paid_supply',
        json={
            'point': [37.683, 55.774],
            'zone': 'moscow',
            'categories': {},
            'modifications_scope': 'taxi',
        },
    )
    assert response.status_code == 200
    assert response.json() == {'categories': {}}


@pytest.mark.pgsql(
    'pricing_data_preparer', files=['rules.sql', 'workabilities.sql'],
)
@pytest.mark.parametrize(
    'point_a, driver_route_info, cfg_paid_supply_free_route, zone,'
    'expected_paid_supply_price, expected_final_ps_driver_price, expected_final_ps_user_price, '
    'expected_final_ps_strikeout_user_price,log',
    [
        (
            [37.683, 55.774],  # moscow
            {'distance': 5000.0, 'time': 1000.0},
            {'DISTANCE': 15000.0, 'TIME': 1200.0},
            'moscow',
            0.0,
            1060.0,
            730.0,
            830.0,
            {
                'econom': {
                    'fixed': True,
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 830.0,
                        'strikeout': 830.0,
                        'base_price': {
                            'boarding': 70.0,
                            'distance': 300.0,
                            'time': 400.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                    'driver': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 1060.0,
                        'base_price': {
                            'boarding': 100.0,
                            'distance': 400.0,
                            'time': 500.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                },
            },
        ),
        (
            [37.683, 55.774],  # moscow
            {'distance': 5000.0, 'time': 1000.0},
            {'DISTANCE': 15000.0, 'TIME': 1200.0},
            'moscow1',
            50.0,
            1060.0 + 50.0,
            730.0 + 25.0,
            830.0 + 25.0,
            {
                'econom': {
                    'fixed': True,
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 830.0,
                        'strikeout': 830.0,
                        'base_price': {
                            'boarding': 70.0,
                            'distance': 300.0,
                            'time': 400.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                    'driver': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 1060.0,
                        'base_price': {
                            'boarding': 100.0,
                            'distance': 400.0,
                            'time': 500.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                },
            },
        ),
        (
            [37.683, 55.774],  # moscow
            {'distance': 5000.0, 'time': 1000.0},
            {'DISTANCE': 0.0, 'TIME': 0.0},
            'moscow',
            200.0,  # 10 * (5000 - 0) / 1000 + 9 * (1000 - 0) / 60
            1060.0 + 200.0,
            730.0 + 100.0,
            830.0 + 100.0,
            {
                'econom': {
                    'fixed': True,
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 830.0,
                        'strikeout': 830.0,
                        'base_price': {
                            'boarding': 70.0,
                            'distance': 300.0,
                            'time': 400.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                    'driver': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 1060.0,
                        'base_price': {
                            'boarding': 100.0,
                            'distance': 400.0,
                            'time': 500.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                },
            },
        ),
        (
            [37.683, 55.774],  # moscow
            {'distance': 40000.0, 'time': 10000.0},
            {'DISTANCE': 15000.0, 'TIME': 1200.0},
            'moscow',
            1570.0,  # 10 * (40000 - 15000) / 1000 + 9 * (10000 - 1200) / 60
            1060.0 + 1570.0,
            730.0 + 785.0,
            830.0 + 785.0,
            {
                'econom': {
                    'fixed': True,
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 830.0,
                        'strikeout': 830.0,
                        'base_price': {
                            'boarding': 70.0,
                            'distance': 300.0,
                            'time': 400.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                    'driver': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 1060.0,
                        'base_price': {
                            'boarding': 100.0,
                            'distance': 400.0,
                            'time': 500.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                },
            },
        ),
        (
            [38.143369, 55.566771],  # suburb of moscow_activation
            {'distance': 40000.0, 'time': 10000.0},
            {'DISTANCE': 15000.0, 'TIME': 1000.0},
            'moscow',
            1495.0,
            # 19 * (20 - 3) + 12 * ((40000 - 15000) / 1000 - (20 - 3)) +
            # 9 * (18 - 5) + 7 * ((10000 - 1000) / 60 - (18 - 5))
            1060.0 + 1495.0,
            ceil(730.0 + 747.5),
            ceil(830.0 + 747.5),
            {
                'econom': {
                    'fixed': True,
                    'decoupling': False,
                    'success': False,
                    'user': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 830.0,
                        'strikeout': 830.0,
                        'base_price': {
                            'boarding': 70.0,
                            'distance': 300.0,
                            'time': 400.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                    'driver': {
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'price': 1060.0,
                        'base_price': {
                            'boarding': 100.0,
                            'distance': 400.0,
                            'time': 500.0,
                        },
                        'trip_details': {'distance': 100500.0, 'time': 307.0},
                    },
                },
            },
        ),
    ],
)
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.experiments3(filename='exp3_config_paid_supply_min_price.json')
async def test_v2_calc_paid_supply_calculation(
        taxi_pricing_data_preparer,
        taxi_config,
        point_a,
        driver_route_info,
        cfg_paid_supply_free_route,
        zone,
        expected_paid_supply_price,
        expected_final_ps_driver_price,
        expected_final_ps_user_price,
        expected_final_ps_strikeout_user_price,
        testpoint,
        log,
):
    taxi_config.set(
        PAID_SUPPLY_FREE_DISTANCE_TIME={
            '__default__': {'__default__': cfg_paid_supply_free_route},
        },
    )

    @testpoint('v2_calc_paid_supply_response_log')
    def v2_calc_paid_supply_resp_log(data):
        assert data == log

    response = await taxi_pricing_data_preparer.post(
        'v2/calc_paid_supply',
        json={
            'modifications_scope': 'taxi',
            'point': point_a,
            'zone': zone,
            'categories': {
                'econom': {
                    'driver_route_info': driver_route_info,
                    'prepared': {
                        'tariff_info': {
                            'time': {
                                'included_minutes': 1,
                                'price_per_minute': 2,
                            },
                            'distance': {
                                'included_kilometers': 3,
                                'price_per_kilometer': 4,
                            },
                            'point_a_free_waiting_time': 5,
                            'max_free_waiting_time': 6,
                        },
                        'corp_decoupling': False,
                        'fixed_price': True,
                        'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
                        'currency': {
                            'fraction_digits': 0,
                            'name': 'RUB',
                            'symbol': '₽',
                        },
                        'links': {'prepare': '__prepare_link__'},
                        'driver': {
                            'modifications': {
                                'for_fixed': [77, 88, 99],
                                'for_taximeter': [77, 88],
                            },
                            'price': {'total': 1060.0},
                            'meta': {},
                            'trip_information': {
                                'distance': 100500,
                                'has_toll_roads': False,
                                'jams': True,
                                'time': 307.0,
                            },
                            'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                            'category_id': '00000000000000000000000000000001',
                            'base_price': {
                                'boarding': 100.0,
                                'distance': 400.0,
                                'time': 500.0,
                                'waiting': 10.0,
                                'requirements': 0.0,
                                'transit_waiting': 50.0,
                                'destination_waiting': 0.0,
                            },
                            'category_prices_id': (
                                'c/00000000000000000000000000000001'
                            ),
                            'additional_prices': {},
                        },
                        'user': {
                            'modifications': {
                                'for_fixed': [55, 44, 33],
                                'for_taximeter': [55, 33],
                            },
                            'price': {'total': 830.0, 'strikeout': 830.0},
                            'meta': {},
                            'trip_information': {
                                'distance': 100500,
                                'has_toll_roads': False,
                                'jams': True,
                                'time': 307.0,
                            },
                            'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                            'category_id': '00000000000000000000000000000001',
                            'base_price': {
                                'boarding': 70.0,
                                'distance': 300.0,
                                'time': 400.0,
                                'waiting': 10.0,
                                'requirements': 0.0,
                                'transit_waiting': 50.0,
                                'destination_waiting': 0.0,
                            },
                            'category_prices_id': (
                                'c/00000000000000000000000000000001'
                            ),
                            'additional_prices': {},
                            'data': {
                                'waypoints_count': 2,
                                'country_code2': 'RU',
                                'zone': 'moscow',
                                'category': 'econom',
                                'rounding_factor': 1.0,
                                'user_tags': [],
                                'surge_params': {
                                    'value': 1.0,
                                    'value_smooth': 1.0,
                                    'value_raw': 1.0,
                                },
                                'requirements': {'simple': [], 'select': {}},
                                'tariff': {
                                    'boarding_price': 0.0,
                                    'minimum_price': 0.0,
                                    'waiting_price': {
                                        'free_waiting_time': 0,
                                        'price_per_minute': 0.0,
                                    },
                                    'requirement_prices': {},
                                },
                                'user_data': {
                                    'has_yaplus': False,
                                    'has_cashback_plus': False,
                                },
                                'category_data': {
                                    'fixed_price': False,
                                    'decoupling': False,
                                    'paid_cancel_waiting_time_limit': 600.0,
                                    'min_paid_supply_price_for_paid_cancel': (
                                        0.0
                                    ),
                                },
                                'exps': {},
                            },
                        },
                    },
                },
            },
        },
    )
    assert response.status_code == 200
    data = _reset_calc_paid_supply_link(response.json())
    assert round_values(data) == round_values(
        {
            'categories': {
                'econom': {
                    'corp_decoupling': False,
                    'fixed_price': True,
                    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
                    'tariff_info': {
                        'time': {'included_minutes': 1, 'price_per_minute': 2},
                        'distance': {
                            'included_kilometers': 3,
                            'price_per_kilometer': 4,
                        },
                        'point_a_free_waiting_time': 5,
                        'max_free_waiting_time': 6,
                    },
                    'currency': {
                        'fraction_digits': 0,
                        'name': 'RUB',
                        'symbol': '₽',
                    },
                    'links': {
                        'prepare': '__prepare_link__',
                        'calc_paid_supply': '__default__',
                    },
                    'driver': {
                        'modifications': {
                            'for_fixed': [77, 88, 99],
                            'for_taximeter': [77, 88],
                        },
                        'price': {'total': 1060.0},
                        'meta': {},
                        'trip_information': {
                            'distance': 100500,
                            'has_toll_roads': False,
                            'jams': True,
                            'time': 307.0,
                        },
                        'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                        'category_id': '00000000000000000000000000000001',
                        'base_price': {
                            'boarding': 100.0,
                            'distance': 400.0,
                            'time': 500.0,
                            'waiting': 10.0,
                            'requirements': 0.0,
                            'transit_waiting': 50.0,
                            'destination_waiting': 0.0,
                        },
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'additional_prices': {
                            'paid_supply': {
                                'modifications': {
                                    'for_fixed': [2],
                                    'for_taximeter': [2],
                                },
                                'price': {
                                    'total': expected_final_ps_driver_price,
                                },
                                'meta': {},
                            },
                        },
                    },
                    'user': {
                        'modifications': {
                            'for_fixed': [55, 44, 33],
                            'for_taximeter': [55, 33],
                        },
                        'price': {'total': 830.0, 'strikeout': 830.0},
                        'meta': {},
                        'trip_information': {
                            'distance': 100500,
                            'has_toll_roads': False,
                            'jams': True,
                            'time': 307.0,
                        },
                        'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                        'category_id': '00000000000000000000000000000001',
                        'base_price': {
                            'boarding': 70.0,
                            'distance': 300.0,
                            'time': 400.0,
                            'waiting': 10.0,
                            'requirements': 0.0,
                            'transit_waiting': 50.0,
                            'destination_waiting': 0.0,
                        },
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'additional_prices': {
                            'paid_supply': {
                                'modifications': {
                                    'for_fixed': [1, 3],
                                    'for_taximeter': [1, 3],
                                },
                                'price': {
                                    'total': expected_final_ps_user_price,
                                    'strikeout': (
                                        expected_final_ps_strikeout_user_price
                                    ),
                                },
                                'meta': {},
                            },
                        },
                        'data': {
                            'waypoints_count': 2,
                            'country_code2': 'RU',
                            'zone': 'moscow',
                            'category': 'econom',
                            'rounding_factor': 1.0,
                            'paid_supply_price': expected_paid_supply_price,
                            'user_tags': [],
                            'surge_params': {
                                'value': 1.0,
                                'value_smooth': 1.0,
                                'value_raw': 1.0,
                            },
                            'requirements': {'simple': [], 'select': {}},
                            'tariff': {
                                'boarding_price': 0.0,
                                'minimum_price': 0.0,
                                'waiting_price': {
                                    'free_waiting_time': 0,
                                    'price_per_minute': 0.0,
                                },
                                'requirement_prices': {},
                            },
                            'user_data': {
                                'has_yaplus': False,
                                'has_cashback_plus': False,
                            },
                            'category_data': {
                                'fixed_price': False,
                                'decoupling': False,
                                'paid_cancel_waiting_time_limit': 600.0,
                                'min_paid_supply_price_for_paid_cancel': 0.0,
                            },
                            'exps': {},
                        },
                    },
                },
            },
        },
    )
    assert v2_calc_paid_supply_resp_log.times_called == 1


REQUEST = {
    'modifications_scope': 'taxi',
    'point': [37.683, 55.774],
    'zone': 'moscow',
    'categories': {
        'econom': {
            'driver_route_info': {'distance': 5000.0, 'time': 1000.0},
            'prepared': {
                'corp_decoupling': False,
                'fixed_price': True,
                'tariff_info': {
                    'time': {'included_minutes': 1, 'price_per_minute': 2},
                    'distance': {
                        'included_kilometers': 3,
                        'price_per_kilometer': 4,
                    },
                    'point_a_free_waiting_time': 5,
                    'max_free_waiting_time': 6,
                },
                'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
                'currency': {
                    'fraction_digits': 0,
                    'name': 'RUB',
                    'symbol': '₽',
                },
                'links': {'prepare': '__prepare_link__'},
                'driver': {
                    'modifications': {
                        'for_fixed': [77, 88, 99],
                        'for_taximeter': [77, 88],
                    },
                    'price': {'total': 1060.0},
                    'meta': {},
                    'trip_information': {
                        'distance': 100500,
                        'has_toll_roads': False,
                        'jams': True,
                        'time': 307.0,
                    },
                    'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                    'category_id': '00000000000000000000000000000001',
                    'base_price': {
                        'boarding': 100.0,
                        'distance': 400.0,
                        'time': 500.0,
                        'waiting': 10.0,
                        'requirements': 0.0,
                        'transit_waiting': 50.0,
                        'destination_waiting': 0.0,
                    },
                    'category_prices_id': 'c/00000000000000000000000000000001',
                    'additional_prices': {},
                    'data': {
                        'waypoints_count': 2,
                        'country_code2': 'RU',
                        'zone': 'moscow',
                        'category': 'econom',
                        'rounding_factor': 1.0,
                        'user_tags': [],
                        'surge_params': {
                            'value': 1.0,
                            'value_smooth': 1.0,
                            'value_raw': 1.0,
                        },
                        'requirements': {'simple': [], 'select': {}},
                        'tariff': {
                            'boarding_price': 0.0,
                            'minimum_price': 0.0,
                            'waiting_price': {
                                'free_waiting_time': 0,
                                'price_per_minute': 0.0,
                            },
                            'requirement_prices': {},
                        },
                        'user_data': {
                            'has_yaplus': False,
                            'has_cashback_plus': False,
                        },
                        'category_data': {
                            'fixed_price': False,
                            'decoupling': False,
                            'paid_cancel_waiting_time_limit': 600.0,
                            'min_paid_supply_price_for_paid_cancel': 0.0,
                        },
                        'exps': {},
                    },
                },
                'user': {
                    'modifications': {
                        'for_fixed': [55, 44, 33],
                        'for_taximeter': [55, 33],
                    },
                    'price': {'total': 830.0, 'strikeout': 830.0},
                    'meta': {},
                    'trip_information': {
                        'distance': 100500,
                        'has_toll_roads': False,
                        'jams': True,
                        'time': 307.0,
                    },
                    'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                    'category_id': '00000000000000000000000000000001',
                    'base_price': {
                        'boarding': 70.0,
                        'distance': 300.0,
                        'time': 400.0,
                        'waiting': 10.0,
                        'requirements': 0.0,
                        'transit_waiting': 50.0,
                        'destination_waiting': 0.0,
                    },
                    'category_prices_id': (
                        'd/corp_tariff_id/decoupling_category_id'
                    ),
                    'additional_prices': {},
                    'data': {
                        'waypoints_count': 2,
                        'country_code2': 'RU',
                        'zone': 'moscow',
                        'category': 'econom',
                        'rounding_factor': 1.0,
                        'user_tags': [],
                        'surge_params': {
                            'value': 1.0,
                            'value_smooth': 1.0,
                            'value_raw': 1.0,
                        },
                        'requirements': {'simple': [], 'select': {}},
                        'tariff': {
                            'boarding_price': 0.0,
                            'minimum_price': 0.0,
                            'waiting_price': {
                                'free_waiting_time': 0,
                                'price_per_minute': 0.0,
                            },
                            'requirement_prices': {},
                        },
                        'user_data': {
                            'has_yaplus': False,
                            'has_cashback_plus': False,
                        },
                        'category_data': {
                            'fixed_price': False,
                            'decoupling': False,
                            'paid_cancel_waiting_time_limit': 600.0,
                            'min_paid_supply_price_for_paid_cancel': 0.0,
                        },
                        'exps': {},
                    },
                },
            },
        },
    },
}


@pytest.mark.pgsql(
    'pricing_data_preparer',
    files=['rules.sql', 'workabilities_only_paid_supply_addition.sql'],
)
@pytest.mark.config(
    PAID_SUPPLY_FREE_DISTANCE_TIME={
        '__default__': {'__default__': {'DISTANCE': 0.0, 'TIME': 0.0}},
    },
)
@pytest.mark.parametrize(
    'same_paid_supply_price, expected_user_paid_supply_price',
    [
        (True, 200),  # 10 * (5000 - 0) / 1000 + 9 * (1000 - 0) / 60
        (False, 18.333333333),  # 2 * (5000 - 0) / 1000 + 0.5 * (1000 - 0) / 60
    ],
)
@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.experiments3(filename='exp3_config_paid_supply_min_price.json')
async def test_v2_calc_paid_supply_decoupling(
        taxi_pricing_data_preparer,
        taxi_config,
        mock_decoupling_corp_tariffs,
        same_paid_supply_price,
        expected_user_paid_supply_price,
):
    taxi_config.set(
        SAME_BASE_PAID_SUPPLY_PRICE_FOR_DRIVER_AND_USER=same_paid_supply_price,
    )
    response = await taxi_pricing_data_preparer.post(
        'v2/calc_paid_supply', json=REQUEST,
    )
    assert response.status_code == 200
    data = _reset_calc_paid_supply_link(response.json())
    assert round_values(data) == round_values(
        {
            'categories': {
                'econom': {
                    'corp_decoupling': False,
                    'fixed_price': True,
                    'geoarea_ids': ['g/1f121111472a45e9bcbb7c72200c6340'],
                    'tariff_info': {
                        'time': {'included_minutes': 1, 'price_per_minute': 2},
                        'distance': {
                            'included_kilometers': 3,
                            'price_per_kilometer': 4,
                        },
                        'point_a_free_waiting_time': 5,
                        'max_free_waiting_time': 6,
                    },
                    'currency': {
                        'fraction_digits': 0,
                        'name': 'RUB',
                        'symbol': '₽',
                    },
                    'links': {
                        'prepare': '__prepare_link__',
                        'calc_paid_supply': '__default__',
                    },
                    'driver': {
                        'modifications': {
                            'for_fixed': [77, 88, 99],
                            'for_taximeter': [77, 88],
                        },
                        'price': {'total': 1060.0},
                        'meta': {},
                        'trip_information': {
                            'distance': 100500,
                            'has_toll_roads': False,
                            'jams': True,
                            'time': 307.0,
                        },
                        'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                        'category_id': '00000000000000000000000000000001',
                        'base_price': {
                            'boarding': 100.0,
                            'distance': 400.0,
                            'time': 500.0,
                            'waiting': 10.0,
                            'requirements': 0.0,
                            'transit_waiting': 50.0,
                            'destination_waiting': 0.0,
                        },
                        'category_prices_id': (
                            'c/00000000000000000000000000000001'
                        ),
                        'additional_prices': {
                            'paid_supply': {
                                'modifications': {
                                    'for_fixed': [2],
                                    'for_taximeter': [2],
                                },
                                'price': {'total': 1260.0},
                                'meta': {},
                            },
                        },
                        'data': {
                            'waypoints_count': 2,
                            'country_code2': 'RU',
                            'zone': 'moscow',
                            'category': 'econom',
                            'rounding_factor': 1.0,
                            'paid_supply_price': 200.0,
                            'user_tags': [],
                            'surge_params': {
                                'value': 1.0,
                                'value_smooth': 1.0,
                                'value_raw': 1.0,
                            },
                            'requirements': {'simple': [], 'select': {}},
                            'tariff': {
                                'boarding_price': 0.0,
                                'minimum_price': 0.0,
                                'waiting_price': {
                                    'free_waiting_time': 0,
                                    'price_per_minute': 0.0,
                                },
                                'requirement_prices': {},
                            },
                            'user_data': {
                                'has_yaplus': False,
                                'has_cashback_plus': False,
                            },
                            'category_data': {
                                'fixed_price': False,
                                'decoupling': False,
                                'paid_cancel_waiting_time_limit': 600.0,
                                'min_paid_supply_price_for_paid_cancel': 0.0,
                            },
                            'exps': {},
                        },
                    },
                    'user': {
                        'modifications': {
                            'for_fixed': [55, 44, 33],
                            'for_taximeter': [55, 33],
                        },
                        'price': {'total': 830.0, 'strikeout': 830.0},
                        'meta': {},
                        'trip_information': {
                            'distance': 100500,
                            'has_toll_roads': False,
                            'jams': True,
                            'time': 307.0,
                        },
                        'tariff_id': 'aaaaaaaaaaaaaaaaaaaaaaaa',
                        'category_id': '00000000000000000000000000000001',
                        'base_price': {
                            'boarding': 70.0,
                            'distance': 300.0,
                            'time': 400.0,
                            'waiting': 10.0,
                            'requirements': 0.0,
                            'transit_waiting': 50.0,
                            'destination_waiting': 0.0,
                        },
                        'category_prices_id': (
                            'd/corp_tariff_id/decoupling_category_id'
                        ),
                        'additional_prices': {
                            'paid_supply': {
                                'modifications': {
                                    'for_fixed': [2],
                                    'for_taximeter': [2],
                                },
                                'price': {
                                    'total': ceil(
                                        830 + expected_user_paid_supply_price,
                                    ),
                                    'strikeout': ceil(
                                        830.0
                                        + expected_user_paid_supply_price,
                                    ),
                                },
                                'meta': {},
                            },
                        },
                        'data': {
                            'waypoints_count': 2,
                            'country_code2': 'RU',
                            'zone': 'moscow',
                            'category': 'econom',
                            'rounding_factor': 1.0,
                            'paid_supply_price': (
                                expected_user_paid_supply_price
                            ),
                            'user_tags': [],
                            'surge_params': {
                                'value': 1.0,
                                'value_smooth': 1.0,
                                'value_raw': 1.0,
                            },
                            'requirements': {'simple': [], 'select': {}},
                            'tariff': {
                                'boarding_price': 0.0,
                                'minimum_price': 0.0,
                                'waiting_price': {
                                    'free_waiting_time': 0,
                                    'price_per_minute': 0.0,
                                },
                                'requirement_prices': {},
                            },
                            'user_data': {
                                'has_yaplus': False,
                                'has_cashback_plus': False,
                            },
                            'category_data': {
                                'fixed_price': False,
                                'decoupling': False,
                                'paid_cancel_waiting_time_limit': 600.0,
                                'min_paid_supply_price_for_paid_cancel': 0.0,
                            },
                            'exps': {},
                        },
                    },
                },
            },
        },
    )


@pytest.mark.now('2021-09-12T19:00:00Z')
@pytest.mark.pgsql(
    'pricing_data_preparer',
    files=[
        'rules_for_strikeout_test.sql',
        'workabilities_for_strikeout_test.sql',
    ],
)
@pytest.mark.experiments3(filename='exp3_config_paid_supply_min_price.json')
async def test_v2_calc_pair_supply_strikeout_price_modifications_test(
        taxi_pricing_data_preparer, taxi_config, mock_decoupling_corp_tariffs,
):
    request = copy.deepcopy(REQUEST)
    request['additional_payloads'] = {
        'need_strikeout_price_modifications': True,
    }
    response = await taxi_pricing_data_preparer.post(
        'v2/calc_paid_supply', json=request,
    )
    assert response.status_code == 200
    data = response.json()

    def _get_strikeout_modifications_list(_for):
        user = data['categories']['econom']['user']
        assert 'additional_prices' in user
        assert 'paid_supply' in user['additional_prices']
        assert (
            'additional_payloads' in user['additional_prices']['paid_supply']
        )
        assert (
            'modifications_for_strikeout_price'
            in user['additional_prices']['paid_supply']['additional_payloads']
        )
        return user['additional_prices']['paid_supply']['additional_payloads'][
            'modifications_for_strikeout_price'
        ][_for]

    _expected_modifications_for_fixed = [3, 4, 5]
    _expected_modifications_for_taximeter = [3, 4, 5, 7]
    modifications_for_fixed = _get_strikeout_modifications_list('for_fixed')
    assert modifications_for_fixed == _expected_modifications_for_fixed
    modifications_for_taximeter = _get_strikeout_modifications_list(
        'for_taximeter',
    )
    assert modifications_for_taximeter == _expected_modifications_for_taximeter
