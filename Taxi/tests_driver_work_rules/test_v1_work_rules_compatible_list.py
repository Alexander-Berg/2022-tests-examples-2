import json
import typing

import pytest

from tests_driver_work_rules import defaults

ENDPOINT = '/v1/work-rules/compatible/list'

HEADERS = {'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET}

PGQUERY1 = """
    INSERT INTO driver_work_rules.work_rules (
        park_id, id, idempotency_token, commission_for_driver_fix_percent, 
        commission_for_subvention_percent, 
        commission_for_workshift_percent, 
        is_commission_if_platform_commission_is_null_enabled, 
        is_commission_for_orders_cancelled_by_client_enabled, 
        is_driver_fix_enabled, is_dynamic_platform_commission_enabled, 
        is_enabled, is_workshift_enabled, 
        name, type, created_at, updated_at, is_archived
    ) 
    VALUES 
    (
        'extra_super_park_id', 'work_rule_archived_type_park', 
        NULL, 12.3456, 3.21, 1.23, true, true, 
        false, true, true, true, 'Name', 'park', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361', true
    ), 
    (
        'extra_super_park_id', 'work_rule_archived_type_vezet', 
        NULL, 12.3456, 3.21, 1.23, true, true, 
        false, true, true, true, 'Name', 'vezet', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361', true
    ), 
    (
        'extra_super_park_id', 'work_rule_archived_compatible_id', 
        NULL, 12.3456, 3.21, 1.23, true, true, 
        false, true, true, true, 'Name', 'vezet', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361', true
    ), 
    (
        'extra_super_park_id', 'work_rule_1', 
        NULL, 12.3456, 3.21, 1.23, true, true, 
        false, true, true, true, 'Name', 'park', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361', false
    ), 
    (
        'extra_super_park_id', 'e26a3cf21acfe01198d50030487e046b', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '', 'park', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361', false
    ), 
    (
        'extra_super_park_id', '656cbf2ed4e7406fa78ec2107ec9fefe', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '', 'park', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361', false
    ), 
    (
        'extra_super_park_id', '551dbceed3fc40faa90532307dceffe8', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '', 'vezet', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361', false
    ), 
    (
        'extra_super_park_id', '3485aa955a484ecc8ce5c6704a52e0af', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '', 'vezet', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361', false
    ), 
    (
        'extra_super_park_id', '9dd42b2db67c4e088df6eb35d6270e58', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '{0}', 'commercial_hiring', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361', false
    ), 
    (
        'extra_super_park_id', 'badd1c9d6b6b4e9fb9e0b48367850467', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '{1}', 'commercial_hiring_with_car', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361', false
    );
"""  # noqa: W291

PGQUERY2 = """
    INSERT INTO driver_work_rules.work_rules (
        park_id, id, idempotency_token, commission_for_driver_fix_percent, 
        commission_for_subvention_percent, 
        commission_for_workshift_percent, 
        is_commission_if_platform_commission_is_null_enabled, 
        is_commission_for_orders_cancelled_by_client_enabled, 
        is_driver_fix_enabled, is_dynamic_platform_commission_enabled, 
        is_enabled, is_workshift_enabled, 
        name, type, created_at, updated_at
    ) 
    VALUES 
    (
        'extra_super_park_id2', '3485aa955a484ecc8ce5c6704a52e0af', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '', 'vezet', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361'
    );
"""  # noqa: W291

RESPONSE_ALL = {
    'work_rules': [
        {
            'id': 'work_rule_1',
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
            'id': 'e26a3cf21acfe01198d50030487e046b',
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
            'subtype': 'default',
            'type': 'park',
        },
        {
            'id': '656cbf2ed4e7406fa78ec2107ec9fefe',
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
            'subtype': 'selfreg',
            'type': 'park',
        },
        {
            'id': '551dbceed3fc40faa90532307dceffe8',
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
            'subtype': 'uber_integration',
            'type': 'vezet',
        },
        {
            'id': '3485aa955a484ecc8ce5c6704a52e0af',
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
            'subtype': 'default',
            'type': 'vezet',
        },
        {
            'id': '9dd42b2db67c4e088df6eb35d6270e58',
            'commission_for_driver_fix_percent': '0.0000',
            'commission_for_subvention_percent': '0.0000',
            'commission_for_workshift_percent': '0.0000',
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_driver_fix_enabled': False,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': False,
            'is_workshift_enabled': False,
            'name': ('abcde' * 100)[:500],
            'subtype': 'default',
            'type': 'commercial_hiring',
        },
        {
            'id': 'badd1c9d6b6b4e9fb9e0b48367850467',
            'commission_for_driver_fix_percent': '0.0000',
            'commission_for_subvention_percent': '0.0000',
            'commission_for_workshift_percent': '0.0000',
            'is_commission_if_platform_commission_is_null_enabled': True,
            'is_commission_for_orders_cancelled_by_client_enabled': True,
            'is_driver_fix_enabled': False,
            'is_dynamic_platform_commission_enabled': True,
            'is_enabled': False,
            'is_workshift_enabled': False,
            'name': ('too_long_name' * 100)[:500],
            'subtype': 'default',
            'type': 'commercial_hiring_with_car',
        },
    ],
}
RESPONSE_BY_TYPE_PARK = {
    'work_rules': [
        {
            'id': 'work_rule_1',
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
            'id': 'e26a3cf21acfe01198d50030487e046b',
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
            'subtype': 'default',
            'type': 'park',
        },
        {
            'id': '656cbf2ed4e7406fa78ec2107ec9fefe',
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
            'subtype': 'selfreg',
            'type': 'park',
        },
    ],
}
RESPONSE_BY_COMPATIBLE_ID = {
    'work_rules': [
        {
            'id': '551dbceed3fc40faa90532307dceffe8',
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
            'subtype': 'uber_integration',
            'type': 'vezet',
        },
        {
            'id': '3485aa955a484ecc8ce5c6704a52e0af',
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
            'subtype': 'default',
            'type': 'vezet',
        },
    ],
}
RESPONSE_BY_ARCHIVED_COMPATIBLE_ID = {
    'work_rules': [
        {
            'id': 'work_rule_archived_compatible_id',
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
            'type': 'vezet',
        },
        {
            'id': '551dbceed3fc40faa90532307dceffe8',
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
            'subtype': 'uber_integration',
            'type': 'vezet',
        },
        {
            'id': '3485aa955a484ecc8ce5c6704a52e0af',
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
            'subtype': 'default',
            'type': 'vezet',
        },
    ],
}
RESPONSE_EMPTY: typing.Dict = {'work_rules': []}


@pytest.mark.pgsql(
    'driver-work-rules',
    queries=[PGQUERY1.format('abcde' * 100, 'too_long_name' * 100), PGQUERY2],
)
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
    'request_params,status_code,expected_response',
    [
        (
            {'park_id': 'extra_super_park_id', 'client_type': 'external'},
            200,
            RESPONSE_BY_TYPE_PARK,
        ),
        (
            {
                'park_id': 'extra_super_park_id',
                'compatible_with_id': '',
                'client_type': 'external',
            },
            200,
            RESPONSE_BY_TYPE_PARK,
        ),
        (
            {
                'park_id': 'extra_super_park_id',
                'compatible_with_id': '551dbceed3fc40faa90532307dceffe8',
                'client_type': 'external',
            },
            200,
            RESPONSE_BY_COMPATIBLE_ID,
        ),
        (
            {
                'park_id': 'extra_super_park_id',
                'compatible_with_id': 'work_rule_archived_compatible_id',
                'client_type': 'external',
            },
            200,
            RESPONSE_BY_ARCHIVED_COMPATIBLE_ID,
        ),
        (
            {'park_id': 'extra_super_park_id', 'client_type': 'internal'},
            200,
            RESPONSE_ALL,
        ),
        (
            {
                'park_id': 'extra_super_park_id',
                'compatible_with_id': '',
                'client_type': 'internal',
            },
            200,
            RESPONSE_ALL,
        ),
        (
            {
                'park_id': 'extra_super_park_id',
                'compatible_with_id': 'work_rule_1',
                'client_type': 'internal',
            },
            200,
            RESPONSE_ALL,
        ),
        (
            {'park_id': 'extra_super_park_id3', 'client_type': 'external'},
            200,
            RESPONSE_EMPTY,
        ),
        (
            {'park_id': 'extra_super_park_id3', 'client_type': 'internal'},
            200,
            RESPONSE_EMPTY,
        ),
        (
            {
                'park_id': 'extra_super_park_id3',
                'compatible_with_id': 'work_rule_1',
                'client_type': 'external',
            },
            200,
            RESPONSE_EMPTY,
        ),
        (
            {
                'park_id': 'extra_super_park_id3',
                'compatible_with_id': 'work_rule_1',
                'client_type': 'internal',
            },
            200,
            RESPONSE_EMPTY,
        ),
        (
            {
                'park_id': 'extra_super_park_id',
                'compatible_with_id': 'compatible_with_strange',
                'client_type': 'external',
            },
            200,
            RESPONSE_BY_TYPE_PARK,
        ),
        (
            {
                'park_id': 'extra_super_park_id',
                'compatible_with_id': 'compatible_with_strange',
                'client_type': 'internal',
            },
            200,
            RESPONSE_ALL,
        ),
    ],
)
async def test_generate(
        taxi_driver_work_rules, request_params, status_code, expected_response,
):
    response = await taxi_driver_work_rules.get(
        ENDPOINT, headers=HEADERS, params=request_params,
    )

    assert response.status_code == status_code
    if response.status_code == 200:
        assert response.json() == expected_response
