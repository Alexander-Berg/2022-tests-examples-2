# encoding=utf-8
import json

import pytest

from testsuite.utils import ordered_object

from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils


ENDPOINT = 'sync/v1/order-types/list'

HEADERS = {'X-Ya-Service-Ticket': defaults.X_YA_SERVICE_TICKET}


@pytest.mark.parametrize(
    'request_body',
    [
        ({}),
        ({'query': {'park': {'id': ''}}},),
        (
            {
                'query': {
                    'park': {
                        'id': defaults.PARK_ID,
                        'order_type': {'ids': []},
                    },
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


def build_request_body(park_id, rule_ids):
    park = {'id': park_id}
    if rule_ids is not None:
        park['order_type'] = {'ids': rule_ids}
    return {'query': {'park': park}}


def build_expected_response(fields):
    order_type = defaults.BASE_RESPONSE_ORDER_TYPE.copy()
    order_type.update(fields)
    return {'order_types': [order_type]}


@pytest.mark.redis_store(
    [
        'hmset',
        defaults.RULE_TYPE_ITEMS_KEY,
        {
            'order_type_1': json.dumps(defaults.BASE_REDIS_ORDER_TYPE),
            'order_type_2': json.dumps(
                utils.modify_base_dict(
                    defaults.BASE_REDIS_ORDER_TYPE,
                    {'Name': defaults.TOO_LONG_NAME, 'Color': ''},
                ),
            ),
            'order_type_3': json.dumps(
                utils.modify_base_dict(
                    defaults.BASE_REDIS_ORDER_TYPE,
                    {'Name': defaults.MAXIMUM_LENGTH_NAME},
                ),
            ),
            'order_type_4': json.dumps({}),
            defaults.YANDEX: json.dumps(defaults.BASE_REDIS_ORDER_TYPE),
        },
    ],
)
@pytest.mark.parametrize(
    'request_body, expected_response',
    [
        (build_request_body('unknown_park_id', None), {'order_types': []}),
        (
            build_request_body(defaults.PARK_ID, None),
            {
                'order_types': [
                    {
                        'id': 'order_type_1',
                        'autocancel_time_in_seconds': 10,
                        'driver_cancel_cost': '50.0000',
                        'color': 'White',
                        'morning_visibility': {'period': 'м', 'value': 3},
                        'name': 'Name',
                        'night_visibility': {'period': 'скрыть', 'value': -1},
                        'is_client_address_shown': True,
                        'is_client_phone_shown': True,
                        'driver_waiting_cost': '50.0000',
                        'weekend_visibility': {'period': '', 'value': 0},
                    },
                    {
                        'id': 'order_type_2',
                        'autocancel_time_in_seconds': 10,
                        'driver_cancel_cost': '50.0000',
                        'color': '',
                        'morning_visibility': {'period': 'м', 'value': 3},
                        'name': defaults.TRUNCATED_TOO_LONG_NAME,
                        'night_visibility': {'period': 'скрыть', 'value': -1},
                        'is_client_address_shown': True,
                        'is_client_phone_shown': True,
                        'driver_waiting_cost': '50.0000',
                        'weekend_visibility': {'period': '', 'value': 0},
                    },
                    {
                        'id': 'order_type_3',
                        'autocancel_time_in_seconds': 10,
                        'driver_cancel_cost': '50.0000',
                        'color': 'White',
                        'morning_visibility': {'period': 'м', 'value': 3},
                        'name': defaults.MAXIMUM_LENGTH_NAME,
                        'night_visibility': {'period': 'скрыть', 'value': -1},
                        'is_client_address_shown': True,
                        'is_client_phone_shown': True,
                        'driver_waiting_cost': '50.0000',
                        'weekend_visibility': {'period': '', 'value': 0},
                    },
                    {
                        'id': 'order_type_4',
                        'autocancel_time_in_seconds': 0,
                        'driver_cancel_cost': '0.0000',
                        'color': '',
                        'morning_visibility': {'period': '', 'value': 0},
                        'name': '',
                        'night_visibility': {'period': '', 'value': 0},
                        'is_client_address_shown': False,
                        'is_client_phone_shown': False,
                        'driver_waiting_cost': '0.0000',
                        'weekend_visibility': {'period': '', 'value': 0},
                    },
                    {
                        'id': defaults.YANDEX,
                        'autocancel_time_in_seconds': 10,
                        'driver_cancel_cost': '0.0000',
                        'color': 'White',
                        'morning_visibility': {'period': 'м', 'value': 3},
                        'name': 'Name',
                        'night_visibility': {'period': 'скрыть', 'value': -1},
                        'is_client_address_shown': True,
                        'is_client_phone_shown': True,
                        'driver_waiting_cost': '50.0000',
                        'weekend_visibility': {'period': '', 'value': 0},
                    },
                ],
            },
        ),
        (
            build_request_body(defaults.PARK_ID, ['order_type_1']),
            build_expected_response({}),
        ),
        (
            build_request_body(defaults.PARK_ID, ['order_type_2']),
            build_expected_response(
                {
                    'id': 'order_type_2',
                    'name': defaults.TRUNCATED_TOO_LONG_NAME,
                    'color': '',
                },
            ),
        ),
        (
            build_request_body(defaults.PARK_ID, ['order_type_3']),
            build_expected_response(
                {'id': 'order_type_3', 'name': defaults.MAXIMUM_LENGTH_NAME},
            ),
        ),
        (
            build_request_body(
                defaults.PARK_ID, ['order_type_2', 'order_type_4'],
            ),
            {
                'order_types': [
                    {
                        'id': 'order_type_2',
                        'autocancel_time_in_seconds': 10,
                        'driver_cancel_cost': '50.0000',
                        'color': '',
                        'morning_visibility': {'period': 'м', 'value': 3},
                        'name': defaults.TRUNCATED_TOO_LONG_NAME,
                        'night_visibility': {'period': 'скрыть', 'value': -1},
                        'is_client_address_shown': True,
                        'is_client_phone_shown': True,
                        'driver_waiting_cost': '50.0000',
                        'weekend_visibility': {'period': '', 'value': 0},
                    },
                    {
                        'id': 'order_type_4',
                        'autocancel_time_in_seconds': 0,
                        'driver_cancel_cost': '0.0000',
                        'color': '',
                        'morning_visibility': {'period': '', 'value': 0},
                        'name': '',
                        'night_visibility': {'period': '', 'value': 0},
                        'is_client_address_shown': False,
                        'is_client_phone_shown': False,
                        'driver_waiting_cost': '0.0000',
                        'weekend_visibility': {'period': '', 'value': 0},
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
        response.json(), expected_response, ['order_types'],
    )
