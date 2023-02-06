import copy
import json
import typing

import pytest

from tests_driver_work_rules import defaults

ENDPOINT = '/fleet/dwr/v1/cards/driver/work-rules/list'

HEADERS = {
    'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET,
    'X-Ya-User-Ticket': 'user_ticket',
    'X-Ya-User-Ticket-Provider': 'yandex',
    'X-Yandex-Login': 'abacaba',
    'X-Yandex-UID': '123',
    'X-Park-Id': 'extra_super_park_id',
}

PROVIDER_YA = 'yandex'
PROVIDER_YA_T = 'yandex_team'

PGQUERY1 = """
    INSERT INTO driver_work_rules.work_rules (
        park_id, id, idempotency_token, commission_for_driver_fix_percent, 
        commission_for_subvention_percent, 
        commission_for_workshift_percent, 
        is_commission_if_platform_commission_is_null_enabled, 
        is_commission_for_orders_cancelled_by_client_enabled, 
        is_driver_fix_enabled, is_dynamic_platform_commission_enabled, 
        is_enabled, is_workshift_enabled, 
        name, type, created_at, updated_at, 
        is_archived, is_default
    ) 
    VALUES 
    (
        'extra_super_park_id', '551dbceed3fc40faa90532307dceffe8', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, 'ddd', 'vezet', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361', 
        false, false
    ), 
    (
        'extra_super_park_id', 'e26a3cf21acfe01198d50030487e046b', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, 'bbb', 'park', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361', 
        true, false
    ), 
    (
        'extra_super_park_id', '9dd42b2db67c4e088df6eb35d6270e58', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '{0}', 'commercial_hiring', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361',
        false, false
    ), 
    (
        'extra_super_park_id', '656cbf2ed4e7406fa78ec2107ec9fefe', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, 'ccc', 'park', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361', 
        false, false
    ), 
    (
        'extra_super_park_id', '3485aa955a484ecc8ce5c6704a52e0af', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, 'eee', 'vezet', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361', 
        false, false
    ), 
    (
        'extra_super_park_id', 'badd1c9d6b6b4e9fb9e0b48367850467', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '{1}', 'commercial_hiring_with_car', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361',
        false, false
    ),    
    (
        'extra_super_park_id', 'work_rule_1', 
        NULL, 12.3456, 3.21, 1.23, true, true, 
        false, true, true, true, 'aaa', 'park', 
        '2019-02-14 11:48:33.644361', '2020-02-14 11:48:33.644361',
        false, true
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
        name, type, created_at, updated_at,
        is_archived, is_default
    ) 
    VALUES 
    (
        'extra_super_park_id2', '3485aa955a484ecc8ce5c6704a52e0af', 
        NULL, 0.0, 0.0, 0.0, true, true, false, 
        true, false, false, '', 'vezet', '2019-02-14 11:48:33.644361', 
        '2020-02-14 11:48:33.644361',
        false, false
    );

"""  # noqa: W291

