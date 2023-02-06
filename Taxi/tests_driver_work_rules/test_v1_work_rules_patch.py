import decimal
import json

import pytest

from testsuite.utils import ordered_object

from tests_driver_work_rules import changelog
from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils


ENDPOINT = 'v1/work-rules'


@pytest.mark.parametrize(
    'headers, expected_response',
    [
        (
            utils.modify_base_dict(
                defaults.HEADERS, {'X-Ya-Service-Ticket': ''},
            ),
            {
                'code': '401',
                'message': 'missing or empty X-Ya-Service-Ticket header',
            },
        ),
    ],
)
async def test_unauthorized(
        taxi_driver_work_rules, headers, expected_response,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {
            'author': defaults.BASE_REQUEST_AUTHOR,
            'work_rule': defaults.BASE_REQUEST_WORK_RULE,
        },
    )
    response = await taxi_driver_work_rules.patch(
        ENDPOINT, params=defaults.PARAMS, headers=headers, json=request_body,
    )
    assert response.status_code == 401
    assert response.json() == expected_response


@pytest.mark.pgsql('driver-work-rules', files=['test_bad_request.sql'])
@pytest.mark.parametrize(
    'params, headers, request_author, request_work_rule, expected_response',
    [
        (
            defaults.PARAMS,
            defaults.HEADERS,
            defaults.BASE_REQUEST_AUTHOR,
            defaults.BASE_REQUEST_WORK_RULE,
            {'code': '400', 'message': 'Missing id in query'},
        ),
        (
            {'park_id': defaults.PARK_ID, 'id': ''},
            defaults.HEADERS,
            defaults.BASE_REQUEST_AUTHOR,
            defaults.BASE_REQUEST_WORK_RULE,
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
            defaults.HEADERS,
            defaults.BASE_REQUEST_AUTHOR,
            defaults.BASE_REQUEST_WORK_RULE,
            {'code': '400', 'message': 'Driver\'s work rule doesn\'t exist'},
        ),
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': 'extra_super_work_rule_id'},
            ),
            defaults.HEADERS,
            defaults.BASE_REQUEST_AUTHOR,
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {
                    'calc_table': [
                        {
                            'commission_fixed': '1.11',
                            'commission_percent': '2.222',
                            'order_type_id': 'extra_super_invalid_order_type',
                            'is_enabled': False,
                        },
                    ],
                },
            ),
            {
                'code': '400',
                'message': (
                    'Calc table entry with '
                    'id extra_super_invalid_order_type not exists'
                ),
            },
        ),
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': 'extra_super_work_rule_id'},
            ),
            defaults.HEADERS,
            defaults.BASE_REQUEST_AUTHOR,
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {'commission_for_subvention_percent': '1,234'},
            ),
            {
                'code': '400',
                'message': (
                    'Field '
                    '\'work_rule.commission_for_subvention_percent\' '
                    'must be able to convert from string to decimal'
                ),
            },
        ),
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': 'extra_super_work_rule_id'},
            ),
            defaults.HEADERS,
            defaults.BASE_REQUEST_AUTHOR,
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {'commission_for_subvention_percent': '1,234'},
            ),
            {
                'code': '400',
                'message': (
                    'Field '
                    '\'work_rule.commission_for_subvention_percent\' '
                    'must be able to convert from string to decimal'
                ),
            },
        ),
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': defaults.VEZET_RULE_ID},
            ),
            defaults.HEADERS,
            defaults.BASE_REQUEST_AUTHOR,
            defaults.BASE_REQUEST_WORK_RULE,
            {'code': '400', 'message': 'Driver\'s work rule doesn\'t exist'},
        ),
    ],
)
async def test_bad_request(
        taxi_driver_work_rules,
        params,
        headers,
        request_author,
        request_work_rule,
        expected_response,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {'author': request_author, 'work_rule': request_work_rule},
    )
    response = await taxi_driver_work_rules.patch(
        ENDPOINT, params=params, headers=headers, json=request_body,
    )
    assert response.status_code == 400
    assert response.json() == expected_response


