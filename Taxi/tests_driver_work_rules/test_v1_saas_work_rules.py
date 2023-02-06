import decimal
import json

import pytest

from testsuite.utils import ordered_object

from tests_driver_work_rules import changelog
from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils


ENDPOINT = 'fleet/dwr/v1/saas/work-rules'

HEADERS = {
    'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET,
    'X-Yandex-UID': '1000',
    'X-Ya-User-Ticket': 'TESTSUITE-USER-TICKET',
    'X-Ya-User-Ticket-Provider': 'yandex',
}


RULE_TYPES_3 = [
    'hmset',
    'RuleType:Items:extra_super_park_id3',
    {
        'extra_super_order_type31': json.dumps({'Name': 'extra_super_name31'}),
        'extra_super_order_type32': json.dumps({'Name': 'extra_super_name32'}),
        'extra_super_order_type33': json.dumps({'Name': 'extra_super_name33'}),
    },
]
RULE_TYPES_4 = [
    'hmset',
    'RuleType:Items:extra_super_park_id4',
    {
        'extra_super_order_type41': json.dumps({'Name': 'extra_super_name41'}),
        'extra_super_order_type42': json.dumps({'Name': 'extra_super_name42'}),
    },
]
CALC_TABLE_31 = [
    'hmset',
    utils.build_calc_table_redis_key(
        'extra_super_park_id3', 'extra_super_work_rule_id31',
    ),
    {
        'extra_super_order_type31': json.dumps(
            {'Fix': 9, 'IsEnabled': True, 'Percent': 0.0},
        ),
        'extra_super_order_type32': json.dumps(
            {'Fix': 9, 'IsEnabled': True, 'Percent': 0.0},
        ),
        'extra_super_order_type33': json.dumps(
            {'Fix': 9, 'IsEnabled': True, 'Percent': 0.0},
        ),
    },
]
CALC_TABLE_32 = [
    'hmset',
    utils.build_calc_table_redis_key(
        'extra_super_park_id3', 'extra_super_work_rule_id32',
    ),
    {
        'extra_super_order_type31': json.dumps(
            {'Fix': 0, 'IsEnabled': True, 'Percent': 9.0},
        ),
        'extra_super_order_type32': json.dumps(
            {'Fix': 0, 'IsEnabled': True, 'Percent': 9.0},
        ),
        'extra_super_order_type33': json.dumps(
            {'Fix': 0, 'IsEnabled': True, 'Percent': 9.0},
        ),
    },
]


@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.redis_store(CALC_TABLE_31, CALC_TABLE_32)
@pytest.mark.redis_store(RULE_TYPES_3)
@pytest.mark.parametrize(
    'extra_headers, params, response_code, expected_response',
    [
        (
            {'X-Park-ID': 'extra_super_park_id3'},
            {'id': 'extra_super_work_rule_id31'},
            200,
            {
                'id': 'extra_super_work_rule_id31',
                'work_rule': {
                    'commission_type': 'fixed',
                    'commission_value': '9.0000',
                    'name': 'Name31',
                },
            },
        ),
        (
            {'X-Park-ID': 'extra_super_park_id3'},
            {'id': 'extra_super_work_rule_id32'},
            200,
            {
                'id': 'extra_super_work_rule_id32',
                'work_rule': {
                    'commission_type': 'percent',
                    'commission_value': '9.0000',
                    'name': 'Name32',
                },
            },
        ),
        (
            {'X-Park-ID': 'extra_super_park_id4'},
            {'id': 'extra_super_work_rule_id41'},
            500,
            {'code': '500', 'message': 'Internal Server Error'},
        ),
        (
            {'X-Park-ID': 'extra_super_park_id2'},
            {'id': 'extra_super_work_rule_id21'},
            400,
            {
                'code': 'WORK_RULE_NOT_FOUND',
                'message': 'Work rule was not found',
            },
        ),
    ],
)
async def test_get(
        taxi_driver_work_rules,
        extra_headers,
        params,
        response_code,
        expected_response,
):
    response = await taxi_driver_work_rules.get(
        ENDPOINT, headers=dict(HEADERS, **extra_headers), params=params,
    )

    assert response.status_code == response_code
    ordered_object.assert_eq(
        response.json(), expected_response, ['calc_table'],
    )


