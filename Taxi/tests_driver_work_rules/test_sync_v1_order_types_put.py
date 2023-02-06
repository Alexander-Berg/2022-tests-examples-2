import json

import pytest

from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils


ENDPOINT = 'sync/v1/order-types'


BASE_REQUEST_ORDER_TYPE = {
    'id': 'extra_super_order_type1',
    'autocancel_time_in_seconds': 10,
    'driver_cancel_cost': '50.0000',
    'color': 'White',
    'name': 'Name',
    'is_client_address_shown': True,
    'is_client_phone_shown': True,
    'driver_waiting_cost': '50.0000',
    'morning_visibility': {'period': 'м', 'value': 3},
    'night_visibility': {'period': 'скрыть', 'value': 2},
    'weekend_visibility': {'period': '', 'value': 0},
}

BASE_REQUEST_ORDER_TYPE_FOR_PUT = [
    BASE_REQUEST_ORDER_TYPE,
    {
        'id': 'extra_super_order_type2',
        'autocancel_time_in_seconds': 20,
        'driver_cancel_cost': '0.0000',
        'color': '',
        'name': 'Name1',
        'is_client_address_shown': False,
        'is_client_phone_shown': True,
        'driver_waiting_cost': '50.0000',
        'morning_visibility': {'period': 'ч', 'value': 2},
        'night_visibility': {'period': 'скрыть', 'value': 2},
        'weekend_visibility': {'period': 'д', 'value': 2},
    },
    {
        'id': 'extra_super_order_type3',
        'autocancel_time_in_seconds': 20,
        'driver_cancel_cost': '0.0000',
        'color': '#2B4059',
        'name': 'Name2',
        'is_client_address_shown': False,
        'is_client_phone_shown': True,
        'driver_waiting_cost': '50.0000',
        'morning_visibility': {'period': 'ч', 'value': 3},
        'night_visibility': {'period': 'скрыть', 'value': 3},
        'weekend_visibility': {'period': 'д', 'value': 3},
    },
]


@pytest.mark.parametrize(
    'params, tested_item, expected_response',
    [
        (None, None, {'code': '400', 'message': 'Missing park_id in query'}),
        (
            defaults.PARAMS,
            utils.modify_base_dict(
                BASE_REQUEST_ORDER_TYPE,
                {
                    'id': 'extra_super_order_type4',
                    'driver_cancel_cost': '!.00',
                },
            ),
            {
                'code': '400',
                'message': (
                    'Field \'order_type.driver_cancel_cost\' '
                    'must be able to convert from string to double'
                ),
            },
        ),
        (
            defaults.PARAMS,
            utils.modify_base_dict(
                BASE_REQUEST_ORDER_TYPE,
                {
                    'id': 'extra_super_order_type4',
                    'driver_waiting_cost': '2.0000#',
                },
            ),
            {
                'code': '400',
                'message': (
                    'Field \'order_type.driver_waiting_cost\' '
                    'must be able to convert from string to double'
                ),
            },
        ),
    ],
)
async def test_bad_request(
        taxi_driver_work_rules, params, tested_item, expected_response,
):
    order_types = []
    if tested_item:
        order_types = BASE_REQUEST_ORDER_TYPE_FOR_PUT.copy()
        order_types.append(tested_item)

    request_body = {'order_types': order_types}
    response = await taxi_driver_work_rules.put(
        ENDPOINT, params=params, headers=defaults.HEADERS, json=request_body,
    )
    assert response.status_code == 400
    assert response.json() == expected_response


EXPECTED_REDIS_ORDER_TYPES = {
    'extra_super_order_type1': {
        'Name': 'Name',
        'Color': 'White',
        'ShowAddress': True,
        'ShowPhone': True,
        'MorningValue': 3,
        'MorningPerroid': 'м',
        'NightValue': 2,
        'NightPerroid': 'скрыть',
        'WeekendValue': 0,
        'WeekendPerroid': '',
        'AutoCancel': 10,
        'CancelCost': 50.0,
        'WaitingCost': 50.0,
    },
    'extra_super_order_type2': {
        'Name': 'Name1',
        'Color': '',
        'ShowAddress': False,
        'ShowPhone': True,
        'MorningValue': 2,
        'MorningPerroid': 'ч',
        'NightValue': 2,
        'NightPerroid': 'скрыть',
        'WeekendValue': 2,
        'WeekendPerroid': 'д',
        'AutoCancel': 20,
        'CancelCost': 0.0,
        'WaitingCost': 50.0,
    },
    'extra_super_order_type3': {
        'Name': 'Name2',
        'Color': '#2B4059',
        'ShowAddress': False,
        'ShowPhone': True,
        'MorningValue': 3,
        'MorningPerroid': 'ч',
        'NightValue': 3,
        'NightPerroid': 'скрыть',
        'WeekendValue': 3,
        'WeekendPerroid': 'д',
        'AutoCancel': 20,
        'CancelCost': 0.0,
        'WaitingCost': 50.0,
    },
}

EXPECTED_REDIS_NAMES_TO_IDS = {
    'NAME': 'extra_super_order_type1',
    'NAME1': 'extra_super_order_type2',
    'NAME2': 'extra_super_order_type3',
}


