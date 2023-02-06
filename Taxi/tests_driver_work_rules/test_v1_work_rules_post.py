import datetime
import json

import pytest
import pytz

from tests_driver_work_rules import changelog
from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils


ENDPOINT = 'v1/work-rules'


@pytest.mark.parametrize(
    'params, headers, tested_fields, error_code, expected_response',
    [
        (
            defaults.PARAMS,
            utils.modify_base_dict(
                defaults.HEADERS, {'X-Idempotency-Token': None},
            ),
            None,
            400,
            {
                'code': '400',
                'message': 'Missing X-Idempotency-Token in header',
            },
        ),
        (
            defaults.PARAMS,
            utils.modify_base_dict(
                defaults.HEADERS, {'X-Idempotency-Token': ''},
            ),
            None,
            400,
            {
                'code': '400',
                'message': (
                    'Value of header \'x_idempotency_token\': '
                    'incorrect size, must be 1 (limit) <= 0 (value)'
                ),
            },
        ),
        (
            defaults.PARAMS,
            defaults.HEADERS,
            {'subtype': 'selfreg', 'type': 'commercial_hiring'},
            400,
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
            defaults.HEADERS,
            {'subtype': 'uber_integration', 'type': 'commercial_hiring'},
            400,
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
            defaults.HEADERS,
            {'subtype': 'selfreg', 'type': 'commercial_hiring_with_car'},
            400,
            {
                'code': '400',
                'message': (
                    'Type \'commercial_hiring_with_car\' '
                    'must contain only \'default\' subtype'
                ),
            },
        ),
        (
            defaults.PARAMS,
            defaults.HEADERS,
            {
                'subtype': 'uber_integration',
                'type': 'commercial_hiring_with_car',
            },
            400,
            {
                'code': '400',
                'message': (
                    'Type \'commercial_hiring_with_car\' '
                    'must contain only \'default\' subtype'
                ),
            },
        ),
        (
            defaults.PARAMS,
            defaults.HEADERS,
            {'commission_for_subvention_percent': '3.abcd'},
            400,
            {
                'code': '400',
                'message': (
                    'Field \'work_rule.commission_for_subvention_percent\' '
                    'must be able to convert from string to decimal'
                ),
            },
        ),
        (
            defaults.PARAMS,
            defaults.HEADERS,
            {'commission_for_workshift_percent': '#.1234'},
            400,
            {
                'code': '400',
                'message': (
                    'Field \'work_rule.commission_for_workshift_percent\' '
                    'must be able to convert from string to decimal'
                ),
            },
        ),
        (
            defaults.PARAMS,
            defaults.HEADERS,
            {'commission_for_subvention_percent': '1,234'},
            400,
            {
                'code': '400',
                'message': (
                    'Field \'work_rule.commission_for_subvention_percent\' '
                    'must be able to convert from string to decimal'
                ),
            },
        ),
        (
            defaults.PARAMS,
            defaults.HEADERS,
            {'commission_for_subvention_percent': '123.4567'},
            400,
            {
                'code': '400',
                'message': (
                    'Value of '
                    '\'work_rule.commission_for_subvention_percent\' '
                    'must be between 0 and 100'
                ),
            },
        ),
    ],
)
async def test_creating_work_rule_bad_request(
        taxi_driver_work_rules,
        params,
        headers,
        tested_fields,
        error_code,
        expected_response,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {
            'work_rule': utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE, tested_fields,
            ),
        },
    )
    response = await taxi_driver_work_rules.post(
        ENDPOINT, params=params, headers=headers, json=request_body,
    )
    assert response.status_code == error_code
    assert response.json() == expected_response


@pytest.mark.parametrize(
    'params, headers, tested_fields, error_code',
    [
        (None, defaults.HEADERS, None, 400),
        (defaults.PARAMS, defaults.HEADERS, {'type': 'invalid_type'}, 400),
        (defaults.PARAMS, defaults.HEADERS, {'is_enabled': None}, 400),
    ],
)
async def test_creating_work_rule_bad_request_codegen(
        taxi_driver_work_rules, params, headers, tested_fields, error_code,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {
            'work_rule': utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE, tested_fields,
            ),
        },
    )
    response = await taxi_driver_work_rules.post(
        ENDPOINT, params=params, headers=headers, json=request_body,
    )
    assert response.status_code == error_code
    assert response.json()['code'] == '400'