@pytest.mark.pgsql('driver-work-rules', files=[])
@pytest.mark.redis_store(RULE_TYPES_3, RULE_TYPES_4)
@pytest.mark.parametrize(
    'extra_headers, request_body, expected_work_rule, expected_calc_table,'
    'expected_change_counts, expected_change_values',
    [
        (
            {
                'X-Park-ID': 'extra_super_park_id3',
                'X-Idempotency-Token': 'extra_super_work_rule_34',
            },
            {
                'commission_type': 'fixed',
                'commission_value': '1.2',
                'name': 'Name34',
            },
            {
                'park_id': 'extra_super_park_id3',
                'idempotency_token': 'extra_super_work_rule_34',
                'commission_for_driver_fix_percent': decimal.Decimal('0.0000'),
                'commission_for_subvention_percent': decimal.Decimal('0.0000'),
                'commission_for_workshift_percent': decimal.Decimal('0.0000'),
                'is_archived': False,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': False,
                'is_default': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': False,
                'name': 'Name34',
                'type': 'park',
            },
            {
                'extra_super_order_type31': {
                    'IsEnabled': True,
                    'Fix': 1.2,
                    'Percent': 0.0,
                },
                'extra_super_order_type32': {
                    'IsEnabled': True,
                    'Fix': 1.2,
                    'Percent': 0.0,
                },
                'extra_super_order_type33': {
                    'IsEnabled': True,
                    'Fix': 1.2,
                    'Percent': 0.0,
                },
            },
            20,
            '{"Name":{"old":"","current":"Name34"},'
            '"Type":{"old":"","current":"0"},'
            '"CommissionForDriverFixPercent":{"old":"","current":"0.0000"},'
            '"CommisisonForSubventionPercent":{"old":"","current":"0.0000"},'
            '"WorkshiftCommissionPercent":{"old":"","current":"0.0000"},'
            '"YandexDisableNullComission":{"old":"","current":"False"},'
            '"YandexDisablePayUserCancelOrder":{"old":"","current":"True"},'
            '"IsDriverFixEnabled":{"old":"","current":"False"},'
            '"DisableDynamicYandexCommission":{"old":"","current":"False"},'
            '"Enable":{"old":"","current":"True"},'
            '"WorkshiftsEnabled":{"old":"","current":"False"},'
            '"extra_super_name31 (Вкл)":{"old":"","current":"True"},'
            '"extra_super_name31 (%)":{"old":"","current":"0.0000"},'
            '"extra_super_name31":{"old":"","current":"1.2000"},'
            '"extra_super_name32 (Вкл)":{"old":"","current":"True"},'
            '"extra_super_name32 (%)":{"old":"","current":"0.0000"},'
            '"extra_super_name32":{"old":"","current":"1.2000"},'
            '"extra_super_name33 (%)":{"old":"","current":"0.0000"},'
            '"extra_super_name33 (Вкл)":{"old":"","current":"True"},'
            '"extra_super_name33":{"old":"","current":"1.2000"}}',
        ),
        (
            {
                'X-Park-ID': 'extra_super_park_id4',
                'X-Idempotency-Token': 'extra_super_work_rule_42',
            },
            {
                'commission_type': 'percent',
                'commission_value': '12',
                'name': 'Name42',
            },
            {
                'park_id': 'extra_super_park_id4',
                'idempotency_token': 'extra_super_work_rule_42',
                'commission_for_driver_fix_percent': decimal.Decimal('0.0000'),
                'commission_for_subvention_percent': decimal.Decimal('0.0000'),
                'commission_for_workshift_percent': decimal.Decimal('0.0000'),
                'is_archived': False,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': False,
                'is_default': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': False,
                'name': 'Name42',
                'type': 'park',
            },
            {
                'extra_super_order_type41': {
                    'IsEnabled': True,
                    'Fix': 0.0,
                    'Percent': 12.0,
                },
                'extra_super_order_type42': {
                    'IsEnabled': True,
                    'Fix': 0.0,
                    'Percent': 12.0,
                },
            },
            17,
            '{"Name":{"old":"","current":"Name42"},'
            '"Type":{"old":"","current":"0"},'
            '"CommissionForDriverFixPercent":{"old":"","current":"0.0000"},'
            '"CommisisonForSubventionPercent":{"old":"","current":"0.0000"},'
            '"WorkshiftCommissionPercent":{"old":"","current":"0.0000"},'
            '"YandexDisableNullComission":{"old":"","current":"False"},'
            '"YandexDisablePayUserCancelOrder":{"old":"","current":"True"},'
            '"IsDriverFixEnabled":{"old":"","current":"False"},'
            '"DisableDynamicYandexCommission":{"old":"","current":"False"},'
            '"Enable":{"old":"","current":"True"},'
            '"WorkshiftsEnabled":{"old":"","current":"False"},'
            '"extra_super_name41 (Вкл)":{"old":"","current":"True"},'
            '"extra_super_name41 (%)":{"old":"","current":"12.0000"},'
            '"extra_super_name41":{"old":"","current":"0.0000"},'
            '"extra_super_name42 (Вкл)":{"old":"","current":"True"},'
            '"extra_super_name42 (%)":{"old":"","current":"12.0000"},'
            '"extra_super_name42":{"old":"","current":"0.0000"}}',
        ),
    ],
)
async def test_post(
        taxi_driver_work_rules,
        fleet_parks_shard,
        redis_store,
        pgsql,
        extra_headers,
        request_body,
        expected_work_rule,
        expected_calc_table,
        expected_change_counts,
        expected_change_values,
):
    response = await taxi_driver_work_rules.post(
        ENDPOINT, headers=dict(HEADERS, **extra_headers), json=request_body,
    )
    response_json = response.json()

    assert response.status_code == 200
    assert request_body == response_json['work_rule']

    park_id = extra_headers['X-Park-ID']
    rule_id = response_json['id']
    pg_work_rule = utils.get_postgres_work_rule(pgsql, park_id, rule_id)

    assert expected_work_rule == {
        k: v
        for k, v in pg_work_rule.items()
        if k not in ['id', 'created_at', 'updated_at']
    }

    # redis calc table
    real_redis_calc_table_value = redis_store.hgetall(
        utils.build_calc_table_redis_key(park_id, rule_id),
    )
    current_redis_calc_table_value = {
        key.decode('ascii'): json.loads(value)
        for key, value in real_redis_calc_table_value.items()
    }

    assert current_redis_calc_table_value == expected_calc_table

    log_info = defaults.LOG_INFO.copy()
    log_info['park_id'] = park_id
    log_info['counts'] = expected_change_counts
    log_info['ip'] = ''
    changelog.check_work_rule_changes(pgsql, log_info, expected_change_values)


