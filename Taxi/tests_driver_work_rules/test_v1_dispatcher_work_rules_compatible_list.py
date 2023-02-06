# encoding=utf-8
import json

import pytest

from testsuite.utils import ordered_object

from tests_driver_work_rules import defaults


ENDPOINT = '/v1/dispatcher/work-rules/compatible/list'

HEADERS = {'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET}


@pytest.mark.pgsql('driver-work-rules', files=['test_type_filter.sql'])
@pytest.mark.redis_store(
    [
        'hmset',
        defaults.RULE_WORK_ITEMS_PREFIX + defaults.PARK_ID,
        {
            '1.1': json.dumps({'Type': 1}),
            '1.2': json.dumps({'Type': 3}),
            '2.1': json.dumps({'Type': 2}),
            '3.1': json.dumps({'Type': 3}),
            '3.2': json.dumps({'Type': 3}),
            '2.2': json.dumps({'Type': 2}),
        },
    ],
)
@pytest.mark.parametrize(
    'compatible_with_id,park_id,status_code,expected_response',
    [
        (
            '2.2',
            defaults.PARK_ID,
            200,
            {
                'work_rules': [
                    {
                        'commission_for_driver_fix_percent': '0.0000',
                        'commission_for_subvention_percent': '0.0000',
                        'commission_for_workshift_percent': '0.0000',
                        'id': '2.1',
                        'is_commission_for_orders_cancelled_by_client_'
                        'enabled': True,
                        'is_commission_if_platform_commission_is_null_'
                        'enabled': True,
                        'is_driver_fix_enabled': False,
                        'is_dynamic_platform_commission_enabled': True,
                        'is_enabled': False,
                        'is_workshift_enabled': False,
                        'name': '',
                        'type': 'commercial_hiring_with_car',
                    },
                    {
                        'commission_for_driver_fix_percent': '0.0000',
                        'commission_for_subvention_percent': '0.0000',
                        'commission_for_workshift_percent': '0.0000',
                        'id': '2.2',
                        'is_commission_for_orders_cancelled_by_client_'
                        'enabled': True,
                        'is_commission_if_platform_commission_is_null_'
                        'enabled': True,
                        'is_driver_fix_enabled': False,
                        'is_dynamic_platform_commission_enabled': True,
                        'is_enabled': False,
                        'is_workshift_enabled': False,
                        'name': '',
                        'type': 'commercial_hiring_with_car',
                    },
                ],
            },
        ),
        (
            '1.1',
            defaults.PARK_ID,
            200,
            {
                'work_rules': [
                    {
                        'commission_for_driver_fix_percent': '0.0000',
                        'commission_for_subvention_percent': '0.0000',
                        'commission_for_workshift_percent': '0.0000',
                        'id': '1.1',
                        'is_commission_for_orders_cancelled_by_client_'
                        'enabled': True,
                        'is_commission_if_platform_commission_is_null_'
                        'enabled': True,
                        'is_driver_fix_enabled': False,
                        'is_dynamic_platform_commission_enabled': True,
                        'is_enabled': False,
                        'is_workshift_enabled': False,
                        'name': '',
                        'type': 'commercial_hiring',
                    },
                ],
            },
        ),
        (
            'unknown_rule_id',
            defaults.PARK_ID,
            400,
            {
                'code': '400',
                'message': 'Invalid compatible_with_id: unknown_rule_id',
            },
        ),
        (
            'rule_id',
            'unknown_park_id',
            400,
            {'code': '400', 'message': 'Park not found or has no work rules'},
        ),
    ],
)
async def test_type_filter(
        taxi_driver_work_rules,
        compatible_with_id,
        park_id,
        status_code,
        expected_response,
):
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=HEADERS,
        json={
            'query': {
                'park': {
                    'id': park_id,
                    'work_rule': {'compatible_with_id': compatible_with_id},
                },
            },
        },
    )

    assert response.status_code == status_code
    ordered_object.assert_eq(
        response.json(), expected_response, ['work_rules'],
    )