@pytest.mark.config(
    PARKS_MODIFICATIONS_WITH_ABSENT_USER_NAME={
        'enabled': False,
        'log_default_name': '--',
    },
)
async def test_internal_error(taxi_driver_work_rules):
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=defaults.BASE_REQUEST_BODY,
    )
    assert response.status_code == 500


@pytest.mark.parametrize(
    'tested_fields',
    [
        {
            'calc_table': [
                {
                    'commission_fixed': '1.2000',
                    'commission_percent': '3.4000',
                    'is_enabled': True,
                },
            ],
        },
        {'calc_table': [{'order_type_id': '', 'is_enabled': True}]},
        {'calc_table': [{'order_type_id': 'q' * 101, 'is_enabled': True}]},
        {
            'calc_table': [
                defaults.BASE_CALC_TABLE_ENTRY,
                {'order_type_id': 'extra_super_order_type2'},
            ],
        },
        {'calc_table': [defaults.BASE_CALC_TABLE_ENTRY]},
    ],
)
async def test_creating_calc_table_bad_request(
        taxi_driver_work_rules, tested_fields,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {
            'work_rule': utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE, tested_fields,
            ),
        },
    )
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=request_body,
    )
    assert response.status_code == 400
    assert response.json()['code'] == '400'


def build_pg_entry_with_type(work_rule_type):
    return (
        '{{"CommisisonForSubventionPercent":{{"current":"3.2100","old":""}},'
        '"CommissionForDriverFixPercent":{{"current":"12.3456","old":""}},'
        '"DisableDynamicYandexCommission":{{"current":"False","old":""}},'
        '"Enable":{{"current":"True","old":""}},'
        '"IsDriverFixEnabled":{{"current":"False","old":""}},'
        '"Name":{{"current":"Name","old":""}},'
        '"Type":{{"current":"{0}","old":""}},'
        '"WorkshiftCommissionPercent":{{"current":"1.2300","old":""}},'
        '"WorkshiftsEnabled":{{"current":"True","old":""}},'
        '"YandexDisableNullComission":{{"current":"False","old":""}},'
        '"YandexDisablePayUserCancelOrder":{{"current":"False","old":""}}}}'
    ).format(str(work_rule_type))


@pytest.mark.parametrize(
    'request_author, request_work_rule, default_id,'
    'expected_pg_work_rule, expected_changelog_entry',
    [
        (
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_YANDEX_AUTHOR_IDENTITY,
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {'subtype': 'default', 'type': 'park'},
            ),
            defaults.PARK_DEFAULT_RULE_ID,
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
                    'type': 'park',
                },
            ),
            build_pg_entry_with_type(0),
        ),
        (
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_YANDEX_TEAM_AUTHOR_IDENTITY,
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {'subtype': 'selfreg', 'type': 'park'},
            ),
            defaults.PARK_SELFREG_RULE_ID,
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
                    'type': 'park',
                },
            ),
            build_pg_entry_with_type(0),
        ),
        (
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_SCRIPT_AUTHOR_IDENTITY,
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {'subtype': 'uber_integration', 'type': 'park'},
            ),
            defaults.UBER_INTEGRATION_RULE_ID,
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
                    'type': 'park',
                },
            ),
            build_pg_entry_with_type(0),
        ),
        (
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_YANDEX_AUTHOR_IDENTITY,
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {'subtype': 'default', 'type': 'commercial_hiring'},
            ),
            defaults.COMMERCIAL_HIRING_RULE_ID,
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
                    'type': 'commercial_hiring',
                },
            ),
            build_pg_entry_with_type(1),
        ),
        (
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_YANDEX_TEAM_AUTHOR_IDENTITY,
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {'subtype': 'default', 'type': 'commercial_hiring_with_car'},
            ),
            defaults.COMMERCIAL_HIRING_WITH_CAR_RULE_ID,
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
                    'type': 'commercial_hiring_with_car',
                },
            ),
            build_pg_entry_with_type(2),
        ),
        (
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_SCRIPT_AUTHOR_IDENTITY,
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE, {'type': 'park'},
            ),
            None,
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
                    'type': 'park',
                },
            ),
            build_pg_entry_with_type(0),
        ),
        (
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_JOB_AUTHOR_IDENTITY,
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE, {'type': 'commercial_hiring'},
            ),
            None,
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
                    'type': 'commercial_hiring',
                },
            ),
            build_pg_entry_with_type(1),
        ),
        (
            utils.modify_base_dict(
                defaults.BASE_REQUEST_AUTHOR,
                defaults.BASE_YANDEX_TEAM_AUTHOR_IDENTITY,
            ),
            utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE,
                {'type': 'commercial_hiring_with_car'},
            ),
            None,
            utils.modify_base_dict(
                defaults.BASE_PG_WORK_RULE,
                {
                    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
                    'type': 'commercial_hiring_with_car',
                },
            ),
            build_pg_entry_with_type(2),
        ),
    ],
)
async def test_creating_work_rule_ok(
        taxi_driver_work_rules,
        mock_dispatcher_access_control,
        fleet_parks_shard,
        redis_store,
        pgsql,
        request_author,
        request_work_rule,
        default_id,
        expected_pg_work_rule,
        expected_changelog_entry,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {'author': request_author, 'work_rule': request_work_rule},
    )
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=request_body,
    )

    # response
    assert response.status_code == 200
    response_rule = response.json()
    response_rule_id = response_rule['id']
    response_rule.pop('id')
    if default_id is not None:
        assert response_rule_id == default_id
    assert request_body['work_rule'] == response_rule

    # pg work rule entry
    pg_work_rule = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, response_rule_id,
    )
    assert pg_work_rule['created_at'] == pg_work_rule['updated_at']
    pg_work_rule.pop('created_at')
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    assert now > pg_work_rule['updated_at']
    pg_work_rule.pop('updated_at')
    if default_id is not None:
        assert pg_work_rule['id'] == default_id
    pg_work_rule.pop('id')
    assert pg_work_rule == expected_pg_work_rule

    # pg changelog entry
    log_info = utils.modify_base_dict(defaults.LOG_INFO, {'counts': 11})
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


