import datetime
import decimal
import json

import pytest
import pytz

from tests_driver_work_rules import changelog
from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils

ENDPOINT = 'fleet/driver-work-rules/v1/work-rules'


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

BASE_WORK_RULE_REQUEST = {
    'is_commission_if_platform_commission_is_null_enabled': False,
    'is_commission_for_orders_cancelled_by_client_enabled': False,
    'is_dynamic_platform_commission_enabled': False,
    'is_enabled': False,
    'name': 'Name1',
}

BASE_WORK_RULE_RESPONSE = utils.modify_base_dict(
    BASE_WORK_RULE_REQUEST,
    {'type': 'park', 'is_default': False, 'is_archived': False},
)

BASE_PG_WORK_RULE = {
    'park_id': 'park_id1',
    'idempotency_token': defaults.IDEMPOTENCY_TOKEN,
    'commission_for_driver_fix_percent': decimal.Decimal('0.0000'),
    'commission_for_subvention_percent': decimal.Decimal('0.0000'),
    'commission_for_workshift_percent': decimal.Decimal('0.0000'),
    'is_archived': False,
    'is_commission_if_platform_commission_is_null_enabled': False,
    'is_commission_for_orders_cancelled_by_client_enabled': False,
    'is_default': False,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': False,
    'is_enabled': False,
    'is_workshift_enabled': False,
    'name': 'Name1',
    'type': 'park',
}

BASE_CALC_TABLE_ENTRY = {
    'order_type_id': 'order_type_id1',
    'is_enabled': True,
    'commission_fixed': '123.0100',
    'commission_percent': '1.1000',
}

BASE_REDIS_CALC_TABLE = {
    'order_type_id1': {'Fix': 123.01, 'Percent': 1.1, 'IsEnabled': True},
}

BASE_PG_CHANGE_LOG_ENTRY = {
    'CommisisonForSubventionPercent': {'current': '0.0000', 'old': ''},
    'CommissionForDriverFixPercent': {'current': '0.0000', 'old': ''},
    'DisableDynamicYandexCommission': {'current': 'True', 'old': ''},
    'Enable': {'current': 'False', 'old': ''},
    'OrderType1 (Вкл)': {'old': '', 'current': 'True'},
    'OrderType1 (%)': {'old': '', 'current': '1.1000'},
    'OrderType1': {'old': '', 'current': '123.0100'},
    'IsDriverFixEnabled': {'current': 'False', 'old': ''},
    'Name': {'current': 'Name1', 'old': ''},
    'Type': {'current': '0', 'old': ''},
    'WorkshiftCommissionPercent': {'current': '0.0000', 'old': ''},
    'WorkshiftsEnabled': {'current': 'False', 'old': ''},
    'YandexDisableNullComission': {'current': 'True', 'old': ''},
    'YandexDisablePayUserCancelOrder': {'current': 'True', 'old': ''},
}

LOG_INFO = {
    'park_id': 'park_id1',
    'user_id': 'user1',
    'user_name': '--',
    'counts': 0,
    'ip': '',
}

