import datetime

import asynctest
import pytest

from eats_integration_offline_orders.generated.service.swagger.models import (
    api as api_module,
)
from test_eats_integration_offline_orders import utils


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_get_check(
        web_app_client, pos_client_mock, table_uuid, load_json,
):

    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200
    data = await response.json()
    assert data == load_json('api_response.json')


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_get_check_create_order(
        web_app_client, web_context, pos_client_mock, table_uuid, load_json,
):
    async def _get_all_orders():
        return await web_context.pg.secondary.fetch('SELECT * FROM orders;')

    orders = await _get_all_orders()
    assert not orders

    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200

    orders = await _get_all_orders()
    assert orders

    order = orders[0]
    assert order['uuid']
    assert order['table_id']
    assert order['items']
    assert order['items_hash']


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders.sql'],
)
async def test_get_check_update_existing_order(
        web_app_client, web_context, pos_client_mock, table_uuid, load_json,
):

    pos_order = load_json('orders.json')['orders'][0]
    pos_order['items'][0]['quantity'] = 3

    pos_client_mock.get_check.return_value = api_module.PosOrders(
        orders=[api_module.PosOrder.deserialize(pos_order)],
    )

    old_order = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM orders LIMIT 1;',
    )

    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200

    updated_order = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM orders LIMIT 1;',
    )

    assert updated_order['items_hash'] != old_order['items_hash']
    assert updated_order['items'] != old_order['items']


@pytest.mark.client_experiments3(
    consumer='eats-integration-offline-orders/service_fee',
    experiment_name='eats_integration_offline_orders-service_fee',
    args=[{'name': 'place_id', 'type': 'string', 'value': 'place_id__1'}],
    value={'fee': 100.0},
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_get_check_service_fee(
        web_app_client, pos_client_mock, table_uuid, place_id, load_json,
):

    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200
    data = await response.json()

    utils.partial_matcher(
        load_json('partial_api_response_service_fee.json'), data,
    )


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_get_check_with_discounts(
        web_app_client, pos_client_mock, table_uuid, load_json,
):
    pos_client_mock.get_check = asynctest.CoroutineMock(
        return_value=api_module.PosOrders.deserialize(
            data=load_json('orders_with_discounts.json'),
        ),
    )

    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200
    actual_data = await response.json()

    utils.partial_matcher(
        load_json('partial_api_response_with_discounts.json'), actual_data,
    )


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders_with_zero_prices.sql'],
)
async def test_get_check_only_not_fully_paid_orders(
        web_app_client, pos_client_mock, table_uuid, load_json,
):
    pos_client_mock.get_check = asynctest.CoroutineMock(
        return_value=api_module.PosOrders.deserialize(
            data=load_json('orders_with_zero_prices.json'),
        ),
    )

    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200
    data = await response.json()
    assert data['orders'] == []


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders_not_created.sql'],
)
@pytest.mark.now(datetime.datetime(2022, 2, 2, 2).isoformat())
async def test_get_check_orders_not_created_without_user(
        web_app_client, pos_client_mock, table_uuid,
):
    pos_client_mock.get_check = asynctest.CoroutineMock(
        return_value=api_module.PosOrders.deserialize(data={'orders': []}),
    )

    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200
    data = await response.json()
    assert data == {'orders': [], 'users_info': []}


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders_not_created.sql'],
)
@pytest.mark.now(datetime.datetime(2022, 2, 2, 2).isoformat())
async def test_get_check_orders_not_created_other_user(
        web_app_client, pos_client_mock, table_uuid,
):
    pos_client_mock.get_check = asynctest.CoroutineMock(
        return_value=api_module.PosOrders.deserialize(data={'orders': []}),
    )

    response = await web_app_client.get(
        f'/v1/check?uuid={table_uuid}', headers={'X-Eats-User': 'not_123'},
    )
    assert response.status == 200
    data = await response.json()
    assert data == {'orders': [], 'users_info': []}


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders_not_created.sql'],
)
@pytest.mark.now(datetime.datetime(2022, 2, 2, 2).isoformat())
async def test_get_check_orders_not_created(
        web_app_client, pos_client_mock, table_uuid, load_json,
):
    pos_client_mock.get_check = asynctest.CoroutineMock(
        return_value=api_module.PosOrders.deserialize(data={'orders': []}),
    )

    response = await web_app_client.get(
        f'/v1/check?uuid={table_uuid}', headers={'X-Eats-User': '123'},
    )
    assert response.status == 200
    data = await response.json()
    utils.partial_matcher(
        load_json('partial_api_response_orders_not_created.json'), data,
    )


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['restaurants.sql', 'tables.sql', 'orders_not_created.sql'],
)
@pytest.mark.now(datetime.datetime(2022, 2, 2, 2, 2).isoformat())
async def test_get_check_orders_not_created_set_error(
        web_app_client, pos_client_mock, table_uuid, load_json,
):
    pos_client_mock.get_check = asynctest.CoroutineMock(
        return_value=api_module.PosOrders.deserialize(data={'orders': []}),
    )

    response = await web_app_client.get(
        f'/v1/check?uuid={table_uuid}', headers={'X-Eats-User': '123'},
    )
    assert response.status == 200
    data = await response.json()
    utils.partial_matcher(
        load_json('partial_api_response_orders_error.json'), data,
    )


@pytest.mark.client_experiments3(
    consumer='eats-integration-offline-orders/ya_discount',
    config_name='eats_integration_offline_orders-ya_discount',
    args=[{'name': 'place_id', 'type': 'string', 'value': 'place_id__1'}],
    value={'val': '10%'},
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'tables.sql'],
)
async def test_get_check_with_ya_discount_percents(
        web_app_client, pos_client_mock, table_uuid, load_json,
):
    pos_client_mock.get_check = asynctest.CoroutineMock(
        return_value=api_module.PosOrders.deserialize(
            data=load_json('orders_with_ya_discount.json'),
        ),
    )

    response = await web_app_client.get(f'/v1/check?uuid={table_uuid}')
    assert response.status == 200
    data = await response.json()
    utils.partial_matcher(
        load_json('partial_api_response_with_ya_discount.json'), data,
    )
