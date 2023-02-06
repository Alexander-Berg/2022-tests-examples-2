import datetime
import decimal
import json

import pytest
import pytz

from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils


ENDPOINT = 'sync/v1/work-rules'

ID = 'id'
SUBTYPE = 'subtype'

BASE_REQUEST_WORK_RULE_FOR_PUT = utils.modify_base_dict(
    defaults.BASE_REQUEST_WORK_RULE,
    {
        'id': 'extra_super_work_rule_id',
        'calc_table': [
            defaults.BASE_CALC_TABLE_ENTRY,
            {
                'commission_fixed': '5.6000',
                'commission_percent': '7.8000',
                'order_type_id': 'extra_super_order_type2',
                'is_enabled': False,
            },
            {
                'commission_fixed': '0.0001',
                'commission_percent': '0.0002',
                'order_type_id': 'extra_super_order_type3',
                'is_enabled': True,
            },
        ],
    },
)

EXPECTED_REDIS_CALC_TABLE = {
    'extra_super_order_type1': {'Fix': 1.2, 'IsEnabled': True, 'Percent': 3.4},
    'extra_super_order_type2': {
        'Fix': 5.6,
        'IsEnabled': False,
        'Percent': 7.8,
    },
    'extra_super_order_type3': {
        'Fix': 0.0001,
        'IsEnabled': True,
        'Percent': 0.0002,
    },
}


