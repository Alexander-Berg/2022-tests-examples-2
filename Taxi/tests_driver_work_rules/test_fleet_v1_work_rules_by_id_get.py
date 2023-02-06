import pytest

from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils

ENDPOINT = 'fleet/driver-work-rules/v1/work-rules/by-id'

FLEET_PARK = {
    'id': 'park_id1',
    'city_id': 'city_driver_fix_enabled',
    'country_id': 'rus',
    'demo_mode': False,
    'geodata': {'lat': 0, 'lon': 0, 'zoom': 0},
    'is_active': True,
    'is_billing_enabled': True,
    'is_workshift_enabled': True,
    'is_franchising_enabled': False,
    'locale': 'ru',
    'login': 'Al',
    'name': 'Pacino',
}

BASE_FLEET_WORK_RULE_RESPONSE = {
    'id': 'work_rule_id1',
    'calc_table': [
        {
            'commission_fixed': '1.2000',
            'commission_percent': '3.4000',
            'order_type_id': 'order_type_id1',
            'is_enabled': True,
        },
        {
            'commission_fixed': '0.0000',
            'commission_percent': '0.0000',
            'order_type_id': 'order_type_id2',
            'is_enabled': False,
        },
    ],
    'work_rule': {
        'commission_for_subvention_percent': '3.21',
        'commission_for_workshift_percent': '14.3',
        'commission_for_driver_fix_percent': '12.35',
        'is_archived': False,
        'is_commission_for_orders_cancelled_by_client_enabled': True,
        'is_commission_if_platform_commission_is_null_enabled': True,
        'is_default': False,
        'is_driver_fix_enabled': False,
        'is_dynamic_platform_commission_enabled': True,
        'is_enabled': True,
        'is_workshift_enabled': True,
        'name': 'Name',
        'type': 'park',
    },
}

TEST_GET_PARAMS = [
    (
        'park_id1',
        'work_rule_id1',
        FLEET_PARK,
        200,
        BASE_FLEET_WORK_RULE_RESPONSE,
    ),
    (
        'park_id1',
        'work_rule_id_without_calc_entries',
        FLEET_PARK,
        200,
        utils.modify_base_dict(
            BASE_FLEET_WORK_RULE_RESPONSE,
            {
                'id': 'work_rule_id_without_calc_entries',
                'calc_table': [
                    {
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                        'order_type_id': 'order_type_id1',
                        'is_enabled': False,
                    },
                    {
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                        'order_type_id': 'order_type_id2',
                        'is_enabled': False,
                    },
                ],
            },
        ),
    ),
    (
        'park_id1',
        'not_existing_work_rule_id',
        FLEET_PARK,
        404,
        {
            'code': 'not_found',
            'message': 'Rule with id `not_existing_work_rule_id` not found',
        },
    ),
    (
        'park_id1',
        'work_rule_id1',
        utils.modify_base_dict(FLEET_PARK, {'id': 'park_id2'}),
        404,
        {'code': 'not_found', 'message': 'Park with id `park_id1` not found'},
    ),
    (
        'park_id1',
        'work_rule_id1',
        utils.modify_base_dict(FLEET_PARK, {'country_id': 'not_existing'}),
        404,
        {
            'code': 'not_found',
            'message': 'Country with id `not_existing` not found',
        },
    ),
]


@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.redis_store(file='redis')
@pytest.mark.parametrize(
    'park_id,rule_id,fleet_park,expected_status_code,expected_response',
    TEST_GET_PARAMS,
)
async def test_get(
        taxi_driver_work_rules,
        mock_fleet_parks_list,
        park_id,
        rule_id,
        fleet_park,
        expected_status_code,
        expected_response,
):
    mock_fleet_parks_list.set_parks([fleet_park])
    response = await taxi_driver_work_rules.get(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS, {'X-Park-Id': park_id},
        ),
        params={'work_rule_id': rule_id},
    )

    assert response.status_code == expected_status_code
    assert response.json() == expected_response