TEST_OK_PARAMS = [
    (
        'park_id1',
        BASE_PARK,
        {'copy_rule_id': 'copy_rule_id_type_park'},
        BASE_WORK_RULE_REQUEST,
        BASE_CALC_TABLE_ENTRY,
        BASE_WORK_RULE_RESPONSE,
        BASE_PG_WORK_RULE,
        BASE_REDIS_CALC_TABLE,
        BASE_PG_CHANGE_LOG_ENTRY,
    ),
    (
        'park_id1',
        BASE_PARK,
        {'copy_rule_id': 'copy_rule_id_type_commercial_hiring'},
        {
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': True,
            'name': 'Name2',
        },
        utils.modify_base_dict(
            BASE_CALC_TABLE_ENTRY, {'commission_percent': '2.3000'},
        ),
        utils.modify_base_dict(
            BASE_WORK_RULE_RESPONSE,
            {
                'type': 'commercial_hiring',
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'name': 'Name2',
            },
        ),
        utils.modify_base_dict(
            BASE_PG_WORK_RULE,
            {
                'type': 'commercial_hiring',
                'is_commission_if_platform_commission_is_null_enabled': True,
                'is_commission_for_orders_cancelled_by_client_enabled': True,
                'is_dynamic_platform_commission_enabled': True,
                'is_enabled': True,
                'name': 'Name2',
            },
        ),
        {'order_type_id1': {'Fix': 123.01, 'Percent': 2.3, 'IsEnabled': True}},
        utils.modify_base_dict(
            BASE_PG_CHANGE_LOG_ENTRY,
            {
                'Type': {'current': '1', 'old': ''},
                'OrderType1 (%)': {'current': '2.3000', 'old': ''},
                'YandexDisableNullComission': {'current': 'False', 'old': ''},
                'YandexDisablePayUserCancelOrder': {
                    'current': 'False',
                    'old': '',
                },
                'DisableDynamicYandexCommission': {
                    'current': 'False',
                    'old': '',
                },
                'Enable': {'current': 'True', 'old': ''},
                'Name': {'current': 'Name2', 'old': ''},
            },
        ),
    ),
    (
        'park_id_driver_fix_enabled',
        utils.modify_base_dict(
            BASE_PARK,
            {
                'id': 'park_id_driver_fix_enabled',
                'is_workshift_enabled': True,
                'country_id': 'rus',
            },
        ),
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {
                'commission_for_subvention_percent': '0',
                'commission_for_driver_fix_percent': '0',
                'commission_for_workshift_percent': '14.5',
                'is_workshift_enabled': True,
                'is_driver_fix_enabled': True,
            },
        ),
        BASE_CALC_TABLE_ENTRY,
        utils.modify_base_dict(
            BASE_WORK_RULE_RESPONSE,
            {
                'commission_for_subvention_percent': '0',
                'commission_for_driver_fix_percent': '0',
                'commission_for_workshift_percent': '14.5',
                'is_workshift_enabled': True,
                'is_driver_fix_enabled': True,
            },
        ),
        utils.modify_base_dict(
            BASE_PG_WORK_RULE,
            {
                'park_id': 'park_id_driver_fix_enabled',
                'commission_for_subvention_percent': decimal.Decimal('0.0000'),
                'commission_for_driver_fix_percent': decimal.Decimal('0.0000'),
                'commission_for_workshift_percent': decimal.Decimal('14.5000'),
                'is_workshift_enabled': True,
                'is_driver_fix_enabled': True,
            },
        ),
        BASE_REDIS_CALC_TABLE,
        utils.modify_base_dict(
            BASE_PG_CHANGE_LOG_ENTRY,
            {
                'CommisisonForSubventionPercent': {
                    'current': '0.0000',
                    'old': '',
                },
                'CommissionForDriverFixPercent': {
                    'current': '0.0000',
                    'old': '',
                },
                'WorkshiftCommissionPercent': {
                    'current': '14.5000',
                    'old': '',
                },
                'WorkshiftsEnabled': {'current': 'True', 'old': ''},
                'IsDriverFixEnabled': {'current': 'True', 'old': ''},
            },
        ),
    ),
    (
        'park_id_driver_fix_enabled',
        utils.modify_base_dict(
            BASE_PARK,
            {
                'id': 'park_id_driver_fix_enabled',
                'is_workshift_enabled': True,
                'country_id': 'rus',
            },
        ),
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {
                'commission_for_subvention_percent': '5',
                'commission_for_driver_fix_percent': '100',
                'commission_for_workshift_percent': '44.4',
                'is_workshift_enabled': True,
                'is_driver_fix_enabled': True,
            },
        ),
        BASE_CALC_TABLE_ENTRY,
        utils.modify_base_dict(
            BASE_WORK_RULE_RESPONSE,
            {
                'commission_for_subvention_percent': '5',
                'commission_for_driver_fix_percent': '100',
                'commission_for_workshift_percent': '44.4',
                'is_workshift_enabled': True,
                'is_driver_fix_enabled': True,
            },
        ),
        utils.modify_base_dict(
            BASE_PG_WORK_RULE,
            {
                'park_id': 'park_id_driver_fix_enabled',
                'commission_for_subvention_percent': decimal.Decimal('5.0000'),
                'commission_for_driver_fix_percent': decimal.Decimal(
                    '100.0000',
                ),
                'commission_for_workshift_percent': decimal.Decimal('44.4000'),
                'is_workshift_enabled': True,
                'is_driver_fix_enabled': True,
            },
        ),
        BASE_REDIS_CALC_TABLE,
        utils.modify_base_dict(
            BASE_PG_CHANGE_LOG_ENTRY,
            {
                'CommisisonForSubventionPercent': {
                    'current': '5.0000',
                    'old': '',
                },
                'CommissionForDriverFixPercent': {
                    'current': '100.0000',
                    'old': '',
                },
                'WorkshiftCommissionPercent': {
                    'current': '44.4000',
                    'old': '',
                },
                'WorkshiftsEnabled': {'current': 'True', 'old': ''},
                'IsDriverFixEnabled': {'current': 'True', 'old': ''},
            },
        ),
    ),
]


