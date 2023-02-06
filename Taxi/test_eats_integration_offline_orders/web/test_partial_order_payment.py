import asyncio
import json
import typing

import pytest

from eats_integration_offline_orders.internal import enums
from test_eats_integration_offline_orders import utils


base_database = utils.BaseDatabase(  # pylint:disable=invalid-name
    restaurants='restaurants.sql',
    restaurants_options='restaurants_options.sql',
    tables='tables.sql',
    orders='orders.sql',
)


@base_database()
async def test_partial_order_payment_200(
        web_app_client, order_uuid, payture_mocks,
):
    response = await web_app_client.post(
        f'/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [
                {'item_id': 'product_id__1', 'quantity': 1},
                {'item_id': 'product_id__2', 'quantity': 1},
            ],
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['redirect_link']
    assert response_data['transaction_uuid']


@base_database()
async def test_partial_order_payment_create_transaction(
        web_app_client, order_uuid, payture_mocks, web_context,
):
    response = await web_app_client.post(
        f'/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [
                {'item_id': 'product_id__1', 'quantity': 1},
                {'item_id': 'product_id__2', 'quantity': 1},
            ],
        },
    )
    assert response.status == 200

    transactions = await web_context.pg.secondary.fetch(
        'SELECT * FROM payment_transactions;',
    )
    assert transactions
    transaction = transactions[0]
    assert transaction['order_id'] == 1
    assert (
        transaction['status']
        == enums.PaymentTransactionStatus.IN_PROGRESS.value
    )
    transaction_items = json.loads(transaction['order_items'])
    assert len(transaction_items) == 2
    assert transaction_items[0]['id'] == 'product_id__1'
    assert transaction_items[0]['quantity'] == 1
    assert transaction_items[1]['id'] == 'product_id__2'
    assert transaction_items[1]['quantity'] == 1


@base_database()
async def test_partial_order_payment_mark_as_in_pay(
        web_app_client, order_uuid, payture_mocks, web_context,
):
    response = await web_app_client.post(
        f'/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [
                {'item_id': 'product_id__1', 'quantity': 1},
                {'item_id': 'product_id__2', 'quantity': 1},
            ],
        },
    )
    assert response.status == 200

    order = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM orders WHERE uuid = $1;', order_uuid,
    )
    order_items = json.loads(order['items'])
    assert order_items[0]['id'] == 'product_id__1'
    assert order_items[0]['in_pay_count'] == 1
    assert order_items[1]['id'] == 'product_id__2'
    assert order_items[1]['in_pay_count'] == 1


@base_database()
async def test_partial_order_payment_rollback_if_payture_fail(
        web_app_client,
        order_uuid,
        payture_mocks,
        web_context,
        table_uuid,
        mockserver,
        load,
):

    init_path = web_context.payture_client.config['init_path']

    @mockserver.handler(f'/payture{init_path}')
    def _init(request):
        return mockserver.make_response(load('payture/response_init_fail.xml'))

    response = await web_app_client.post(
        f'/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [
                {'item_id': 'product_id__1', 'quantity': 1},
                {'item_id': 'product_id__2', 'quantity': 1},
            ],
        },
    )
    assert response.status == 400

    order = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM orders WHERE uuid = $1;', order_uuid,
    )
    order_items = json.loads(order['items'])
    assert order_items[0]['id'] == 'product_id__1'
    assert order_items[0]['in_pay_count'] == 0
    assert order_items[1]['id'] == 'product_id__2'
    assert order_items[1]['in_pay_count'] == 0

    transaction = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM payment_transactions LIMIT 1;',
    )
    assert (
        transaction['status'] == enums.PaymentTransactionStatus.CANCELED.value
    )


@base_database()
async def test_partial_order_payment_400_if_not_enough_items(
        web_app_client, order_uuid,
):
    response = await web_app_client.post(
        f'/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [
                {'item_id': 'pos_item_id__1', 'quantity': 12},
                {'item_id': 'pos_item_id__2', 'quantity': 1},
            ],
        },
    )
    assert response.status == 400


@base_database()
async def test_partial_order_payment_with_noninteger_quantities_200(
        web_app_client, order_uuid, payture_mocks,
):
    response = await web_app_client.post(
        f'/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [
                {'item_id': 'product_id__1', 'quantity': 0.5},
                {'item_id': 'product_id__2', 'quantity': 0.5},
            ],
        },
    )
    assert response.status == 200
    response_data = await response.json()
    assert response_data['redirect_link']
    assert response_data['transaction_uuid']