RESPONSE_ALL = {
    'items': [
        {
            'id': 'work_rule_1',
            'name': 'aaa',
            'is_enabled': True,
            'type': 'park',
            'is_default': True,
        },
        {
            'id': '9dd42b2db67c4e088df6eb35d6270e58',
            'name': ('abcde' * 100)[:500],
            'is_enabled': False,
            'type': 'commercial_hiring',
            'is_default': False,
        },
        {
            'id': '656cbf2ed4e7406fa78ec2107ec9fefe',
            'name': 'ccc',
            'is_enabled': False,
            'type': 'park',
            'is_default': False,
        },
        {
            'id': '551dbceed3fc40faa90532307dceffe8',
            'name': 'ddd',
            'is_enabled': False,
            'type': 'vezet',
            'is_default': False,
        },
        {
            'id': '3485aa955a484ecc8ce5c6704a52e0af',
            'name': 'eee',
            'is_enabled': False,
            'type': 'vezet',
            'is_default': False,
        },
        {
            'id': 'badd1c9d6b6b4e9fb9e0b48367850467',
            'name': ('too_long_name' * 100)[:500],
            'is_enabled': False,
            'type': 'commercial_hiring_with_car',
            'is_default': False,
        },
    ],
}
RESPONSE_BY_TYPE_PARK = {
    'items': [
        {
            'id': 'work_rule_1',
            'is_enabled': True,
            'name': 'aaa',
            'type': 'park',
            'is_default': True,
        },
        {
            'id': '656cbf2ed4e7406fa78ec2107ec9fefe',
            'is_enabled': False,
            'name': 'ccc',
            'type': 'park',
            'is_default': False,
        },
    ],
}
RESPONSE_BY_COMPATIBLE_ID = {
    'items': [
        {
            'id': '551dbceed3fc40faa90532307dceffe8',
            'name': 'ddd',
            'is_enabled': False,
            'type': 'vezet',
            'is_default': False,
        },
        {
            'id': '3485aa955a484ecc8ce5c6704a52e0af',
            'name': 'eee',
            'is_enabled': False,
            'type': 'vezet',
            'is_default': False,
        },
    ],
}
RESPONSE_EMPTY: typing.Dict = {'items': []}
RESPONSE_ALL_WITH_USED_RULE_ID = copy.deepcopy(RESPONSE_ALL)
RESPONSE_ALL_WITH_USED_RULE_ID['items'].insert(
    2,
    {
        'id': 'e26a3cf21acfe01198d50030487e046b',
        'is_enabled': False,
        'name': 'bbb',
        'type': 'park',
        'is_default': False,
    },
)


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
    'park_id,provider_type,request_params,status_code,expected_response',
    [
        ('extra_super_park_id', PROVIDER_YA, {}, 200, RESPONSE_BY_TYPE_PARK),
        (
            'extra_super_park_id',
            PROVIDER_YA,
            {'compatible_with_id': ''},
            200,
            RESPONSE_BY_TYPE_PARK,
        ),
        (
            'extra_super_park_id',
            PROVIDER_YA,
            {'compatible_with_id': '551dbceed3fc40faa90532307dceffe8'},
            200,
            RESPONSE_BY_COMPATIBLE_ID,
        ),
        ('extra_super_park_id', PROVIDER_YA_T, {}, 200, RESPONSE_ALL),
        (
            'extra_super_park_id',
            PROVIDER_YA_T,
            {'compatible_with_id': ''},
            200,
            RESPONSE_ALL,
        ),
        (
            'extra_super_park_id',
            PROVIDER_YA_T,
            {'compatible_with_id': 'work_rule_1'},
            200,
            RESPONSE_ALL,
        ),
        ('extra_super_park_id3', PROVIDER_YA, {}, 200, RESPONSE_EMPTY),
        ('extra_super_park_id3', PROVIDER_YA_T, {}, 200, RESPONSE_EMPTY),
        (
            'extra_super_park_id3',
            PROVIDER_YA,
            {'compatible_with_id': 'work_rule_1'},
            200,
            RESPONSE_EMPTY,
        ),
        (
            'extra_super_park_id3',
            PROVIDER_YA_T,
            {'compatible_with_id': 'work_rule_1'},
            200,
            RESPONSE_EMPTY,
        ),
        (
            'extra_super_park_id',
            PROVIDER_YA,
            {'compatible_with_id': 'compatible_with_strange'},
            200,
            RESPONSE_BY_TYPE_PARK,
        ),
        (
            'extra_super_park_id',
            PROVIDER_YA_T,
            {'compatible_with_id': 'compatible_with_strange'},
            200,
            RESPONSE_ALL,
        ),
        (
            'extra_super_park_id',
            PROVIDER_YA_T,
            {'compatible_with_id': 'e26a3cf21acfe01198d50030487e046b'},
            200,
            RESPONSE_ALL_WITH_USED_RULE_ID,
        ),
    ],
)
async def test_generate(
        taxi_driver_work_rules,
        park_id,
        provider_type,
        request_params,
        status_code,
        expected_response,
):
    HEADERS['X-Park-Id'] = park_id
    HEADERS['X-Ya-User-Ticket-Provider'] = provider_type
    response = await taxi_driver_work_rules.get(
        ENDPOINT, headers=HEADERS, params=request_params,
    )

    assert response.status_code == status_code
    if response.status_code == 200:
        assert response.json() == expected_response
