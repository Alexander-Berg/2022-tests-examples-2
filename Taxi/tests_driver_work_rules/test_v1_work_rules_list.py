# encoding=utf-8
import json

import pytest

from testsuite.utils import ordered_object

from tests_driver_work_rules import defaults


ENDPOINT = 'v1/work-rules/list'
ENDPOINT_MASTER = 'v1/work-rules/list-from-master'


HEADERS = {'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET}


@pytest.mark.parametrize(
    'request_body',
    [
        ({}),
        ({'query': {'park': {'id': ''}}},),
        (
            {
                'query': {
                    'park': {'id': defaults.PARK_ID, 'work_rule': {'ids': []}},
                },
            },
        ),
    ],
)
async def test_bad_request(taxi_driver_work_rules, request_body):
    response = await taxi_driver_work_rules.post(
        ENDPOINT, headers=HEADERS, json=request_body,
    )

    assert response.status_code == 400
    assert response.json()['code'] == '400'


ALL_WORK_RULES = {
    'work_rules': [
        {
            'commission_for_driver_fix_percent': '12.3456',
            'commission_for_subvention_percent': '3.2100',
            'commission_for_workshift_percent': '1.2300',
            'id': 'work_rule_1',
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_driver_fix_enabled': False,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': True,
            'is_workshift_enabled': True,
            'name': 'Name',
            'type': 'park',
        },
        {
            'commission_for_driver_fix_percent': '0.0000',
            'commission_for_subvention_percent': '0.0000',
            'commission_for_workshift_percent': '0.0000',
            'id': defaults.COMMERCIAL_HIRING_RULE_ID,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_driver_fix_enabled': False,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': False,
            'is_workshift_enabled': False,
            'name': defaults.MAXIMUM_LENGTH_NAME,
            'subtype': 'default',
            'type': 'commercial_hiring',
        },
        {
            'commission_for_driver_fix_percent': '0.0000',
            'commission_for_subvention_percent': '0.0000',
            'commission_for_workshift_percent': '0.0000',
            'id': defaults.COMMERCIAL_HIRING_WITH_CAR_RULE_ID,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_driver_fix_enabled': False,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': False,
            'is_workshift_enabled': False,
            'name': defaults.TRUNCATED_TOO_LONG_NAME,
            'subtype': 'default',
            'type': 'commercial_hiring_with_car',
        },
        {
            'commission_for_driver_fix_percent': '0.0000',
            'commission_for_subvention_percent': '0.0000',
            'commission_for_workshift_percent': '0.0000',
            'id': defaults.PARK_DEFAULT_RULE_ID,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_driver_fix_enabled': False,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': False,
            'is_workshift_enabled': False,
            'name': '',
            'subtype': 'default',
            'type': 'park',
        },
        {
            'commission_for_driver_fix_percent': '0.0000',
            'commission_for_subvention_percent': '0.0000',
            'commission_for_workshift_percent': '0.0000',
            'id': defaults.PARK_SELFREG_RULE_ID,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_driver_fix_enabled': False,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': False,
            'is_workshift_enabled': False,
            'name': '',
            'subtype': 'selfreg',
            'type': 'park',
        },
        {
            'commission_for_driver_fix_percent': '0.0000',
            'commission_for_subvention_percent': '0.0000',
            'commission_for_workshift_percent': '0.0000',
            'id': defaults.UBER_INTEGRATION_RULE_ID,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_driver_fix_enabled': False,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': False,
            'is_workshift_enabled': False,
            'name': '',
            'subtype': 'uber_integration',
            'type': 'park',
        },
        {
            'commission_for_driver_fix_percent': '0.0000',
            'commission_for_subvention_percent': '0.0000',
            'commission_for_workshift_percent': '0.0000',
            'id': defaults.VEZET_RULE_ID,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': False,
            'is_driver_fix_enabled': False,
            'is_workshift_enabled': False,
            'name': '',
            'subtype': 'default',
            'type': 'vezet',
        },
    ],
}


def build_request_body(
        park_id,
        rule_ids=None,
        is_enabled=None,
        is_dynamic_platform_commission_enabled=None,
):
    park = {'id': park_id}
    work_rule = {}

    if rule_ids is not None:
        work_rule['ids'] = rule_ids
    if is_enabled is not None:
        work_rule['is_enabled'] = is_enabled
    if is_dynamic_platform_commission_enabled is not None:
        work_rule[
            'is_dynamic_platform_commission_enabled'
        ] = is_dynamic_platform_commission_enabled

    if bool(work_rule):
        park['work_rule'] = work_rule

    return {'query': {'park': park}}


def build_expected_response(fields):
    work_rule = defaults.BASE_RESPONSE_WORK_RULE.copy()
    work_rule.update(fields)
    return {'work_rules': [work_rule]}


@pytest.mark.pgsql('driver-work-rules', files=['test_ok.sql'])
@pytest.mark.redis_store(
    [
        'hmset',
        defaults.RULE_WORK_ITEMS_PREFIX + defaults.PARK_ID,
        {
            'work_rule_1': json.dumps(defaults.BASE_REDIS_RULE),
            defaults.PARK_DEFAULT_RULE_ID: json.dumps({}),
            defaults.PARK_SELFREG_RULE_ID: json.dumps({}),
            defaults.UBER_INTEGRATION_RULE_ID: json.dumps({}),
            defaults.VEZET_RULE_ID: json.dumps({}),
            defaults.COMMERCIAL_HIRING_RULE_ID: json.dumps(
                {'Name': defaults.MAXIMUM_LENGTH_NAME},
            ),
            defaults.COMMERCIAL_HIRING_WITH_CAR_RULE_ID: json.dumps(
                {'Name': defaults.TOO_LONG_NAME},
            ),
        },
    ],
    [
        'hmset',
        'RuleWork:Items:extra_super_park_id2',
        {defaults.VEZET_RULE_ID: json.dumps({})},
    ],
)
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (build_request_body('unknown_park_id'), {'work_rules': []}),
        (build_request_body(defaults.PARK_ID), ALL_WORK_RULES),
        (
            build_request_body(
                defaults.PARK_ID, [defaults.PARK_DEFAULT_RULE_ID],
            ),
            build_expected_response(
                {
                    'id': defaults.PARK_DEFAULT_RULE_ID,
                    'subtype': 'default',
                    'type': 'park',
                },
            ),
        ),
        (
            build_request_body(
                defaults.PARK_ID, [defaults.PARK_SELFREG_RULE_ID],
            ),
            build_expected_response(
                {
                    'id': defaults.PARK_SELFREG_RULE_ID,
                    'subtype': 'selfreg',
                    'type': 'park',
                },
            ),
        ),
        (
            build_request_body(
                defaults.PARK_ID, [defaults.UBER_INTEGRATION_RULE_ID],
            ),
            build_expected_response(
                {
                    'id': defaults.UBER_INTEGRATION_RULE_ID,
                    'subtype': 'uber_integration',
                    'type': 'park',
                },
            ),
        ),
        (
            build_request_body(
                defaults.PARK_ID, [defaults.COMMERCIAL_HIRING_RULE_ID],
            ),
            build_expected_response(
                {
                    'id': defaults.COMMERCIAL_HIRING_RULE_ID,
                    'subtype': 'default',
                    'type': 'commercial_hiring',
                    'name': defaults.MAXIMUM_LENGTH_NAME,
                },
            ),
        ),
        (
            build_request_body(
                defaults.PARK_ID,
                [defaults.COMMERCIAL_HIRING_WITH_CAR_RULE_ID],
            ),
            build_expected_response(
                {
                    'id': defaults.COMMERCIAL_HIRING_WITH_CAR_RULE_ID,
                    'subtype': 'default',
                    'type': 'commercial_hiring_with_car',
                    'name': defaults.TRUNCATED_TOO_LONG_NAME,
                },
            ),
        ),
        (
            build_request_body(defaults.PARK_ID, [defaults.VEZET_RULE_ID]),
            build_expected_response(
                {
                    'id': defaults.VEZET_RULE_ID,
                    'subtype': 'default',
                    'type': 'vezet',
                },
            ),
        ),
        (
            build_request_body(
                defaults.PARK_ID, ['work_rule_1', 'work_rule_4'],
            ),
            {
                'work_rules': [
                    {
                        'commission_for_driver_fix_percent': '12.3456',
                        'is_commission_for_orders_cancelled_by_client_'
                        'enabled': True,
                        'is_driver_fix_enabled': False,
                        'is_dynamic_platform_commission_enabled': True,
                        'is_commission_if_platform_commission_is_null_'
                        'enabled': True,
                        'id': 'work_rule_1',
                        'is_enabled': True,
                        'name': 'Name',
                        'commission_for_subvention_percent': '3.2100',
                        'type': 'park',
                        'commission_for_workshift_percent': '1.2300',
                        'is_workshift_enabled': True,
                    },
                ],
            },
        ),
        (
            build_request_body('extra_super_park_id2', None),
            {
                'work_rules': [
                    {
                        'id': defaults.VEZET_RULE_ID,
                        'commission_for_driver_fix_percent': '0.0000',
                        'commission_for_subvention_percent': '0.0000',
                        'commission_for_workshift_percent': '0.0000',
                        'is_commission_if_platform_commission_is_null_'
                        'enabled': True,
                        'is_commission_for_orders_cancelled_by_client_'
                        'enabled': True,
                        'is_driver_fix_enabled': False,
                        'is_dynamic_platform_commission_enabled': True,
                        'is_enabled': False,
                        'is_workshift_enabled': False,
                        'name': '',
                        'subtype': 'default',
                        'type': 'vezet',
                    },
                ],
            },
        ),
    ],
)
async def test_ok(taxi_driver_work_rules, request_body, expected_response):
    response = await taxi_driver_work_rules.post(
        ENDPOINT, headers=HEADERS, json=request_body,
    )

    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), expected_response, ['work_rules'],
    )