@base_database(restaurants_options='restaurants_options_split_disabled.sql')
async def test_partial_order_payment_disable_403(
        web_app_client, order_uuid, payture_mocks,
):
    response = await web_app_client.post(
        f'/v1/pay/partial',
        json={
            'order_uuid': order_uuid,
            'order_items': [{'item_id': 'product_id__1', 'quantity': 1}],
        },
    )
    assert response.status == 403


def _make_request_data(
        pay_type='trust_card',
        pay_method_id: typing.Optional[str] = 'card-x66b88c90fc8d571e6d5e9715',
):
    result = {'pay_type': pay_type, 'pay_method_id': pay_method_id}
    return {key: value for key, value in result.items() if value is not None}


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'restaurants.sql', 'orders.sql'],
)
@pytest.mark.parametrize(
    'request_data,expected_status,expected_response,',
    [
        pytest.param(_make_request_data(), 200, None, id='success'),
        pytest.param(
            _make_request_data(pay_method_id=None),
            403,
            {'message': 'payment method trust_card is not available'},
            id='without pay_method_id for card',
        ),
    ],
)
async def test_partial_order_payment_trust(
        web_app_client,
        web_context,
        order_uuid,
        mock_epma_v1_payment_methods_availability,
        stq,
        # params:
        request_data,
        expected_status,
        expected_response,
):
    response = await web_app_client.post(
        f'/v1/pay/partial',
        headers={
            'X-Eats-User': 'personal_phone_id=test_personal_phone_id',
            'X-Yandex-Uid': 'test_yandex_uid',
        },
        json={
            'order_uuid': order_uuid,
            'order_items': [{'item_id': 'product_id__1', 'quantity': 1}],
            **request_data,
        },
    )
    assert response.status == expected_status
    data = await response.json()
    if expected_status == 200:
        assert 'transaction_uuid' in data
        assert mock_epma_v1_payment_methods_availability.times_called == 1
        assert (
            stq.ei_offline_orders_trust_payment_create_order.times_called == 1
        )
    if expected_response is not None:
        assert data == expected_response


@pytest.mark.parametrize(
    'idempotency_token_1,idempotency_token_2,expected_times_called',
    [
        pytest.param(
            'idempotency_token_1',
            'idempotency_token_1',
            1,
            id='the same token per 2 requests',
        ),
        pytest.param(
            'idempotency_token_1',
            'idempotency_token_2',
            2,
            id='different tokens per 2 requests',
        ),
    ],
)
@base_database()
async def test_order_payment_idempotency_token(
        taxi_eats_integration_offline_orders_web,
        web_context,
        testpoint,
        payture_mocks,
        table_uuid,
        order_uuid,
        # params:
        idempotency_token_1,
        idempotency_token_2,
        expected_times_called,
):
    request_json = {
        'order_uuid': order_uuid,
        'order_items': [{'item_id': 'product_id__1', 'quantity': 1}],
    }

    coro: typing.Optional[typing.Awaitable] = None

    @testpoint('idempotency_token_testpoint')
    def idempotency_token_testpoint(data):
        nonlocal coro
        if coro is not None:
            return
        # sending second request during first request is handling
        coro = asyncio.create_task(
            taxi_eats_integration_offline_orders_web.post(
                f'/v1/pay/partial',
                headers={'X-Idempotency-Token': idempotency_token_2},
                json=request_json,
            ),
        )

    response_1 = await taxi_eats_integration_offline_orders_web.post(
        f'/v1/pay/partial',
        headers={'X-Idempotency-Token': idempotency_token_1},
        json=request_json,
    )
    assert idempotency_token_testpoint.times_called == 1

    assert response_1.status == 200
    assert coro is not None
    response_2 = await coro
    assert response_2.status == 200

    assert payture_mocks['init'].times_called == expected_times_called

    data_1 = await response_1.json()
    data_2 = await response_1.json()
    assert data_1['redirect_link'] is not None
    assert data_1['redirect_link'] == data_2['redirect_link']


async def test_partial_order_payment_cash(
        taxi_eats_integration_offline_orders_web,
):
    response = await taxi_eats_integration_offline_orders_web.post(
        f'/v1/pay/partial',
        json={
            'uuid': 'uuid',
            'order_uuid': 'uuid',
            'order_items': [
                {'item_id': 'product_id__1', 'quantity': 1},
                {'item_id': 'product_id__2', 'quantity': 1},
            ],
            'pay_type': 'cash',
        },
    )
    assert response.status == 400
    body = await response.json()
    assert body == {'message': 'cash is not available in this handler'}