@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:extra_super_park_id',
        {
            'extra_super_order_type1': json.dumps(
                {'Name': 'extra_super_name1'},
            ),
            'extra_super_order_type2': json.dumps(
                {'Name': 'extra_super_name2'},
            ),
            'extra_super_order_type3': json.dumps(
                {'Name': 'extra_super_name3'},
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'params, tested_fields, expected_response',
    [
        (None, None, {'code': '400', 'message': 'Missing park_id in query'}),
        (
            defaults.PARAMS,
            {
                'id': defaults.COMMERCIAL_HIRING_RULE_ID,
                'subtype': 'default',
                'type': 'park',
            },
            {
                'code': '400',
                'message': 'Work rule id is mismatch with subtype',
            },
        ),
        (
            defaults.PARAMS,
            {
                'subtype': 'uber_integration',
                'type': 'commercial_hiring',
                'id': 'extra_super_work_rule_id',
            },
            {
                'code': '400',
                'message': (
                    'Type \'commercial_hiring\' must contain only '
                    '\'default\' subtype'
                ),
            },
        ),
        (
            defaults.PARAMS,
            {'commission_for_subvention_percent': '123.4567'},
            {
                'code': '400',
                'message': (
                    'Value of '
                    '\'work_rule.commission_for_subvention_percent\' '
                    'must be between 0 and 100'
                ),
            },
        ),
        (
            defaults.PARAMS,
            {
                'calc_table': [
                    defaults.BASE_CALC_TABLE_ENTRY,
                    {
                        'commission_fixed': '5.6000',
                        'commission_percent': '7.8000',
                        'order_type_id': 'extra_super_order_type2',
                        'is_enabled': False,
                    },
                    {
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                        'order_type_id': 'extra_super_order_type4',
                        'is_enabled': True,
                    },
                ],
            },
            {
                'code': '400',
                'message': (
                    'Park has no order type with id extra_super_order_type4'
                ),
            },
        ),
        (
            defaults.PARAMS,
            {'calc_table': [defaults.BASE_CALC_TABLE_ENTRY]},
            {
                'code': '400',
                'message': 'Value of \'calc_table\' has invalid size',
            },
        ),
    ],
)
async def test_bad_request(
        taxi_driver_work_rules, params, tested_fields, expected_response,
):
    request_body = {
        'work_rule': utils.modify_base_dict(
            BASE_REQUEST_WORK_RULE_FOR_PUT, tested_fields,
        ),
    }
    response = await taxi_driver_work_rules.put(
        ENDPOINT, params=params, headers=defaults.HEADERS, json=request_body,
    )
    assert response.status_code == 400
    assert response.json() == expected_response


@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:extra_super_park_id',
        {
            'extra_super_order_type1': json.dumps(
                {'Name': 'extra_super_name1'},
            ),
            'extra_super_order_type2': json.dumps(
                {'Name': 'extra_super_name2'},
            ),
            'extra_super_order_type3': json.dumps(
                {'Name': 'extra_super_name3'},
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'params, tested_fields',
    [
        (
            defaults.PARAMS,
            {
                'id': defaults.COMMERCIAL_HIRING_RULE_ID,
                'subtype': 'default',
                'type': 'park',
            },
        ),
        (defaults.PARAMS, {'id': None}),
        (
            defaults.PARAMS,
            {
                'calc_table': [
                    {
                        'commission_fixed': '1.2000',
                        'order_type_id': 'extra_super_order_type1',
                        'is_enabled': True,
                    },
                    {
                        'commission_fixed': '5.6000',
                        'commission_percent': '7.8000',
                        'order_type_id': 'extra_super_order_type2',
                        'is_enabled': False,
                    },
                    {
                        'commission_fixed': '0.0001',
                        'commission_percent': '0.0002',
                        'order_type_id': 'extra_super_order_type3',
                        'is_enabled': True,
                    },
                ],
            },
        ),
    ],
)
async def test_bad_request_codegen(
        taxi_driver_work_rules, params, tested_fields,
):
    request_body = {
        'work_rule': utils.modify_base_dict(
            BASE_REQUEST_WORK_RULE_FOR_PUT, tested_fields,
        ),
    }
    response = await taxi_driver_work_rules.put(
        ENDPOINT, params=params, headers=defaults.HEADERS, json=request_body,
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.parametrize(
    'params, request_work_rule, expected_redis_work_rule,'
    'expected_pg_work_rule',
    [
        (
            defaults.PARAMS,
            utils.modify_base_dict(
                BASE_REQUEST_WORK_RULE_FOR_PUT,
                {
                    'id': defaults.UBER_INTEGRATION_RULE_ID,
                    'calc_table': [],
                    'subtype': 'uber_integration',
                    'type': 'park',
                },
            ),
            utils.modify_base_dict(defaults.BASE_REDIS_RULE, {'Type': 0}),
            {
                'park_id': 'extra_super_park_id',
                'id': '551dbceed3fc40faa90532307dceffe8',
                'idempotency_token': None,
                'commission_for_driver_fix_percent': decimal.Decimal(
                    '12.3456',
                ),
                'commission_for_subvention_percent': decimal.Decimal('3.2100'),
                'commission_for_workshift_percent': decimal.Decimal('1.2300'),
                'is_archived': False,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_default': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'Name',
                'type': 'park',
            },
        ),
    ],
)
async def test_ok_with_empty_init_storage(
        taxi_driver_work_rules,
        pgsql,
        redis_store,
        params,
        request_work_rule,
        expected_redis_work_rule,
        expected_pg_work_rule,
):
    request_body = {'work_rule': request_work_rule}
    work_rule_id = request_work_rule[ID]

    response = await taxi_driver_work_rules.put(
        ENDPOINT, params=params, headers=defaults.HEADERS, json=request_body,
    )
    assert response.status_code == 200
    assert response.json() == request_work_rule

    pg_work_rule = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, defaults.UBER_INTEGRATION_RULE_ID,
    )
    assert pg_work_rule['created_at'] == pg_work_rule['updated_at']
    pg_work_rule.pop('created_at')
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    assert now > pg_work_rule['updated_at']
    pg_work_rule.pop('updated_at')
    assert pg_work_rule == expected_pg_work_rule

    assert (
        utils.get_redis_calc_table(redis_store, defaults.PARK_ID, work_rule_id)
        == {}
    )


@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:extra_super_park_id',
        {
            'extra_super_order_type1': json.dumps(
                {'Name': 'extra_super_name1'},
            ),
            'extra_super_order_type2': json.dumps(
                {'Name': 'extra_super_name2'},
            ),
            'extra_super_order_type3': json.dumps(
                {'Name': 'extra_super_name3'},
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'request_work_rule, expected_pg_work_rule',
    [
        (
            utils.modify_base_dict(
                BASE_REQUEST_WORK_RULE_FOR_PUT,
                {
                    'type': 'commercial_hiring',
                    'id': defaults.COMMERCIAL_HIRING_RULE_ID,
                },
            ),
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {'park_id': defaults.PARK_ID, 'type': 'commercial_hiring'},
            ),
        ),
        (
            utils.modify_base_dict(
                BASE_REQUEST_WORK_RULE_FOR_PUT,
                {'type': 'commercial_hiring_with_car'},
            ),
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'park_id': defaults.PARK_ID,
                    'type': 'commercial_hiring_with_car',
                },
            ),
        ),
        (
            utils.modify_base_dict(
                BASE_REQUEST_WORK_RULE_FOR_PUT,
                {
                    'subtype': 'default',
                    'type': 'vezet',
                    'id': defaults.VEZET_RULE_ID,
                },
            ),
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {'park_id': defaults.PARK_ID, 'type': 'vezet'},
            ),
        ),
    ],
)
async def test_creating_ok(
        taxi_driver_work_rules,
        redis_store,
        pgsql,
        request_work_rule,
        expected_pg_work_rule,
):

    request_body = {'work_rule': request_work_rule}
    work_rule_id = request_work_rule[ID]

    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=request_body,
    )

    assert response.status_code == 200

    response_rule = response.json()
    assert response_rule == request_work_rule

    pg_work_rule = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, response_rule['id'],
    )
    assert pg_work_rule['created_at'] == pg_work_rule['updated_at']
    pg_work_rule.pop('created_at')
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    assert now > pg_work_rule['updated_at']
    pg_work_rule.pop('updated_at')
    pg_work_rule.pop('id')
    assert pg_work_rule == expected_pg_work_rule

    assert (
        utils.get_redis_calc_table(redis_store, defaults.PARK_ID, work_rule_id)
        == EXPECTED_REDIS_CALC_TABLE
    )