@pytest.mark.pgsql('driver-work-rules', files=['test_bad_request.sql'])
@pytest.mark.parametrize(
    'params, headers, request_author, request_work_rule',
    [
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': 'extra_super_work_rule_id'},
            ),
            defaults.HEADERS,
            {
                'consumer': 'extra_super_consumer',
                'identity': {
                    'type': 'invalid_type',
                    'user_ip': defaults.USER_IP,
                    'passport_uid': '1',
                },
            },
            defaults.BASE_REQUEST_WORK_RULE,
        ),
    ],
)
async def test_bad_request_codegen(
        taxi_driver_work_rules,
        params,
        headers,
        request_author,
        request_work_rule,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {'author': request_author, 'work_rule': request_work_rule},
    )
    response = await taxi_driver_work_rules.patch(
        ENDPOINT, params=params, headers=headers, json=request_body,
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


@pytest.mark.pgsql('driver-work-rules', files=['test_ok.sql'])
@pytest.mark.redis_store(
    [
        'hmset',
        utils.build_calc_table_redis_key(
            defaults.PARK_ID, 'extra_super_work_rule_id',
        ),
        {
            'extra_super_order_type1': json.dumps(
                defaults.BASE_REDIS_CALC_TABLE_ENTRY,
            ),
            'extra_super_order_type2': json.dumps(
                defaults.BASE_REDIS_CALC_TABLE_ENTRY,
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
            'extra_super_order_type2': json.dumps(
                {'Name': 'extra_super_name2'},
            ),
            'extra_super_order_type3': json.dumps({}),
        },
    ],
)
@pytest.mark.parametrize(
    'params, request_author, request_work_rule, expected_response,'
    'expected_pg_work_rule, expected_redis_calc_table, log_info_counts,'
    'expected_changelog_entry',
    [
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': 'extra_super_work_rule_id'},
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_YANDEX_AUTHOR_IDENTITY,
            ),
            {
                'calc_table': [
                    {
                        'commission_fixed': '1.11',
                        'commission_percent': '2.222',
                        'is_enabled': False,
                        'order_type_id': 'extra_super_order_type2',
                        'order_type_name': 'extra_super_name2',
                    },
                    {
                        'commission_fixed': '3.3',
                        'is_enabled': False,
                        'order_type_id': 'extra_super_order_type3',
                    },
                ],
                'commission_for_subvention_percent': '3.33333',
                'commission_for_workshift_percent': '4.4444',
                'commission_for_driver_fix_percent': '5.5555',
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'NewName',
            },
            {
                'id': 'extra_super_work_rule_id',
                'calc_table': [
                    {
                        'commission_fixed': '1.2000',
                        'commission_percent': '3.4000',
                        'is_enabled': True,
                        'order_type_id': 'extra_super_order_type1',
                        'order_type_name': 'extra_super_name1',
                    },
                    {
                        'commission_fixed': '1.1100',
                        'commission_percent': '2.2220',
                        'is_enabled': False,
                        'order_type_id': 'extra_super_order_type2',
                        'order_type_name': 'extra_super_name2',
                    },
                    {
                        'commission_fixed': '3.3000',
                        'commission_percent': '0.0000',
                        'is_enabled': False,
                        'order_type_id': 'extra_super_order_type3',
                    },
                ],
                'commission_for_driver_fix_percent': '5.5555',
                'commission_for_subvention_percent': '3.3333',
                'commission_for_workshift_percent': '4.4444',
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'NewName',
                'type': 'park',
            },
            {
                'park_id': 'extra_super_park_id',
                'id': 'extra_super_work_rule_id',
                'idempotency_token': None,
                'commission_for_driver_fix_percent': decimal.Decimal('5.5555'),
                'commission_for_subvention_percent': decimal.Decimal('3.3333'),
                'commission_for_workshift_percent': decimal.Decimal('4.4444'),
                'is_archived': False,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_default': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'NewName',
                'type': 'park',
            },
            {
                'extra_super_order_type1': {
                    'Fix': 1.2000,
                    'IsEnabled': True,
                    'Percent': 3.4000,
                },
                'extra_super_order_type2': {
                    'Fix': 1.1100,
                    'IsEnabled': False,
                    'Percent': 2.2220,
                },
                'extra_super_order_type3': {
                    'Fix': 3.3000,
                    'IsEnabled': False,
                    'Percent': 0.0,
                },
            },
            {'counts': 8},
            '{"CommisisonForSubventionPercent":'
            '{"current":"3.3333","old":"3.2100"},'
            '"CommissionForDriverFixPercent":'
            '{"current":"5.5555","old":"12.3456"},'
            '"Name":{"current":"NewName","old":"Name"},'
            '"WorkshiftCommissionPercent":{"current":"4.4444","old":"1.2300"},'
            '"extra_super_name2":{"current":"1.1100","old":"1.2000"},'
            '"extra_super_name2 (%)":{"current":"2.2220","old":"3.4000"},'
            '"extra_super_name2 (Вкл)":{"current":"False","old":"True"},'
            '"":{"current":"3.3000","old":"0.0000"}}',
        ),
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': defaults.PARK_SELFREG_RULE_ID},
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_YANDEX_TEAM_AUTHOR_IDENTITY,
            ),
            {
                'calc_table': [
                    {
                        'commission_fixed': '1.11',
                        'order_type_id': 'extra_super_order_type1',
                    },
                    {'order_type_id': 'extra_super_order_type3'},
                ],
                'commission_for_workshift_percent': '4.4444',
                'is_workshift_enabled': True,
                'name': 'NewName',
                'type': 'invalid_type',  # field will be ignored
                'subtype': 'invalid_subtype',  # field will be ignored
            },
            {
                'id': '656cbf2ed4e7406fa78ec2107ec9fefe',
                'calc_table': [
                    {
                        'order_type_id': 'extra_super_order_type1',
                        'order_type_name': 'extra_super_name1',
                        'is_enabled': True,
                        'commission_fixed': '1.1100',
                        'commission_percent': '3.4000',
                    },
                    {
                        'order_type_id': 'extra_super_order_type2',
                        'order_type_name': 'extra_super_name2',
                        'is_enabled': False,
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                    },
                    {
                        'order_type_id': 'extra_super_order_type3',
                        'is_enabled': False,
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                    },
                ],
                'commission_for_driver_fix_percent': '12.3456',
                'commission_for_subvention_percent': '3.2100',
                'commission_for_workshift_percent': '4.4444',
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'NewName',
                'subtype': 'selfreg',
                'type': 'park',
            },
            {
                'park_id': 'extra_super_park_id',
                'id': '656cbf2ed4e7406fa78ec2107ec9fefe',
                'idempotency_token': None,
                'commission_for_driver_fix_percent': decimal.Decimal(
                    '12.3456',
                ),
                'commission_for_subvention_percent': decimal.Decimal('3.2100'),
                'commission_for_workshift_percent': decimal.Decimal('4.4444'),
                'is_archived': False,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_default': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'NewName',
                'type': 'park',
            },
            {
                'extra_super_order_type1': {
                    'Fix': 1.1100,
                    'IsEnabled': True,
                    'Percent': 3.4000,
                },
                'extra_super_order_type3': {
                    'Fix': 0.0,
                    'IsEnabled': False,
                    'Percent': 0.0,
                },
            },
            {'counts': 3},
            '{"Name":{"current":"NewName","old":"Name"},'
            '"WorkshiftCommissionPercent":{"current":"4.4444","old":"1.2300"},'
            '"extra_super_name1":{"current":"1.1100","old":"1.2000"}}',
        ),
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': 'extra_super_work_rule_id'},
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_SCRIPT_AUTHOR_IDENTITY,
            ),
            {
                'commission_for_subvention_percent': '3.33333',
                'commission_for_workshift_percent': '4.4444',
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'NewName',
            },
            {
                'id': 'extra_super_work_rule_id',
                'calc_table': [
                    {
                        'order_type_id': 'extra_super_order_type1',
                        'order_type_name': 'extra_super_name1',
                        'is_enabled': True,
                        'commission_fixed': '1.2000',
                        'commission_percent': '3.4000',
                    },
                    {
                        'order_type_id': 'extra_super_order_type2',
                        'order_type_name': 'extra_super_name2',
                        'is_enabled': True,
                        'commission_fixed': '1.2000',
                        'commission_percent': '3.4000',
                    },
                    {
                        'order_type_id': 'extra_super_order_type3',
                        'is_enabled': False,
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                    },
                ],
                'commission_for_driver_fix_percent': '12.3456',
                'commission_for_subvention_percent': '3.3333',
                'commission_for_workshift_percent': '4.4444',
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'NewName',
                'type': 'park',
            },
            {
                'park_id': 'extra_super_park_id',
                'id': 'extra_super_work_rule_id',
                'idempotency_token': None,
                'commission_for_driver_fix_percent': decimal.Decimal(
                    '12.3456',
                ),
                'commission_for_subvention_percent': decimal.Decimal('3.3333'),
                'commission_for_workshift_percent': decimal.Decimal('4.4444'),
                'is_archived': False,
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_default': False,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'NewName',
                'type': 'park',
            },
            {
                'extra_super_order_type1': {
                    'Fix': 1.2000,
                    'IsEnabled': True,
                    'Percent': 3.4000,
                },
                'extra_super_order_type2': {
                    'Fix': 1.2000,
                    'IsEnabled': True,
                    'Percent': 3.400,
                },
            },
            {'counts': 3},
            '{"CommisisonForSubventionPercent":'
            '{"current":"3.3333","old":"3.2100"},'
            '"Name":{"current":"NewName","old":"Name"},'
            '"WorkshiftCommissionPercent":'
            '{"current":"4.4444","old":"1.2300"}}',
        ),
        (
            utils.modify_base_dict(
                defaults.PARAMS, {'id': 'extra_super_work_rule_id'},
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_JOB_AUTHOR_IDENTITY,
            ),
            {
                'calc_table': [
                    {
                        'commission_fixed': '1.11',
                        'commission_percent': '2.222',
                        'order_type_id': 'extra_super_order_type2',
                        'is_enabled': False,
                    },
                ],
            },
            {
                'id': 'extra_super_work_rule_id',
                'calc_table': [
                    {
                        'order_type_id': 'extra_super_order_type1',
                        'order_type_name': 'extra_super_name1',
                        'is_enabled': True,
                        'commission_fixed': '1.2000',
                        'commission_percent': '3.4000',
                    },
                    {
                        'order_type_id': 'extra_super_order_type2',
                        'order_type_name': 'extra_super_name2',
                        'is_enabled': False,
                        'commission_fixed': '1.1100',
                        'commission_percent': '2.2220',
                    },
                    {
                        'order_type_id': 'extra_super_order_type3',
                        'is_enabled': False,
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                    },
                ],
                'commission_for_driver_fix_percent': '12.3456',
                'commission_for_subvention_percent': '3.2100',
                'commission_for_workshift_percent': '1.2300',
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_driver_fix_enabled': False,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'is_workshift_enabled': True,
                'name': 'Name',
                'type': 'park',
            },
            {
                'park_id': 'extra_super_park_id',
                'id': 'extra_super_work_rule_id',
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
            {
                'extra_super_order_type1': {
                    'Fix': 1.2000,
                    'IsEnabled': True,
                    'Percent': 3.4000,
                },
                'extra_super_order_type2': {
                    'Fix': 1.1100,
                    'IsEnabled': False,
                    'Percent': 2.2220,
                },
            },
            {'counts': 3},
            '{"extra_super_name2":{"current":"1.1100","old":"1.2000"},'
            '"extra_super_name2 (%)":{"current":"2.2220","old":"3.4000"},'
            '"extra_super_name2 (Вкл)":{"current":"False","old":"True"}}',
        ),
    ],
)
async def test_ok(
        taxi_driver_work_rules,
        mock_dispatcher_access_control,
        fleet_parks_shard,
        redis_store,
        pgsql,
        params,
        request_author,
        request_work_rule,
        expected_response,
        expected_pg_work_rule,
        expected_redis_calc_table,
        log_info_counts,
        expected_changelog_entry,
):
    rule_id = params['id']

    old_pg_work_rule = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, rule_id,
    )
    old_created_at = old_pg_work_rule['created_at']
    old_updated_at = old_pg_work_rule['updated_at']

    request_body = utils.modify_base_dict(
        {'author': request_author}, {'work_rule': request_work_rule},
    )
    response = await taxi_driver_work_rules.patch(
        ENDPOINT, params=params, headers=defaults.HEADERS, json=request_body,
    )

    # response
    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), expected_response, ['calc_table'],
    )

    # pg work rule entry
    pg_work_rule = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, rule_id,
    )
    assert old_created_at == pg_work_rule['created_at']
    assert old_updated_at <= pg_work_rule['updated_at']
    pg_work_rule.pop('created_at')
    pg_work_rule.pop('updated_at')
    assert pg_work_rule == expected_pg_work_rule

    # redis calc table
    real_redis_calc_table_value = redis_store.hgetall(
        utils.build_calc_table_redis_key(defaults.PARK_ID, rule_id),
    )
    current_redis_calc_table_value = {
        key.decode('ascii'): json.loads(value)
        for key, value in real_redis_calc_table_value.items()
    }
    assert current_redis_calc_table_value == expected_redis_calc_table

    # pg changelog entry
    log_info = utils.modify_base_dict(defaults.LOG_INFO, log_info_counts)
    author_type = request_author['identity']['type']
    if author_type == 'passport_yandex_team':
        log_info = utils.modify_base_dict(
            log_info, {'user_id': '', 'user_name': 'Tech support'},
        )
    elif author_type in ('script', 'job'):
        log_info = utils.modify_base_dict(
            log_info, {'user_id': '', 'user_name': 'platform', 'ip': ''},
        )
    changelog.check_work_rule_changes(
        pgsql, log_info, expected_changelog_entry,
    )