DEFAULT_NEW_PG_WORK_RULE_FIELDS = (
    '"CommisisonForSubventionPercent":{"current":"3.2100","old":""},'
    '"CommissionForDriverFixPercent":{"current":"12.3456","old":""},'
    '"DisableDynamicYandexCommission":{"current":"False","old":""},'
    '"Enable":{"current":"True","old":""},'
    '"IsDriverFixEnabled":{"current":"False","old":""},'
    '"Name":{"current":"Name","old":""},'
    '"Type":{"current":"1","old":""},'
    '"WorkshiftCommissionPercent":{"current":"1.2300","old":""},'
    '"WorkshiftsEnabled":{"current":"True","old":""},'
    '"YandexDisableNullComission":{"current":"False","old":""},'
    '"YandexDisablePayUserCancelOrder":{"current":"False","old":""},'
)


@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:' + defaults.PARK_ID,
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
    'tested_fields, expected_redis_calc_table, log_info_counts,'
    'expected_changelog_entry',
    [
        (
            {'calc_table': [defaults.BASE_CALC_TABLE_ENTRY]},
            {'extra_super_order_type1': defaults.BASE_REDIS_CALC_TABLE_ENTRY},
            14,
            '{'
            + DEFAULT_NEW_PG_WORK_RULE_FIELDS
            + '"extra_super_name1":{"current":"1.2000","old":""},'
            '"extra_super_name1 (%)":{"current":"3.4000","old":""},'
            '"extra_super_name1 (Вкл)":{"current":"True","old":""}}',
        ),
        (
            {
                'calc_table': [
                    {
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                        'order_type_id': 'extra_super_order_type1',
                        'is_enabled': False,
                    },
                    {
                        'commission_fixed': '0.0000',
                        'commission_percent': '0.0000',
                        'order_type_id': 'extra_super_order_type2',
                        'is_enabled': True,
                    },
                ],
            },
            {
                'extra_super_order_type1': {
                    'Fix': 0.0,
                    'IsEnabled': False,
                    'Percent': 0.0,
                },
                'extra_super_order_type2': {
                    'Fix': 0.0,
                    'IsEnabled': True,
                    'Percent': 0.0,
                },
            },
            17,
            '{'
            + DEFAULT_NEW_PG_WORK_RULE_FIELDS
            + '"extra_super_name1":{"current":"0.0000","old":""},'
            '"extra_super_name1 (%)":{"current":"0.0000","old":""},'
            '"extra_super_name1 (Вкл)":{"current":"False","old":""},'
            '"extra_super_name2":{"current":"0.0000","old":""},'
            '"extra_super_name2 (%)":{"current":"0.0000","old":""},'
            '"extra_super_name2 (Вкл)":{"current":"True","old":""}}',
        ),
        (
            {
                'calc_table': [
                    defaults.BASE_CALC_TABLE_ENTRY,
                    {
                        'commission_fixed': '1.1000',
                        'commission_percent': '2.2200',
                        'order_type_id': 'extra_super_order_type3',
                        'is_enabled': False,
                    },
                ],
            },
            {
                'extra_super_order_type1': (
                    defaults.BASE_REDIS_CALC_TABLE_ENTRY
                ),
                'extra_super_order_type3': {
                    'Fix': 1.1000,
                    'IsEnabled': False,
                    'Percent': 2.2200,
                },
            },
            17,
            '{'
            + DEFAULT_NEW_PG_WORK_RULE_FIELDS
            + '"extra_super_name1":{"current":"1.2000","old":""},'
            '"extra_super_name1 (%)":{"current":"3.4000","old":""},'
            '"extra_super_name1 (Вкл)":{"current":"True","old":""},'
            '"": {"old": "", "current": "1.1000"},'
            '" (%)": {"old": "", "current": "2.2200"},'
            '" (Вкл)": {"old": "", "current": "False"}}',
        ),
    ],
)
async def test_creating_calc_table_ok(
        taxi_driver_work_rules,
        mock_dispatcher_access_control,
        fleet_parks_shard,
        redis_store,
        pgsql,
        tested_fields,
        expected_redis_calc_table,
        log_info_counts,
        expected_changelog_entry,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {
            'work_rule': utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE, tested_fields,
            ),
        },
    )
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=request_body,
    )

    assert response.status_code == 200

    response_rule = response.json()
    response_rule_id = response_rule['id']
    response_rule.pop('id')
    assert request_body['work_rule'] == response_rule

    assert (
        utils.get_redis_calc_table(
            redis_store, defaults.PARK_ID, response_rule_id,
        )
        == expected_redis_calc_table
    )

    log_info = utils.modify_base_dict(
        defaults.LOG_INFO, {'counts': log_info_counts},
    )
    changelog.check_work_rule_changes(
        pgsql, log_info, expected_changelog_entry,
    )


