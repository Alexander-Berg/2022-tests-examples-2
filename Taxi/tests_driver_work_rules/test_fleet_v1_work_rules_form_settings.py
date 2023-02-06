import typing

import pytest

from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils

ENDPOINT = 'fleet/driver-work-rules/v1/work-rules/form-settings'

ORDER_TYPES_EMPTY: typing.Dict = {'order_types': []}

ORDER_TYPES_3: typing.Dict = {
    'order_types': [
        {'id': 'order_type1', 'name': 'OrderType1'},
        {'id': 'order_type2', 'name': 'OrderType2'},
        {'id': 'order_type3', 'name': 'OrderType3'},
    ],
}

CALC_ENTRY_RANGE_CONFIG_DEFAULT: typing.Dict = {
    'commission_percent_range': {'min': '0.5', 'max': '1.2'},
}

WORKSHIFT_RANGE_CONFIG_DEFAULT: typing.Dict = {
    'workshift_commission_percent_range': {'min': '14.5', 'max': '44.4'},
}

DRIVER_FIX_RANGE: typing.Dict = {
    'driver_fix_commission_percent_range': {'min': '0', 'max': '100'},
}

SUBVENTION_RANGE = {
    'subvention_commission_percent_range': {'min': '0', 'max': '5'},
}

BASE_PARK = {
    'id': 'park_id1',
    'city_id': 'Moscow',
    'country_id': 'Ita',
    'demo_mode': False,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
    'is_active': True,
    'is_billing_enabled': True,
    'is_franchising_enabled': False,
    'locale': 'ru',
    'login': 'Al',
    'name': 'Pacino',
}