@pytest.mark.redis_store(file='redis')
@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.parametrize(
    'park_id,park,params,work_rule,calc_table_entry,'
    'expected_work_rule_response,expected_pg_work_rule,'
    'expected_redis_calc_table,expected_change_log',
    TEST_OK_PARAMS,
)
async def test_ok(
        taxi_driver_work_rules,
        mock_fleet_parks_list,
        fleet_parks_shard,
        redis_store,
        pgsql,
        park_id,
        park,
        params,
        work_rule,
        calc_table_entry,
        expected_work_rule_response,
        expected_pg_work_rule,
        expected_redis_calc_table,
        expected_change_log,
):
    mock_fleet_parks_list.set_parks([park])

    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS, {'X-Park-Id': park_id},
        ),
        params=params,
        json={'work_rule': work_rule, 'calc_table': [calc_table_entry]},
    )
    assert response.status_code == 200

    response_body = response.json()
    response_rule_id = response_body.pop('id')
    assert response_body['work_rule'] == expected_work_rule_response
    assert response_body['calc_table'] == [calc_table_entry]

    # calc table
    assert (
        utils.get_redis_calc_table(redis_store, park_id, response_rule_id)
        == expected_redis_calc_table
    )

    # pg work rule entry
    pg_work_rule = utils.get_postgres_work_rule(
        pgsql, park_id, response_rule_id,
    )
    assert pg_work_rule['created_at'] == pg_work_rule['updated_at']
    pg_work_rule.pop('created_at')
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Moscow'))
    assert now > pg_work_rule['updated_at']
    pg_work_rule.pop('updated_at')
    pg_work_rule.pop('id')
    assert pg_work_rule == expected_pg_work_rule

    # pg changelog entry
    log_info = utils.modify_base_dict(
        LOG_INFO, {'park_id': park_id, 'counts': 14},
    )
    changelog.check_work_rule_changes(
        pgsql, log_info, json.dumps(expected_change_log),
    )


TEST_IDEMPOTENCY_PARAMS = [
    (
        'existing_idempotency_token',
        'already_existing_rule_id',
        {
            'work_rule': utils.modify_base_dict(
                BASE_WORK_RULE_RESPONSE, {'name': 'ExistingRule'},
            ),
            'calc_table': [BASE_CALC_TABLE_ENTRY],
        },
    ),
    (
        'new_idempotency_token',
        None,
        {
            'work_rule': BASE_WORK_RULE_RESPONSE,
            'calc_table': [BASE_CALC_TABLE_ENTRY],
        },
    ),
]