REQUEST_FOR_CREATING = {
    'author': {
        'consumer': 'extra_super_consumer',
        'identity': {
            'type': 'passport_user',
            'user_ip': '1.2.3.4',
            'passport_uid': '1',
        },
    },
    'work_rule': {
        'commission_for_subvention_percent': '1.1111',
        'commission_for_workshift_percent': '1.1111',
        'commission_for_driver_fix_percent': '1.1111',
        'is_commission_for_orders_cancelled_by_client_enabled': True,
        'is_commission_if_platform_commission_is_null_enabled': True,
        'is_driver_fix_enabled': False,
        'is_dynamic_platform_commission_enabled': True,
        'is_enabled': True,
        'is_workshift_enabled': True,
        'name': 'Name',
        'type': 'park',
        'subtype': 'default',
    },
}


@pytest.mark.pgsql(
    'driver-work-rules',
    queries=[
        defaults.WORK_RULE_INSERT_QUERY.format(
            defaults.PARK_ID,
            defaults.PARK_DEFAULT_RULE_ID,
            'extra_super_idempotency_token1',
        ),
    ],
)
@pytest.mark.parametrize(
    'idempotency_token',
    ['extra_super_idempotency_token1', 'extra_super_idempotency_token2'],
)
async def test_pkey_conflict(
        taxi_driver_work_rules,
        mock_dispatcher_access_control,
        fleet_parks_shard,
        pgsql,
        redis_store,
        idempotency_token,
):
    work_rule_id = defaults.PARK_DEFAULT_RULE_ID
    old_pg_work_rule = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, work_rule_id,
    )

    headers = {
        'X-Idempotency-Token': idempotency_token,
        'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET,
    }
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=headers,
        json=REQUEST_FOR_CREATING,
    )

    assert response.status_code == 200
    expected_response = utils.modify_base_dict(
        REQUEST_FOR_CREATING['work_rule'],
        {'id': defaults.PARK_DEFAULT_RULE_ID},
    )
    assert response.json() == expected_response

    pg_work_rule = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, work_rule_id,
    )
    assert pg_work_rule == old_pg_work_rule

    redis_work_rule = utils.get_redis_all_park_work_rules(
        redis_store, defaults.PARK_ID,
    )
    assert redis_work_rule == {}


