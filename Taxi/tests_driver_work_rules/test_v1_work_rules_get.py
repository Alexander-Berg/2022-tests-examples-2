import json

import pytest

from testsuite.utils import ordered_object

from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils


ENDPOINT = 'v1/work-rules'

HEADERS = {'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET}


@pytest.mark.parametrize(
    'params, expected_response',
    [
        (None, {'code': '400', 'message': 'Missing park_id in query'}),
        (defaults.PARAMS, {'code': '400', 'message': 'Missing id in query'}),
        (
            utils.modify_base_dict(defaults.PARAMS, {'id': ''}),
            {
                'code': '400',
                'message': (
                    'Value of query \'id\': incorrect size, '
                    'must be 1 (limit) <= 0 (value)'
                ),
            },
        ),
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': 'extra_super_invalid_rule_id'},
            ),
            {'code': '400', 'message': 'Work rule was not found'},
        ),
    ],
)
async def test_bad_request(taxi_driver_work_rules, params, expected_response):
    response = await taxi_driver_work_rules.get(
        ENDPOINT, headers=HEADERS, params=params,
    )
    assert response.status_code == 400
    assert response.json() == expected_response


@pytest.mark.pgsql('driver-work-rules', files=['test_ok.sql'])
@pytest.mark.redis_store(
    [
        'hmset',
        utils.build_calc_table_redis_key(
            defaults.PARK_ID, 'extra_super_work_rule_id1',
        ),
        {
            'extra_super_order_type1': json.dumps(
                defaults.BASE_REDIS_CALC_TABLE_ENTRY,
            ),
            'extra_super_order_type2': json.dumps(
                {'Fix': 9, 'IsEnabled': False, 'Percent': 8.0},
            ),
        },
    ],
    [
        'hmset',
        utils.build_calc_table_redis_key(
            defaults.PARK_ID, defaults.PARK_SELFREG_RULE_ID,
        ),
        {
            'extra_super_order_type1': json.dumps(
                defaults.BASE_REDIS_CALC_TABLE_ENTRY,
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:extra_super_park_id',
        {
            'extra_super_order_type1': json.dumps(
                {'Name': 'extra_super_name1'},
            ),
            'extra_super_order_type2': json.dumps({}),
            'extra_super_order_type3': json.dumps({}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Aggregator:Financial:extra_super_aggregator_id',
        {'2_СommissionAggregator': 5.0, '2_WorkShiftCommission': 5.43},
    ],
)
@pytest.mark.parametrize(
    'params, expected_response',
    [
        (
            utils.modify_base_dict(
                defaults.PARAMS,
                {
                    'id': 'extra_super_work_rule_id1',
                    'is_agg_commission_requested': True,
                },
            ),
            {
                'calc_table': [
                    {
                        'commission_fixed': '1.2000',
                        'commission_percent': '3.4000',
                        'order_type_id': 'extra_super_order_type1',
                        'order_type_name': 'extra_super_name1',
                        'is_enabled': True,
                    },
                    {
                        'commission_fixed': '9.0000',
                        'commission_percent': '8.0000',
                        'order_type_id': 'extra_super_order_type2',
                        'is_enabled': False,
                    },
                    {
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                        'order_type_id': 'extra_super_order_type3',
                        'is_enabled': False,
                    },
                ],
                'commission_for_aggregator_percent': '5.0',
                'commission_for_driver_fix_percent': '12.3456',
                'commission_for_subvention_percent': '3.2100',
                'commission_for_workshift_percent': '1.2300',
                'commission_for_workshift_aggregator_percent': '5.43',
                'id': 'extra_super_work_rule_id1',
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'Name',
                'type': 'park',
            },
        ),
        (
            {
                'park_id': 'extra_super_park_id2',
                'id': defaults.PARK_SELFREG_RULE_ID,
            },
            {
                'calc_table': [],
                'commission_for_driver_fix_percent': '12.3456',
                'commission_for_subvention_percent': '3.2100',
                'commission_for_workshift_percent': '1.2300',
                'id': defaults.PARK_SELFREG_RULE_ID,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'Name',
                'subtype': 'selfreg',
                'type': 'park',
            },
        ),
    ],
)
async def test_ok(
        taxi_driver_work_rules,
        mock_fleet_parks_list,
        params,
        expected_response,
):
    response = await taxi_driver_work_rules.get(
        ENDPOINT, headers=HEADERS, params=params,
    )

    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), expected_response, ['calc_table'],
    )


async def test_ok_from_master(
        taxi_driver_work_rules,
        mock_fleet_parks_list,
        mock_dispatcher_access_control,
        fleet_parks_shard,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {
            'author': defaults.BASE_REQUEST_AUTHOR,
            'work_rule': defaults.BASE_REQUEST_WORK_RULE,
        },
    )
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        params={'park_id': defaults.PARK_ID},
        headers=defaults.HEADERS,
        json=request_body,
    )
    work_rule_id = response.json()['id']

    params = {
        'park_id': defaults.PARK_ID,
        'id': work_rule_id,
        'from_master': True,
    }
    response = await taxi_driver_work_rules.get(
        ENDPOINT, headers=HEADERS, params=params,
    )

    assert response.status_code == 200
    expected_response = {
        'calc_table': [],
        'commission_for_driver_fix_percent': '12.3456',
        'commission_for_subvention_percent': '3.2100',
        'commission_for_workshift_percent': '1.2300',
        'id': work_rule_id,
        'is_commission_for_orders_cancelled_by_client_enabled': True,
        'is_commission_if_platform_commission_is_null_enabled': True,
        'is_driver_fix_enabled': False,
        'is_dynamic_platform_commission_enabled': True,
        'is_enabled': True,
        'is_workshift_enabled': True,
        'name': 'Name',
        'type': 'commercial_hiring',
    }
    ordered_object.assert_eq(
        response.json(), expected_response, ['calc_table'],
    )


async def test_fail_from_master(taxi_driver_work_rules):
    params = {
        'park_id': defaults.PARK_ID,
        'id': 'strange_work_rule_id',
        'from_master': True,
    }
    response = await taxi_driver_work_rules.get(
        ENDPOINT, headers=HEADERS, params=params,
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'Work rule was not found',
    }