WORK_RULE_1 = {
    'id': 'work_rule_1',
    'commission_for_driver_fix_percent': '0.0000',
    'commission_for_subvention_percent': '0.0000',
    'commission_for_workshift_percent': '0.0000',
    'is_commission_if_platform_commission_is_null_enabled': True,
    'is_commission_for_orders_cancelled_by_client_enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': False,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': '',
    'type': 'park',
}

WORK_RULE_2 = {
    'id': 'work_rule_2',
    'commission_for_driver_fix_percent': '0.0000',
    'commission_for_subvention_percent': '0.0000',
    'commission_for_workshift_percent': '0.0000',
    'is_commission_if_platform_commission_is_null_enabled': True,
    'is_commission_for_orders_cancelled_by_client_enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': False,
    'is_enabled': False,
    'is_workshift_enabled': False,
    'name': '',
    'type': 'park',
}

WORK_RULE_3 = {
    'id': 'work_rule_3',
    'commission_for_driver_fix_percent': '0.0000',
    'commission_for_subvention_percent': '0.0000',
    'commission_for_workshift_percent': '0.0000',
    'is_commission_if_platform_commission_is_null_enabled': True,
    'is_commission_for_orders_cancelled_by_client_enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': True,
    'is_workshift_enabled': False,
    'name': '',
    'type': 'park',
}