@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.redis_store(CALC_TABLE_31, CALC_TABLE_32)
@pytest.mark.redis_store(RULE_TYPES_3, RULE_TYPES_4)
@pytest.mark.parametrize(
    'extra_headers, query, request_body, expected_work_rule,'
    'expected_calc_table, expected_change_counts, expected_change_values',
    [
        (
            {'X-Park-ID': 'extra_super_park_id3'},
            {'id': 'extra_super_work_rule_id31'},
            {
                'commission_type': 'fixed',
                'commission_value': '12',
                'name': 'Name331',
            },
            {
                'id': 'extra_super_work_rule_id31',
                'park_id': 'extra_super_park_id3',
                'idempotency_token': 'extra_super_work_rule_31',
                'commission_for_driver_fix_percent': decimal.Decimal('0.0000'),
                'commission_for_subvention_percent': decimal.Decimal('0.0000'),
                'commission_for_workshift_percent': decimal.Decimal('0.0000'),
                'is_archived': False,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': False,
                'is_default': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': False,
                'name': 'Name331',
                'type': 'park',
            },
            {
                'extra_super_order_type31': {
                    'IsEnabled': True,
                    'Fix': 12.0,
                    'Percent': 0.0,
                },
                'extra_super_order_type32': {
                    'IsEnabled': True,
                    'Fix': 12.0,
                    'Percent': 0.0,
                },
                'extra_super_order_type33': {
                    'IsEnabled': True,
                    'Fix': 12.0,
                    'Percent': 0.0,
                },
            },
            4,
            '{"Name":{"old":"Name31","current":"Name331"},'
            '"extra_super_name33":{"old":"9.0000","current":"12.0000"},'
            '"extra_super_name31":{"old":"9.0000","current":"12.0000"},'
            '"extra_super_name32":{"old":"9.0000","current":"12.0000"}}',
        ),
        (
            {'X-Park-ID': 'extra_super_park_id3'},
            {'id': 'extra_super_work_rule_id31'},
            {
                'commission_type': 'percent',
                'commission_value': '12',
                'name': 'Name3331',
            },
            {
                'id': 'extra_super_work_rule_id31',
                'park_id': 'extra_super_park_id3',
                'idempotency_token': 'extra_super_work_rule_31',
                'commission_for_driver_fix_percent': decimal.Decimal('0.0000'),
                'commission_for_subvention_percent': decimal.Decimal('0.0000'),
                'commission_for_workshift_percent': decimal.Decimal('0.0000'),
                'is_archived': False,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': False,
                'is_default': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': False,
                'name': 'Name3331',
                'type': 'park',
            },
            {
                'extra_super_order_type31': {
                    'IsEnabled': True,
                    'Fix': 0.0,
                    'Percent': 12.0,
                },
                'extra_super_order_type32': {
                    'IsEnabled': True,
                    'Fix': 0.0,
                    'Percent': 12.0,
                },
                'extra_super_order_type33': {
                    'IsEnabled': True,
                    'Fix': 0.0,
                    'Percent': 12.0,
                },
            },
            7,
            '{"Name":{"old":"Name31","current":"Name3331"},'
            '"extra_super_name31 (%)":{"old":"0.0000","current":"12.0000"},'
            '"extra_super_name31":{"old":"9.0000","current":"0.0000"},'
            '"extra_super_name32 (%)":{"old":"0.0000","current":"12.0000"},'
            '"extra_super_name32":{"old":"9.0000","current":"0.0000"},'
            '"extra_super_name33 (%)":{"old":"0.0000","current":"12.0000"},'
            '"extra_super_name33":{"old":"9.0000","current":"0.0000"}}',
        ),
    ],
)
async def test_put(
        taxi_driver_work_rules,
        fleet_parks_shard,
        redis_store,
        pgsql,
        extra_headers,
        query,
        request_body,
        expected_work_rule,
        expected_calc_table,
        expected_change_counts,
        expected_change_values,
):
    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        headers=dict(HEADERS, **extra_headers),
        params=query,
        json=request_body,
    )
    response_json = response.json()

    assert response.status_code == 200
    assert request_body == response_json['work_rule']

    park_id = extra_headers['X-Park-ID']
    rule_id = query['id']
    pg_work_rule = utils.get_postgres_work_rule(pgsql, park_id, rule_id)

    assert expected_work_rule == {
        k: v
        for k, v in pg_work_rule.items()
        if k not in ['created_at', 'updated_at']
    }

    # redis calc table
    real_redis_calc_table_value = redis_store.hgetall(
        utils.build_calc_table_redis_key(park_id, rule_id),
    )
    current_redis_calc_table_value = {
        key.decode('ascii'): json.loads(value)
        for key, value in real_redis_calc_table_value.items()
    }

    assert current_redis_calc_table_value == expected_calc_table

    log_info = defaults.LOG_INFO.copy()
    log_info['park_id'] = park_id
    log_info['counts'] = expected_change_counts
    log_info['ip'] = ''
    changelog.check_work_rule_changes(pgsql, log_info, expected_change_values)


