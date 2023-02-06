import json

import pytest

ENDPOINT = 'v1/parks/orders/bulk_retrieve/raw'


async def common_request(taxi_driver_orders, request, code, expected_response):
    response = await taxi_driver_orders.post(ENDPOINT, json=request)

    assert response.status_code == code, response.text
    if code == 400:
        assert response.json()['code'] == '400'
    else:
        assert response.json() == expected_response


TEST_BAD_PARAMS = [
    ({}, {'code': '400', 'message': 'Field \'query\' is missing'}),
    (
        {'query': {'park': {}}},
        {'code': '400', 'message': 'Field \'query.park.id\' is missing'},
    ),
    (
        {'query': {'park': {'id': 'park_id'}}},
        {'code': '400', 'message': 'Field \'query.park.order\' is missing'},
    ),
    (
        {'query': {'park': {'id': 'park_id', 'order': {}}}},
        {
            'code': '400',
            'message': 'Field \'query.park.order.ids\' is missing',
        },
    ),
    (
        {'query': {'park': {'id': 'park_id', 'order': {'ids': []}}}},
        {
            'code': '400',
            'message': (
                'Value of \'query.park.order.ids\': incorrect size, '
                'must be 1 (limit) <= 0 (value)'
            ),
        },
    ),
    (
        {'query': {'park': {'id': 'park_id', 'order': {'ids': ['']}}}},
        {
            'code': '400',
            'message': (
                'Value of \'query.park.order.ids[0]\': incorrect size, '
                'must be 1 (limit) <= 0 (value)'
            ),
        },
    ),
]


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
@pytest.mark.parametrize('payload, expected_response', TEST_BAD_PARAMS)
async def test_bad_request(
        taxi_driver_orders,
        fleet_parks_shard,
        payload,
        expected_response,
        yt_apply,
):
    await common_request(taxi_driver_orders, payload, 400, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_empty_orders(taxi_driver_orders, fleet_parks_shard, yt_apply):
    payload = {
        'query': {'park': {'id': 'park_id_???', 'order': {'ids': ['1']}}},
    }

    expected_response = {'orders': [{'id': '1'}]}

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_one_order(taxi_driver_orders, fleet_parks_shard, yt_apply):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_0',
                'order': {'ids': ['order0'], 'cut_hidden_fields': False},
            },
        },
    }

    expected_response = {
        'orders': [
            {
                'id': 'order0',
                'order': {
                    'category': 32,
                    'cost_coupon': '0',
                    'cost_pay': '100.99',
                    'cost_sub': '0',
                    'cost_total': '159.99911',
                    'driver_id': 'driver_id_0',
                    'payment': 5,
                    'provider': 1,
                    'status': 50,
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_many_orders(taxi_driver_orders, fleet_parks_shard, yt_apply):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_1',
                'order': {
                    'ids': ['order1', 'order???', 'order2'],
                    'cut_hidden_fields': False,
                },
            },
        },
    }

    expected_response = {
        'orders': [
            {
                'id': 'order1',
                'order': {
                    'category': 65536,
                    'cost_coupon': '0',
                    'cost_sub': '0',
                    'driver_id': 'driver_id_1',
                    'payment': 0,
                    'provider': 0,
                    'status': 50,
                },
            },
            {'id': 'order???'},
            {
                'id': 'order2',
                'order': {
                    'category': 0,
                    'cost_coupon': '0',
                    'cost_pay': '157',
                    'cost_sub': '0',
                    'cost_total': '157',
                    'driver_id': 'driver_id_2',
                    'payment': 0,
                    'provider': 0,
                    'status': 50,
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Order:SetCar:Items:park_id_3',
        {'order6': json.dumps({'provider': 2})},
    ],
)
async def test_fallback_yt(taxi_driver_orders, fleet_parks_shard, yt_apply):
    payload = {
        'query': {
            'park': {
                'id': 'park_id_3',
                'order': {
                    'ids': ['order6', 'order99'],
                    'cut_hidden_fields': False,
                },
            },
        },
        'lookup_yt': True,
    }

    expected_response = {
        'orders': [
            {
                'id': 'order6',
                'order': {
                    'category': 32,
                    'cost_coupon': '0',
                    'cost_pay': '100',
                    'cost_sub': '0',
                    'cost_total': '100',
                    'provider': 2,
                    'status': 10,
                },
            },
            {
                'id': 'order99',
                'order': {
                    'category': 0,
                    'cost_coupon': '0',
                    'cost_pay': '222',
                    'cost_total': '224',
                    'driver_id': 'driver_id_0',
                    'payment': 0,
                    'provider': 1,
                    'status': 50,
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_fallback_yt_disabled_by_request(
        taxi_driver_orders, fleet_parks_shard, yt_apply,
):
    payload = {
        'query': {'park': {'id': 'park_id_3', 'order': {'ids': ['order99']}}},
        'lookup_yt': False,
    }

    expected_response = {'orders': [{'id': 'order99'}]}

    await common_request(taxi_driver_orders, payload, 200, expected_response)


@pytest.mark.config(DRIVER_ORDERS_FORCE_FALLBACK_YT=True)
@pytest.mark.yt(
    schemas=['yt_orders_dyn_schema.yaml'],
    dyn_table_data=['yt_orders_dyn_data.yaml'],
)
async def test_force_fallback_yt(
        taxi_driver_orders, fleet_parks_shard, yt_apply,
):
    payload = {
        'query': {'park': {'id': 'park_id_3', 'order': {'ids': ['order99']}}},
        'lookup_yt': False,
    }

    expected_response = {
        'orders': [
            {
                'id': 'order99',
                'order': {
                    'driver_id': 'driver_id_0',
                    'provider': 1,
                    'status': 50,
                },
            },
        ],
    }

    await common_request(taxi_driver_orders, payload, 200, expected_response)