@pytest.mark.parametrize(
    'request_order_types, expected_redis_order_types, '
    'expected_redis_names_to_ids',
    [
        (
            BASE_REQUEST_ORDER_TYPE_FOR_PUT,
            EXPECTED_REDIS_ORDER_TYPES,
            EXPECTED_REDIS_NAMES_TO_IDS,
        ),
    ],
)
async def test_creating_ok(
        taxi_driver_work_rules,
        redis_store,
        request_order_types,
        expected_redis_order_types,
        expected_redis_names_to_ids,
):
    request_body = {'order_types': request_order_types}

    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == request_body

    assert (
        utils.get_redis_order_types(redis_store) == expected_redis_order_types
    )
    assert (
        utils.get_order_types_names_to_ids(redis_store)
        == expected_redis_names_to_ids
    )


@pytest.mark.redis_store(
    [
        'hmset',
        defaults.RULE_TYPE_ITEMS_KEY,
        {
            'extra_super_order_type1': json.dumps(
                defaults.BASE_REDIS_ORDER_TYPE,
            ),
            'extra_super_order_type2': json.dumps(
                {'Name': 'extra_super_name2'},
            ),
        },
    ],
    [
        'hmset',
        defaults.RULE_TYPE_NAMES_TO_IDS,
        {
            'NAME': 'extra_super_order_type1',
            'NAME1': 'extra_super_order_type2',
        },
    ],
)
@pytest.mark.parametrize(
    'request_order_types, expected_redis_order_types, '
    'expected_redis_names_to_ids',
    [
        (
            BASE_REQUEST_ORDER_TYPE_FOR_PUT,
            EXPECTED_REDIS_ORDER_TYPES,
            EXPECTED_REDIS_NAMES_TO_IDS,
        ),
        (
            [
                {
                    'id': 'extra_super_order_type4',
                    'autocancel_time_in_seconds': 10,
                    'driver_cancel_cost': '50.0000',
                    'color': 'White',
                    'name': 'Name',
                    'is_client_address_shown': True,
                    'is_client_phone_shown': True,
                    'driver_waiting_cost': '50.0000',
                    'morning_visibility': {'period': 'ч', 'value': 3},
                    'night_visibility': {'period': 'всегда', 'value': 0},
                    'weekend_visibility': {'period': 'д', 'value': 3},
                },
            ],
            {
                'extra_super_order_type4': {
                    'Name': 'Name',
                    'Color': 'White',
                    'ShowAddress': True,
                    'ShowPhone': True,
                    'MorningValue': 3,
                    'MorningPerroid': 'ч',
                    'NightValue': 0,
                    'NightPerroid': 'всегда',
                    'WeekendValue': 3,
                    'WeekendPerroid': 'д',
                    'AutoCancel': 10,
                    'CancelCost': 50.0,
                    'WaitingCost': 50.0,
                },
            },
            {'NAME': 'extra_super_order_type4'},
        ),
    ],
)
async def test_updating_ok(
        taxi_driver_work_rules,
        redis_store,
        request_order_types,
        expected_redis_order_types,
        expected_redis_names_to_ids,
):
    request_body = {'order_types': request_order_types}

    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == request_body

    assert (
        utils.get_redis_order_types(redis_store) == expected_redis_order_types
    )
    assert (
        utils.get_order_types_names_to_ids(redis_store)
        == expected_redis_names_to_ids
    )


