from typing import List

import pytest

from testsuite.utils import matching


async def test_without_criterias(taxi_cargo_c2c):
    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/search',
        headers={'Accept-Language': 'ru'},
        json={},
    )

    assert response.status_code == 400


async def test_by_order_id(taxi_cargo_c2c, create_cargo_c2c_orders):
    order_id = await create_cargo_c2c_orders()
    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/search',
        headers={'Accept-Language': 'ru'},
        json={
            'order_id': {
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'deliveries': [
            {
                'created_ts': matching.datetime_string,
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_1',
                'roles': ['sender'],
            },
            {
                'created_ts': matching.datetime_string,
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_2',
                'roles': ['recipient'],
            },
            {
                'created_ts': matching.datetime_string,
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_3',
                'roles': ['initiator'],
            },
        ],
    }


async def test_by_phone(taxi_cargo_c2c, create_cargo_c2c_orders, mockserver):
    order_id = await create_cargo_c2c_orders()

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_bulk_store(request):
        return {
            'items': [
                {'id': item['value'][:-3], 'value': item['value']}
                for item in request.json['items']
            ],
        }

    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/search',
        headers={'Accept-Language': 'ru'},
        json={'phone': 'phone_pd_id_1_ph'},
    )
    assert response.status_code == 200
    assert response.json() == {
        'deliveries': [
            {
                'created_ts': matching.datetime_string,
                'order_id': order_id,
                'order_provider_id': 'cargo-c2c',
                'phone_pd_id': 'phone_pd_id_1',
                'roles': ['sender'],
            },
        ],
    }


@pytest.mark.parametrize(
    ('offset', 'limit', 'expected_result'),
    [(0, 2, ['second', 'first']), (0, 1, ['second']), (1, 1, ['first'])],
)
async def test_limit_offset(
        taxi_cargo_c2c,
        create_cargo_c2c_orders,
        offset: int,
        limit: int,
        expected_result: List[str],
        mockserver,
):
    first_order_id = await create_cargo_c2c_orders()
    second_order_id = await create_cargo_c2c_orders()

    expected_orders = []
    for item in expected_result:
        if item == 'first':
            expected_orders.append(first_order_id)
        elif item == 'second':
            expected_orders.append(second_order_id)

    @mockserver.json_handler('/personal/v1/phones/bulk_store')
    def _phones_bulk_store(request):
        return {
            'items': [
                {'id': item['value'][:-3], 'value': item['value']}
                for item in request.json['items']
            ],
        }

    response = await taxi_cargo_c2c.post(
        '/v1/admin/delivery/search',
        headers={'Accept-Language': 'ru'},
        json={'phone': 'phone_pd_id_1_ph', 'limit': limit, 'offset': offset},
    )
    assert response.status_code == 200
    orders = [item['order_id'] for item in response.json()['deliveries']]
    assert orders == expected_orders