TEST_OK_PARAMS = [
    # test ok
    (
        'park_id1',
        {'compatible_rule_id': 'work_rule_id_type_park'},
        {'is_workshift_enabled': True, 'country_id': 'rus'},
        {},
        200,
        {
            'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT},
            **WORKSHIFT_RANGE_CONFIG_DEFAULT,
            **SUBVENTION_RANGE,
        },
    ),
    # park not found
    (
        'not_existing_park_id',
        {},
        {},
        {},
        404,
        {
            'code': 'not_found',
            'message': 'Park with id `not_existing_park_id` not found',
        },
    ),
    # country not found
    (
        'park_id1',
        {},
        {'country_id': 'not_existing_country'},
        {},
        404,
        {
            'code': 'not_found',
            'message': 'Country with id `not_existing_country` not found',
        },
    ),
    # rule not found
    (
        'park_id1',
        {'compatible_rule_id': 'not_existing_rule_id'},
        {},
        {},
        404,
        {
            'code': 'not_found',
            'message': 'Rule with id `not_existing_rule_id` not found',
        },
    ),
    # park is individual entrepreneur, config enabled
    (
        'park_id1',
        {},
        {'driver_partner_source': 'self_assign'},
        {'DRIVER_WORK_MODES_ENABLE_DRIVER_FIX_FOR_INDIVIDUALS': True},
        200,
        {
            'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT},
            **DRIVER_FIX_RANGE,
        },
    ),
    # park is individual entrepreneur, config disabled
    (
        'park_id1',
        {},
        {'driver_partner_source': 'self_assign'},
        {'DRIVER_WORK_MODES_ENABLE_DRIVER_FIX_FOR_INDIVIDUALS': False},
        200,
        {'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT}},
    ),
    # driver fix enabled in park by config
    (
        'park_id_driver_fix_enabled',
        {},
        {'id': 'park_id_driver_fix_enabled'},
        {},
        200,
        {
            'calc_table': {
                **ORDER_TYPES_EMPTY,
                **CALC_ENTRY_RANGE_CONFIG_DEFAULT,
            },
            **DRIVER_FIX_RANGE,
        },
    ),
    # driver fix disabled in park by config
    (
        'park_id_driver_fix_disabled',
        {},
        {'id': 'park_id_driver_fix_disabled'},
        {},
        200,
        {
            'calc_table': {
                **ORDER_TYPES_EMPTY,
                **CALC_ENTRY_RANGE_CONFIG_DEFAULT,
            },
        },
    ),
    # driver fix enabled in city by config
    (
        'park_id1',
        {},
        {'city_id': 'city_driver_fix_enabled'},
        {},
        200,
        {
            'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT},
            **DRIVER_FIX_RANGE,
        },
    ),
    # driver fix disabled in city by config
    (
        'park_id1',
        {},
        {'city_id': 'city_driver_fix_disabled'},
        {},
        200,
        {'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT}},
    ),
    # driver fix disabled, no city in config
    (
        'park_id1',
        {},
        {'city_id': 'city_driver_fix_disabled_no_in_config'},
        {},
        200,
        {'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT}},
    ),
    # driver fix enabled in ita by config
    (
        'park_id1',
        {},
        {'country_id': 'ita'},
        {},
        200,
        {
            'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT},
            **DRIVER_FIX_RANGE,
        },
    ),
    # driver fix disabled in usa by config
    (
        'park_id1',
        {},
        {'country_id': 'usa'},
        {},
        200,
        {'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT}},
    ),
    # driver fix disabled, no aze in config
    (
        'park_id1',
        {},
        {'country_id': 'aze'},
        {},
        200,
        {'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT}},
    ),
    # subvention enabled in country rus by config
    (
        'park_id1',
        {},
        {'country_id': 'rus'},
        {},
        200,
        {
            'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT},
            **SUBVENTION_RANGE,
        },
    ),
    # workshift enabled in park
    (
        'park_id1',
        {'compatible_rule_id': 'work_rule_id_type_park'},
        {'is_workshift_enabled': True},
        {},
        200,
        {
            'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT},
            **WORKSHIFT_RANGE_CONFIG_DEFAULT,
        },
    ),
    # check calc entry and workshift range of rule with type park in Corleone
    (
        'park_id1',
        {'compatible_rule_id': 'work_rule_id_type_park'},
        {'city_id': 'Corleone', 'is_workshift_enabled': True},
        {},
        200,
        {
            'calc_table': {
                **ORDER_TYPES_3,
                'commission_percent_range': {'min': '10', 'max': '90'},
            },
            'workshift_commission_percent_range': {'min': '9', 'max': '50'},
        },
    ),
    # check calc entry and workshift range of rule with type commercial hiring
    # in Corleone
    (
        'park_id1',
        {'compatible_rule_id': 'work_rule_id_type_commercial_hiring'},
        {'city_id': 'Corleone', 'is_workshift_enabled': True},
        {},
        200,
        {
            'calc_table': {
                **ORDER_TYPES_3,
                'commission_percent_range': {'min': '5.3', 'max': '18'},
            },
            'workshift_commission_percent_range': {
                'min': '33.3',
                'max': '60.1',
            },
        },
    ),
    # check calc entry and workshift range from default config
    # of rule with type park
    (
        'park_id1',
        {'compatible_rule_id': 'work_rule_id_type_park'},
        {'is_workshift_enabled': True},
        {},
        200,
        {
            'calc_table': {**ORDER_TYPES_3, **CALC_ENTRY_RANGE_CONFIG_DEFAULT},
            **WORKSHIFT_RANGE_CONFIG_DEFAULT,
        },
    ),
    # check calc entry and workshift range from default config
    # of rule with type commercial hiring
    (
        'park_id1',
        {'compatible_rule_id': 'work_rule_id_type_commercial_hiring'},
        {'is_workshift_enabled': True},
        {},
        200,
        {
            'calc_table': {
                **ORDER_TYPES_3,
                'commission_percent_range': {'min': '2.1', 'max': '20.3'},
            },
            'workshift_commission_percent_range': {'min': '12', 'max': '30.9'},
        },
    ),
    # check calc entry and workshift range from driver hiring park settings
    (
        'park_id1',
        {'compatible_rule_id': 'work_rule_id_type_commercial_hiring'},
        {
            'is_workshift_enabled': True,
            'driver_hiring': {
                'commercial_hiring_commission_min': '12.3',
                'commercial_hiring_commission_max': '15.0',
                'commercial_hiring_workshift_commission_min': '3',
                'commercial_hiring_workshift_commission_max': '9',
            },
        },
        {},
        200,
        {
            'calc_table': {
                'commission_percent_range': {'min': '12.3', 'max': '15'},
                **ORDER_TYPES_3,
            },
            'workshift_commission_percent_range': {'min': '3', 'max': '9'},
        },
    ),
    # check calc entry and workshift range partially from driver hiring
    # park settings
    (
        'park_id1',
        {'compatible_rule_id': 'work_rule_id_type_commercial_hiring'},
        {
            'is_workshift_enabled': True,
            'driver_hiring': {
                'commercial_hiring_commission_min': '12.3',
                'commercial_hiring_workshift_commission_min': '3',
            },
        },
        {},
        200,
        {
            'calc_table': {
                'commission_percent_range': {'min': '12.3', 'max': '20.3'},
                **ORDER_TYPES_3,
            },
            'workshift_commission_percent_range': {'min': '3', 'max': '30.9'},
        },
    ),
]


@pytest.mark.redis_store(file='redis')
@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.parametrize(
    'park_id,params,park,config,expected_status_code,expected_response',
    TEST_OK_PARAMS,
)
async def test_get(
        taxi_driver_work_rules,
        taxi_config,
        mock_fleet_parks_list,
        park_id,
        params,
        config,
        park,
        expected_status_code,
        expected_response,
):
    taxi_config.set_values(config)
    mock_fleet_parks_list.set_parks([utils.modify_base_dict(BASE_PARK, park)])

    response = await taxi_driver_work_rules.get(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS, {'X-Park-Id': park_id},
        ),
        params=params,
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_response