def _get_work_rules_cnt(pgsql):
    return len(
        utils.select_by_query(
            pgsql, 'SELECT * FROM driver_work_rules.work_rules',
        ),
    )


@pytest.mark.redis_store(file='redis')
@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.parametrize(
    'idempotency_token,expected_old_rule_id,expected_response',
    TEST_IDEMPOTENCY_PARAMS,
)
async def test_idempotency(
        taxi_driver_work_rules,
        mock_fleet_parks_list,
        pgsql,
        redis_store,
        fleet_parks_shard,
        idempotency_token,
        expected_old_rule_id,
        expected_response,
):
    mock_fleet_parks_list.set_parks([BASE_PARK])

    before_cnt = _get_work_rules_cnt(pgsql)

    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS,
            {
                'X-Park-Id': 'park_id1',
                'X-Idempotency-Token': idempotency_token,
            },
        ),
        json={
            'work_rule': BASE_WORK_RULE_REQUEST,
            'calc_table': [BASE_CALC_TABLE_ENTRY],
        },
    )
    assert response.status_code == 200
    response_body = response.json()
    rule_id = response_body.pop('id')
    assert response_body == expected_response

    after_cnt = _get_work_rules_cnt(pgsql)

    if expected_old_rule_id is not None:
        assert rule_id == expected_old_rule_id
        assert before_cnt == after_cnt
    else:
        assert before_cnt + 1 == after_cnt