@pytest.mark.parametrize(
    'order_types_in_redis, names_to_ids_in_redis, request_order_types, '
    'expected_redis_names_to_ids',
    [
        # test name normalization
        (
            {},
            {},
            [
                {
                    'id': 'extra_super_order_type4',
                    'autocancel_time_in_seconds': 10,
                    'driver_cancel_cost': '50.0000',
                    'color': 'White',
                    'name': '  Ордер тип ',
                    'is_client_address_shown': True,
                    'is_client_phone_shown': True,
                    'driver_waiting_cost': '50.0000',
                    'morning_visibility': {'period': 'ч', 'value': 3},
                    'night_visibility': {'period': 'всегда', 'value': 0},
                    'weekend_visibility': {'period': 'д', 'value': 3},
                },
            ],
            {'ОРДЕР ТИП': 'extra_super_order_type4'},
        ),
        # test duplicate names
        (
            {},
            {},
            [
                {
                    'id': 'extra_super_order_type4',
                    'autocancel_time_in_seconds': 10,
                    'driver_cancel_cost': '50.0000',
                    'color': 'White',
                    'name': '  Ордер тип ',
                    'is_client_address_shown': True,
                    'is_client_phone_shown': True,
                    'driver_waiting_cost': '50.0000',
                    'morning_visibility': {'period': 'ч', 'value': 3},
                    'night_visibility': {'period': 'всегда', 'value': 0},
                    'weekend_visibility': {'period': 'д', 'value': 3},
                },
                {
                    'id': 'extra_super_order_type4',
                    'autocancel_time_in_seconds': 10,
                    'driver_cancel_cost': '50.0000',
                    'color': 'White',
                    'name': 'Ордер ТИП',
                    'is_client_address_shown': True,
                    'is_client_phone_shown': True,
                    'driver_waiting_cost': '50.0000',
                    'morning_visibility': {'period': 'ч', 'value': 3},
                    'night_visibility': {'period': 'всегда', 'value': 0},
                    'weekend_visibility': {'period': 'д', 'value': 3},
                },
            ],
            {'ОРДЕР ТИП': 'extra_super_order_type4'},
        ),
        # test remove all
        (
            {
                'extra_super_order_type': json.dumps(
                    {'Name': 'extra_super_name'},
                ),
            },
            {'EXTRA_SUPER_NAME': 'extra_super_order_type'},
            [],
            {},
        ),
        # test substract
        (
            {
                'extra_super_order_type': json.dumps(
                    {'Name': 'extra_super_name'},
                ),
                'extra_super_order_type1': json.dumps(
                    {'Name': 'extra_super_name1'},
                ),
            },
            {
                'EXTRA_SUPER_NAME': 'extra_super_order_type',
                'EXTRA_SUPER_NAME1': 'extra_super_order_type1',
            },
            [
                {
                    'id': 'extra_super_order_type',
                    'autocancel_time_in_seconds': 10,
                    'driver_cancel_cost': '50.0000',
                    'color': 'White',
                    'name': 'extra_super_name',
                    'is_client_address_shown': True,
                    'is_client_phone_shown': True,
                    'driver_waiting_cost': '50.0000',
                    'morning_visibility': {'period': 'ч', 'value': 3},
                    'night_visibility': {'period': 'всегда', 'value': 0},
                    'weekend_visibility': {'period': 'д', 'value': 3},
                },
                {
                    'id': 'extra_super_order_type2',
                    'autocancel_time_in_seconds': 10,
                    'driver_cancel_cost': '50.0000',
                    'color': 'White',
                    'name': 'extra_super_name2',
                    'is_client_address_shown': True,
                    'is_client_phone_shown': True,
                    'driver_waiting_cost': '50.0000',
                    'morning_visibility': {'period': 'ч', 'value': 3},
                    'night_visibility': {'period': 'всегда', 'value': 0},
                    'weekend_visibility': {'period': 'д', 'value': 3},
                },
            ],
            {
                'EXTRA_SUPER_NAME': 'extra_super_order_type',
                'EXTRA_SUPER_NAME2': 'extra_super_order_type2',
            },
        ),
        # test change name
        (
            {
                'extra_super_order_type': json.dumps(
                    {'Name': 'extra_super_name'},
                ),
            },
            {'EXTRA_SUPER_NAME': 'extra_super_order_type'},
            [
                {
                    'id': 'extra_super_order_type',
                    'autocancel_time_in_seconds': 10,
                    'driver_cancel_cost': '50.0000',
                    'color': 'White',
                    'name': 'extra_super_name10',
                    'is_client_address_shown': True,
                    'is_client_phone_shown': True,
                    'driver_waiting_cost': '50.0000',
                    'morning_visibility': {'period': 'ч', 'value': 3},
                    'night_visibility': {'period': 'всегда', 'value': 0},
                    'weekend_visibility': {'period': 'д', 'value': 3},
                },
            ],
            {'EXTRA_SUPER_NAME10': 'extra_super_order_type'},
        ),
        # test change id
        (
            {
                'extra_super_order_type': json.dumps(
                    {'Name': 'extra_super_name'},
                ),
            },
            {'EXTRA_SUPER_NAME': 'extra_super_order_type'},
            [
                {
                    'id': 'extra_super_order_type10',
                    'autocancel_time_in_seconds': 10,
                    'driver_cancel_cost': '50.0000',
                    'color': 'White',
                    'name': 'extra_super_name',
                    'is_client_address_shown': True,
                    'is_client_phone_shown': True,
                    'driver_waiting_cost': '50.0000',
                    'morning_visibility': {'period': 'ч', 'value': 3},
                    'night_visibility': {'period': 'всегда', 'value': 0},
                    'weekend_visibility': {'period': 'д', 'value': 3},
                },
            ],
            {'EXTRA_SUPER_NAME': 'extra_super_order_type10'},
        ),
    ],
)
async def test_name_to_ids(
        taxi_driver_work_rules,
        redis_store,
        order_types_in_redis,
        names_to_ids_in_redis,
        request_order_types,
        expected_redis_names_to_ids,
):
    if order_types_in_redis:
        redis_store.hmset(defaults.RULE_TYPE_ITEMS_KEY, order_types_in_redis)
    if names_to_ids_in_redis:
        redis_store.hmset(
            defaults.RULE_TYPE_NAMES_TO_IDS, names_to_ids_in_redis,
        )

    request_body = {'order_types': request_order_types}

    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        params=defaults.PARAMS,
        headers=defaults.HEADERS,
        json=request_body,
    )

    assert response.status_code == 200
    assert response.json() == request_body

    assert (
        utils.get_order_types_names_to_ids(redis_store)
        == expected_redis_names_to_ids
    )