WORK_RULE_4 = {
    'id': 'work_rule_4',
    'commission_for_driver_fix_percent': '0.0000',
    'commission_for_subvention_percent': '0.0000',
    'commission_for_workshift_percent': '0.0000',
    'is_commission_if_platform_commission_is_null_enabled': True,
    'is_commission_for_orders_cancelled_by_client_enabled': True,
    'is_driver_fix_enabled': False,
    'is_dynamic_platform_commission_enabled': True,
    'is_enabled': False,
    'is_workshift_enabled': False,
    'name': '',
    'type': 'park',
}


@pytest.mark.pgsql(
    'driver-work-rules', files=['test_ok_with_boolean_filters.sql'],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'RuleWork:Items:extra_super_park_id3',
        {
            'work_rule_1': json.dumps(
                # 'is_enabled':True},
                # {'is_dynamic_platform_commission_enabled': False,
                {'Enable': True, 'DisableDynamicYandexCommission': True},
            ),
            'work_rule_2': json.dumps(
                # 'is_enabled':False},
                # {'is_dynamic_platform_commission_enabled': False,
                {'Enable': False, 'DisableDynamicYandexCommission': True},
            ),
            'work_rule_3': json.dumps(
                # 'is_enabled':True},
                # {'is_dynamic_platform_commission_enabled': True,
                {'Enable': True, 'DisableDynamicYandexCommission': False},
            ),
            'work_rule_4': json.dumps(
                # 'is_enabled':False},
                # {'is_dynamic_platform_commission_enabled': True,
                {'Enable': False, 'DisableDynamicYandexCommission': False},
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'ids, is_enabled, is_dynamic_platform_commission_enabled,'
    'expected_response',
    [
        (
            None,
            None,
            None,
            {
                'work_rules': [
                    WORK_RULE_1,
                    WORK_RULE_2,
                    WORK_RULE_3,
                    WORK_RULE_4,
                ],
            },
        ),
        (
            ['work_rule_1', 'work_rule_2'],
            None,
            None,
            {'work_rules': [WORK_RULE_1, WORK_RULE_2]},
        ),
        (None, True, None, {'work_rules': [WORK_RULE_1, WORK_RULE_3]}),
        (None, None, True, {'work_rules': [WORK_RULE_3, WORK_RULE_4]}),
        (
            ['work_rule_1', 'work_rule_2', 'work_rule_3'],
            False,
            None,
            {'work_rules': [WORK_RULE_2]},
        ),
        (
            ['work_rule_1', 'work_rule_2', 'work_rule_3'],
            None,
            False,
            {'work_rules': [WORK_RULE_1, WORK_RULE_2]},
        ),
        (None, True, False, {'work_rules': [WORK_RULE_1]}),
        (['work_rule_2', 'work_rule_3'], True, False, {'work_rules': []}),
        (
            ['work_rule_2', 'work_rule_3'],
            False,
            False,
            {'work_rules': [WORK_RULE_2]},
        ),
    ],
)
async def test_ok_with_boolean_filters(
        taxi_driver_work_rules,
        ids,
        is_enabled,
        is_dynamic_platform_commission_enabled,
        expected_response,
):
    request_body = build_request_body(
        'extra_super_park_id3',
        ids,
        is_enabled,
        is_dynamic_platform_commission_enabled,
    )
    response = await taxi_driver_work_rules.post(
        ENDPOINT, headers=HEADERS, json=request_body,
    )

    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(), expected_response, ['work_rules'],
    )


@pytest.mark.pgsql('driver-work-rules', files=['test_ok.sql'])
async def test_from_master(taxi_driver_work_rules, pgsql):
    rule_insert = (
        defaults.WORK_RULE_INSERT_QUERY.format(
            'extra_super_park_id2',
            defaults.PARK_DEFAULT_RULE_ID,
            'extra_super_idempotency_token1',
        ),
    )

    cursor = pgsql['driver-work-rules'].conn.cursor()
    cursor.execute(rule_insert[0])

    request_body = build_request_body('extra_super_park_id2', None)
    response = await taxi_driver_work_rules.post(
        ENDPOINT_MASTER, headers=HEADERS, json=request_body,
    )

    assert response.status_code == 200
    ordered_object.assert_eq(
        response.json(),
        {
            'work_rules': [
                {
                    'id': defaults.VEZET_RULE_ID,
                    'commission_for_driver_fix_percent': '0.0000',
                    'commission_for_subvention_percent': '0.0000',
                    'commission_for_workshift_percent': '0.0000',
                    'is_commission_if_platform_commission_is_null_'
                    'enabled': True,
                    'is_commission_for_orders_cancelled_by_client_'
                    'enabled': True,
                    'is_driver_fix_enabled': False,
                    'is_dynamic_platform_commission_enabled': True,
                    'is_enabled': False,
                    'is_workshift_enabled': False,
                    'name': '',
                    'subtype': 'default',
                    'type': 'vezet',
                },
                {
                    'id': 'e26a3cf21acfe01198d50030487e046b',
                    'commission_for_driver_fix_percent': '3.2100',
                    'commission_for_subvention_percent': '12.3456',
                    'commission_for_workshift_percent': '1.2300',
                    'is_commission_for_orders_cancelled_by_client_enabled': (
                        True
                    ),
                    'is_commission_if_platform_commission_is_null_enabled': (
                        True
                    ),
                    'is_driver_fix_enabled': True,
                    'is_dynamic_platform_commission_enabled': True,
                    'is_enabled': True,
                    'is_workshift_enabled': True,
                    'name': 'Name',
                    'subtype': 'default',
                    'type': 'park',
                },
            ],
        },
        ['work_rules'],
    )