# test for unique index (park_id, idempotency_token)
async def test_unique_index_conflict(
        taxi_driver_work_rules,
        mock_dispatcher_access_control,
        fleet_parks_shard,
        pgsql,
):
    expected_response = utils.modify_base_dict(
        defaults.BASE_RESPONSE_WORK_RULE,
        {
            'commission_for_subvention_percent': '3.2100',
            'commission_for_workshift_percent': '1.2300',
            'commission_for_driver_fix_percent': '12.3456',
            'is_enabled': True,
            'is_workshift_enabled': True,
            'name': 'Name',
            'type': 'commercial_hiring',
        },
    )
    expected_pg_work_rule = utils.modify_base_dict(
        defaults.BASE_PG_WORK_RULE,
        {
            'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
            'type': 'commercial_hiring',
        },
    )

    # first request
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=defaults.BASE_REQUEST_BODY,
    )

    # first response
    assert response.status_code == 200
    response_body = response.json()
    work_rule_id = response_body['id']
    response_body.pop('id')
    assert response_body == expected_response

    # first pg work rule
    pg_work_rule = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, work_rule_id,
    )

    pg_work_rule_id = pg_work_rule['id']
    pg_work_rule.pop('id')
    assert pg_work_rule_id == work_rule_id

    created_at = pg_work_rule['created_at']
    pg_work_rule.pop('created_at')
    updated_at = pg_work_rule['updated_at']
    pg_work_rule.pop('updated_at')
    assert created_at == updated_at

    assert pg_work_rule == expected_pg_work_rule

    # second request
    response2 = await taxi_driver_work_rules.post(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=defaults.BASE_REQUEST_BODY,
    )

    # second response
    assert response2.status_code == 200
    response_body2 = response2.json()
    work_rule_id2 = response_body2['id']
    response_body2.pop('id')
    assert response_body2 == expected_response

    # second pg work rule
    pg_work_rule2 = utils.get_postgres_work_rule(
        pgsql, defaults.PARK_ID, work_rule_id,
    )

    pg_work_rule_id2 = pg_work_rule2['id']
    pg_work_rule2.pop('id')
    assert pg_work_rule_id2 == work_rule_id2
    assert work_rule_id2 == work_rule_id

    created_at2 = pg_work_rule2['created_at']
    pg_work_rule2.pop('created_at')
    updated_at2 = pg_work_rule2['updated_at']
    pg_work_rule2.pop('updated_at')
    assert created_at == created_at2
    assert updated_at == updated_at2

    assert pg_work_rule2 == expected_pg_work_rule


@pytest.mark.redis_store(
    [
        'hmset',
        utils.build_calc_table_redis_key(
            defaults.PARK_ID, defaults.COMMERCIAL_HIRING_RULE_ID,
        ),
        {
            'extra_super_order_type1': json.dumps(
                {'Fix': 9.9, 'IsEnabled': True, 'Percent': 8.8},
            ),
            'extra_super_order_type10': json.dumps({'IsEnabled': True}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'RuleType:Items:' + defaults.PARK_ID,
        {
            'extra_super_order_type1': json.dumps(
                {'Name': 'extra_super_name1'},
            ),
            'extra_super_order_type2': json.dumps(
                {'Name': 'extra_super_name2'},
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'tested_fields, expected_redis_calc_table, expected_changelog_entry',
    [
        (
            {
                'calc_table': [defaults.BASE_CALC_TABLE_ENTRY],
                'subtype': 'default',
            },
            {'extra_super_order_type1': defaults.BASE_REDIS_CALC_TABLE_ENTRY},
            '{'
            + DEFAULT_NEW_PG_WORK_RULE_FIELDS
            + '"extra_super_name1":{"current":"1.2000","old":""},'
            '"extra_super_name1 (%)":{"current":"3.4000","old":""},'
            '"extra_super_name1 (Вкл)":{"current":"True","old":""}}',
        ),
    ],
)
async def test_double_calc_table_entry_creation(
        taxi_driver_work_rules,
        mock_dispatcher_access_control,
        fleet_parks_shard,
        redis_store,
        pgsql,
        tested_fields,
        expected_redis_calc_table,
        expected_changelog_entry,
):
    request_body = utils.modify_base_dict(
        defaults.BASE_REQUEST_BODY,
        {
            'work_rule': utils.modify_base_dict(
                defaults.BASE_REQUEST_WORK_RULE, tested_fields,
            ),
        },
    )
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=request_body,
    )
    assert response.status_code == 200
    response_rule = response.json()
    response_rule_id = response_rule['id']
    response_rule.pop('id')
    assert request_body['work_rule'] == response_rule

    assert (
        utils.get_redis_calc_table(
            redis_store, defaults.PARK_ID, response_rule_id,
        )
        == expected_redis_calc_table
    )

    log_info = utils.modify_base_dict(defaults.LOG_INFO, {'counts': 14})
    changelog.check_work_rule_changes(
        pgsql, log_info, expected_changelog_entry,
    )