@pytest.mark.pgsql('driver-work-rules', files=['test_updating_ok.sql'])
@pytest.mark.redis_store(
    [
        'hmset',
        utils.build_calc_table_redis_key(
            'extra_super_park_id2', 'extra_super_work_rule_id',
        ),
        {
            'extra_super_order_type1': json.dumps(
                defaults.BASE_REDIS_CALC_TABLE_ENTRY,
            ),
            'extra_super_order_type2': json.dumps({'Fix': 1.2000}),
        },
    ],
    [
        'hmset',
        utils.build_calc_table_redis_key(
            'extra_super_park_id2', defaults.VEZET_RULE_ID,
        ),
        {'extra_super_order_type1': json.dumps({'IsEnabled': True})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:extra_super_park_id2',
        {
            'extra_super_order_type1': json.dumps(
                {'Name': 'extra_super_name1'},
            ),
            'extra_super_order_type2': json.dumps(
                {'Name': 'extra_super_name2'},
            ),
            'extra_super_order_type3': json.dumps(
                {'Name': 'extra_super_name3'},
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'request_work_rule, expected_pg_work_rule',
    [
        (
            utils.modify_base_dict(
                BASE_REQUEST_WORK_RULE_FOR_PUT,
                {'type': 'park', 'id': 'extra_super_work_rule_id'},
            ),
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'park_id': 'extra_super_park_id2',
                    'id': 'extra_super_work_rule_id',
                    'type': 'park',
                },
            ),
        ),
        (
            utils.modify_base_dict(
                BASE_REQUEST_WORK_RULE_FOR_PUT,
                {
                    'id': defaults.VEZET_RULE_ID,
                    'type': 'vezet',
                    'subtype': 'default',
                },
            ),
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'park_id': 'extra_super_park_id2',
                    'id': defaults.VEZET_RULE_ID,
                    'type': 'vezet',
                },
            ),
        ),
    ],
)
async def test_updating_ok(
        taxi_driver_work_rules,
        redis_store,
        pgsql,
        request_work_rule,
        expected_pg_work_rule,
):
    request_body = {'work_rule': request_work_rule}
    work_rule_id = request_work_rule[ID]

    old_pg_work_rule = utils.get_postgres_work_rule(
        pgsql, 'extra_super_park_id2', work_rule_id,
    )
    old_created_at = old_pg_work_rule['created_at']
    old_updated_at = old_pg_work_rule['updated_at']
    assert old_created_at <= old_updated_at

    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        params={'park_id': 'extra_super_park_id2'},
        headers=defaults.HEADERS,
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == request_work_rule

    pg_work_rule = utils.get_postgres_work_rule(
        pgsql, 'extra_super_park_id2', work_rule_id,
    )
    assert old_created_at == pg_work_rule['created_at']
    pg_work_rule.pop('created_at')
    assert old_updated_at < pg_work_rule['updated_at']
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    assert now > pg_work_rule['updated_at']
    pg_work_rule.pop('updated_at')
    assert pg_work_rule == expected_pg_work_rule

    assert (
        utils.get_redis_calc_table(
            redis_store, 'extra_super_park_id2', work_rule_id,
        )
        == EXPECTED_REDIS_CALC_TABLE
    )