@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.redis_store(CALC_TABLE_31, CALC_TABLE_32)
@pytest.mark.redis_store(RULE_TYPES_3, RULE_TYPES_4)
@pytest.mark.parametrize(
    'extra_headers, query, request_body',
    [
        (
            {'X-Park-ID': 'extra_super_park_id3'},
            {'id': 'extra_super_work_rule_id51'},
            {
                'commission_type': 'fixed',
                'commission_value': '12',
                'name': 'Name331',
            },
        ),
        (
            {'X-Park-ID': 'extra_super_park_id5'},
            {'id': 'extra_super_work_rule_id31'},
            {
                'commission_type': 'fixed',
                'commission_value': '12',
                'name': 'Name331',
            },
        ),
    ],
)
async def test_put_non_exist(
        taxi_driver_work_rules,
        fleet_parks_shard,
        redis_store,
        pgsql,
        extra_headers,
        query,
        request_body,
):
    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        headers=dict(HEADERS, **extra_headers),
        params=query,
        json=request_body,
    )

    assert response.status_code == 400
    assert response.json() == {
        'code': 'WORK_RULE_NOT_FOUND',
        'message': 'Driver\'s work rule doesn\'t exist',
    }

    park_id = extra_headers['X-Park-ID']
    rule_id = query['id']
    pg_work_rule = utils.get_postgres_work_rule(pgsql, park_id, rule_id)

    assert pg_work_rule is None

    real_redis_calc_table_value = redis_store.hgetall(
        utils.build_calc_table_redis_key(park_id, rule_id),
    )

    assert real_redis_calc_table_value == {}