TEST_4XX_PARAMS = [
    (
        'not_existing_park_id1',
        BASE_PARK,
        {},
        BASE_WORK_RULE_REQUEST,
        BASE_CALC_TABLE_ENTRY,
        404,
        {
            'code': 'not_found',
            'message': 'Park with id `not_existing_park_id1` not found',
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {'copy_rule_id': 'not_existing_rule_id'},
        BASE_WORK_RULE_REQUEST,
        BASE_CALC_TABLE_ENTRY,
        404,
        {
            'code': 'not_found',
            'message': 'Rule with id `not_existing_rule_id` not found',
        },
    ),
    (
        'park_id1',
        utils.modify_base_dict(
            BASE_PARK, {'country_id': 'not_existing_country'},
        ),
        {},
        BASE_WORK_RULE_REQUEST,
        BASE_CALC_TABLE_ENTRY,
        404,
        {
            'code': 'not_found',
            'message': 'Country with id `not_existing_country` not found',
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {'commission_for_driver_fix_percent': 'not_decimal'},
        ),
        BASE_CALC_TABLE_ENTRY,
        400,
        {
            'code': 'parse_error',
            'message': (
                'Field \'work_rule.commission_for_driver_fix_percent\' '
                'must be able to convert from string to decimal'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {'commission_for_subvention_percent': 'not_decimal'},
        ),
        BASE_CALC_TABLE_ENTRY,
        400,
        {
            'code': 'parse_error',
            'message': (
                'Field \'work_rule.commission_for_subvention_percent\' '
                'must be able to convert from string to decimal'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {'commission_for_workshift_percent': 'not_decimal'},
        ),
        BASE_CALC_TABLE_ENTRY,
        400,
        {
            'code': 'parse_error',
            'message': (
                'Field \'work_rule.commission_for_workshift_percent\' '
                'must be able to convert from string to decimal'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        BASE_WORK_RULE_REQUEST,
        utils.modify_base_dict(
            BASE_CALC_TABLE_ENTRY, {'commission_percent': 'not_double'},
        ),
        400,
        {
            'code': 'parse_error',
            'message': (
                'Field \'calc_table.commission_percent\' must be able to'
                ' convert from string to double'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        BASE_WORK_RULE_REQUEST,
        utils.modify_base_dict(
            BASE_CALC_TABLE_ENTRY, {'commission_fixed': 'not_double'},
        ),
        400,
        {
            'code': 'parse_error',
            'message': (
                'Field \'calc_table.commission_fixed\' must be able to '
                'convert from string to double'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        utils.modify_base_dict(BASE_WORK_RULE_REQUEST, {'name': ''}),
        BASE_CALC_TABLE_ENTRY,
        400,
        {
            'code': 'empty_work_rule_name',
            'message': 'Rule name can not be empty.',
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        BASE_WORK_RULE_REQUEST,
        utils.modify_base_dict(
            BASE_CALC_TABLE_ENTRY, {'order_type_id': 'not_existing'},
        ),
        409,
        {
            'code': 'not_existing_order_type_id',
            'message': 'Park has no order type with id `not_existing`',
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST, {'is_workshift_enabled': True},
        ),
        BASE_CALC_TABLE_ENTRY,
        409,
        {
            'code': 'commission_not_allowed',
            'message': 'Workshift commission not allowed in park',
        },
    ),
    (
        'park_id1',
        utils.modify_base_dict(BASE_PARK, {'is_workshift_enabled': True}),
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {
                'is_workshift_enabled': True,
                'commission_for_workshift_percent': '-1',
            },
        ),
        BASE_CALC_TABLE_ENTRY,
        409,
        {
            'code': 'commission_out_of_range',
            'message': (
                'Field `work_rule.commission_for_workshift_percent` '
                'is invalid, its value(-1) must be in the range [14.5 .. 44.4]'
            ),
        },
    ),
    (
        'park_id1',
        utils.modify_base_dict(BASE_PARK, {'is_workshift_enabled': True}),
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {
                'is_workshift_enabled': True,
                'commission_for_workshift_percent': '44.46',
            },
        ),
        BASE_CALC_TABLE_ENTRY,
        409,
        {
            'code': 'commission_out_of_range',
            'message': (
                'Field `work_rule.commission_for_workshift_percent` is invalid'
                ', its value(44.46) must be in the range [14.5 .. 44.4]'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST, {'is_driver_fix_enabled': True},
        ),
        BASE_CALC_TABLE_ENTRY,
        409,
        {
            'code': 'commission_not_allowed',
            'message': 'Driver fix commission not allowed in park',
        },
    ),
    (
        'park_id_driver_fix_enabled',
        utils.modify_base_dict(
            BASE_PARK, {'id': 'park_id_driver_fix_enabled'},
        ),
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {
                'is_driver_fix_enabled': True,
                'commission_for_driver_fix_percent': '-1',
            },
        ),
        BASE_CALC_TABLE_ENTRY,
        409,
        {
            'code': 'commission_out_of_range',
            'message': (
                'Field `work_rule.commission_for_driver_fix_percent` '
                'is invalid, its value(-1) must be in the range [0 .. 100]'
            ),
        },
    ),
    (
        'park_id_driver_fix_enabled',
        utils.modify_base_dict(
            BASE_PARK, {'id': 'park_id_driver_fix_enabled'},
        ),
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {
                'is_driver_fix_enabled': True,
                'commission_for_driver_fix_percent': '101',
            },
        ),
        BASE_CALC_TABLE_ENTRY,
        409,
        {
            'code': 'commission_out_of_range',
            'message': (
                'Field `work_rule.commission_for_driver_fix_percent` '
                'is invalid, its value(101) must be in the range [0 .. 100]'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {'commission_for_subvention_percent': '1.0'},
        ),
        BASE_CALC_TABLE_ENTRY,
        409,
        {
            'code': 'commission_not_allowed',
            'message': 'Subvention commission not allowed in park',
        },
    ),
    (
        'park_id1',
        utils.modify_base_dict(BASE_PARK, {'country_id': 'rus'}),
        {},
        utils.modify_base_dict(
            BASE_WORK_RULE_REQUEST,
            {'commission_for_subvention_percent': '10'},
        ),
        BASE_CALC_TABLE_ENTRY,
        409,
        {
            'code': 'commission_out_of_range',
            'message': (
                'Field `work_rule.commission_for_subvention_percent` '
                'is invalid, its value(10) must be in the range [0 .. 5]'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        BASE_WORK_RULE_REQUEST,
        utils.modify_base_dict(
            BASE_CALC_TABLE_ENTRY, {'commission_percent': '0.1'},
        ),
        409,
        {
            'code': 'commission_out_of_range',
            'message': (
                'Field `calc_table[id=order_type_id1].commission_percent` '
                'is invalid, its value(0.1) must be in the range [0.5 .. 1.2]'
            ),
        },
    ),
    (
        'park_id1',
        BASE_PARK,
        {},
        BASE_WORK_RULE_REQUEST,
        utils.modify_base_dict(
            BASE_CALC_TABLE_ENTRY, {'commission_percent': '1.3'},
        ),
        409,
        {
            'code': 'commission_out_of_range',
            'message': (
                'Field `calc_table[id=order_type_id1].commission_percent` '
                'is invalid, its value(1.3) must be in the range [0.5 .. 1.2]'
            ),
        },
    ),
]


@pytest.mark.redis_store(file='redis')
@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.parametrize(
    'park_id,park,params,work_rule,calc_table_entry,expected_status_code,'
    'expected_response',
    TEST_4XX_PARAMS,
)
async def test_4xx(
        taxi_driver_work_rules,
        mock_fleet_parks_list,
        park,
        park_id,
        params,
        work_rule,
        calc_table_entry,
        expected_status_code,
        expected_response,
):
    mock_fleet_parks_list.set_parks([park])

    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS, {'X-Park-Id': park_id},
        ),
        params=params,
        json={'work_rule': work_rule, 'calc_table': [calc_table_entry]},
    )
    assert response.status_code == expected_status_code
    assert response.json() == expected_response


TEST_VEZET_PARAMS = [
    (
        'yandex',
        '',
        403,
        {'code': 'no_permissions', 'message': 'No permissions'},
    ),
    (
        'yandex_team',
        '',
        403,
        {'code': 'no_permissions', 'message': 'No permissions'},
    ),
    (
        'yandex_team',
        'work_rules_type_ne_vezet',
        403,
        {'code': 'no_permissions', 'message': 'No permissions'},
    ),
    (
        'yandex_team',
        'work_rules_type_ne_vezet,work_rules_type_vezet,work_rules_type_vezet_inogda',  # noqa: E501
        200,
        {
            'work_rule': utils.modify_base_dict(
                BASE_WORK_RULE_RESPONSE, {'type': 'vezet'},
            ),
            'calc_table': [BASE_CALC_TABLE_ENTRY],
        },
    ),
]


@pytest.mark.redis_store(file='redis')
@pytest.mark.pgsql('driver-work-rules', files=['work_rules_vezet.sql'])
@pytest.mark.parametrize(
    (
        'user_provider',
        'permissions',
        'expected_status_code',
        'expected_response',
    ),
    TEST_VEZET_PARAMS,
)
async def test_vezet(
        taxi_driver_work_rules,
        mock_fleet_parks_list,
        fleet_parks_shard,
        redis_store,
        pgsql,
        user_provider,
        permissions,
        expected_status_code,
        expected_response,
):
    mock_fleet_parks_list.set_parks([BASE_PARK])

    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS,
            {
                'X-Park-Id': 'park_id1',
                'X-Ya-User-Ticket-Provider': user_provider,
                'X-YaTaxi-Fleet-Permissions': permissions,
            },
        ),
        params={'copy_rule_id': 'copy_rule_id_type_park'},
        json={
            'work_rule': BASE_WORK_RULE_REQUEST,
            'calc_table': [BASE_CALC_TABLE_ENTRY],
        },
    )
    assert response.status_code == expected_status_code

    response_body = response.json()
    if expected_status_code == 200:
        response_body.pop('id')
    assert response_body == expected_response
