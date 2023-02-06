# pylint: disable=redefined-outer-name
# pylint: disable=invalid-name
import json

import pytest

from eats_integration_offline_orders.internal import enums
from test_eats_integration_offline_orders import utils

TransactionStatus = enums.PaymentTransactionStatus

base_database = utils.BaseDatabase(
    tables='tables.sql',
    orders='orders.sql',
    restaurants='restaurants.sql',
    payment_transactions='payment_transactions.sql',
)


@pytest.fixture()
def payment_callback_response(web_app_client, load_json):
    async def _response(status=200):
        response = await web_app_client.post(
            '/v1/pay/callback',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            data=f'{load_json("payment_callback_request.json")["as_string"]}',
        )
        assert response.status == status
        return response

    return _response


@base_database()
async def test_payment_callback(payment_callback_response, billing_mocks):
    await payment_callback_response(200)


@base_database()
async def test_payment_callback_with_cipher(
        web_app_client, load_json, billing_mocks,
):

    response = await web_app_client.post(
        '/v1/pay/callback',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=(
            load_json('payment_callback_request.json')['as_cipher'][
                'encrypted'
            ]
        ),
    )

    assert response.status == 200


@base_database(
    orders='order_is_paid/orders.sql',
    payment_transactions='order_is_paid/payment_transactions.sql',
)
async def test_payment_callback_order_is_paid(
        payment_callback_response, pos_client_mock, billing_mocks, stq,
):
    await payment_callback_response(200)

    assert stq.ei_offline_orders_pos_pay_order.has_calls
    assert stq.ei_offline_orders_notify_order_paid.has_calls
    # pylint: disable=protected-access
    assert (
        stq.ei_offline_orders_notify_order_paid._queue._queue[0][1]['kwargs']
        == {
            'place_id': 'place_id__1',
            'table_nr': 'table_id__1',
            'amount': 0.43,
            'not_paid_amount': 0.0,
            'full_amount': 0.43,
            'is_fully_paid': True,
            'waiter_id': None,
            'order_uuid': 'order_uuid__1',
            'inner_order_id': None,
        }
    )


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={
        'payment_callback_ip_white_list': ['1.1.1.1'],
    },
)
@base_database()
@pytest.mark.parametrize('ip, result', [['1.1.1.1', 200], ['1.1.1.2', 403]])
async def test_payment_callback_ip_white_list(
        web_app_client, load_json, ip, result,
):

    response = await web_app_client.post(
        '/v1/pay/callback',
        headers={
            'X-Forwarded-For-Y': ip,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data=f'"{load_json("payment_callback_request.json")["as_string"]}"',
    )

    assert response.status == result


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={
        'payment_callback_ip_white_list': ['1.1.1.8/29'],
    },
)
@base_database()
@pytest.mark.parametrize('ip, result', [['1.1.1.9', 200], ['1.1.1.7', 403]])
async def test_payment_callback_ip_white_list_with_networks(
        web_app_client, load_json, ip, result,
):

    response = await web_app_client.post(
        '/v1/pay/callback',
        headers={
            'X-Forwarded-For-Y': ip,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data=f'"{load_json("payment_callback_request.json")["as_string"]}"',
    )

    assert response.status == result


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={
        'payment_callback_ip_white_list': ['1.1.1.1-1.1.1.4'],
    },
)
@base_database()
@pytest.mark.parametrize('ip, result', [['1.1.1.3', 200], ['1.1.1.5', 403]])
async def test_payment_callback_ip_white_list_with_range(
        web_app_client, load_json, ip, result,
):

    response = await web_app_client.post(
        '/v1/pay/callback',
        headers={
            'X-Forwarded-For-Y': ip,
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data=f'"{load_json("payment_callback_request.json")["as_string"]}"',
    )

    assert response.status == result


@base_database()
async def test_payment_callback_update_order(
        payment_callback_response, web_context, order_uuid, billing_mocks,
):
    await payment_callback_response(200)
    order = await web_context.pg.secondary.fetchrow(
        'select * from orders where uuid = $1;', order_uuid,
    )
    order_items = json.loads(order['items'])
    assert order_items[0]['id'] == 'product_id__1'
    assert order_items[0]['in_pay_count'] == 0
    assert order_items[0]['paid_count'] == 1
    assert order_items[1]['id'] == 'product_id__2'
    assert order_items[1]['in_pay_count'] == 0
    assert order_items[1]['paid_count'] == 1


@base_database()
async def test_payment_callback_update_status_success(
        payment_callback_response,
        web_context,
        payment_transaction_uuid,
        billing_mocks,
):
    await payment_callback_response(200)

    transaction = await web_context.pg.secondary.fetchrow(
        'select * from payment_transactions where uuid = $1;',
        payment_transaction_uuid,
    )

    assert transaction['status'] == TransactionStatus.SUCCESS.value


@base_database()
async def test_payment_callback_update_status_fail(
        web_context, payment_transaction_uuid, web_app_client,
):
    response = await web_app_client.post(
        '/v1/pay/callback',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=f'Notification=MerchantPay&OrderId={payment_transaction_uuid}&'
        f'Success=Fail&ErrCode=ANY_ERROR_CODE',
    )
    assert response.status == 200

    transaction = await web_context.pg.secondary.fetchrow(
        'select * from payment_transactions where uuid = $1;',
        payment_transaction_uuid,
    )

    assert transaction['status'] == TransactionStatus.IN_PROGRESS.value


@base_database()
async def test_payment_callback_update_status_timeout(
        web_context, payment_transaction_uuid, web_app_client,
):
    response = await web_app_client.post(
        '/v1/pay/callback',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=f'Notification=MerchantPay&OrderId={payment_transaction_uuid}&'
        f'Success=Fail&ErrCode=ORDER_TIME_OUT',
    )
    assert response.status == 200

    transaction = await web_context.pg.secondary.fetchrow(
        'select * from payment_transactions where uuid = $1;',
        payment_transaction_uuid,
    )

    assert transaction['status'] == TransactionStatus.ORDER_TIME_OUT.value


@base_database()
async def test_payment_callback_fail(
        web_context, payment_transaction_uuid, web_app_client,
):
    response = await web_app_client.post(
        '/v1/pay/callback',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        data=f'Notification=MerchantPay&OrderId={payment_transaction_uuid}&'
        f'Success=Fail&ErrCode=WRONG_EXPIRE_DATE',
    )
    assert response.status == 200

    transaction = await web_context.pg.secondary.fetchrow(
        'select * from payment_transactions where uuid = $1;',
        payment_transaction_uuid,
    )

    assert transaction['status'] == TransactionStatus.IN_PROGRESS.value


@base_database(
    orders='order_with_noninteger_quantities/orders.sql',
    payment_transactions='order_with_noninteger_quantities/payment_transactions.sql',  # noqa: E501
)
async def test_payment_callback_update_order_with_noninteger_quantities(
        payment_callback_response, web_context, order_uuid, billing_mocks,
):
    await payment_callback_response(200)
    order = await web_context.pg.secondary.fetchrow(
        'select * from orders where uuid = $1;', order_uuid,
    )
    order_items = json.loads(order['items'])
    assert order_items[0]['id'] == 'product_id__1'
    assert order_items[0]['in_pay_count'] == 0
    assert order_items[0]['paid_count'] == 1.5
    assert order_items[1]['id'] == 'product_id__2'
    assert order_items[1]['in_pay_count'] == 0
    assert order_items[1]['paid_count'] == 0.5
    assert order['status'] == 'paid'


@base_database(
    orders='order_with_service_fee/orders.sql',
    payment_transactions='order_with_service_fee/payment_transactions.sql',
)
async def test_payment_callback_update_order_with_service_fee(
        payment_callback_response, web_context, order_uuid, billing_mocks,
):
    await payment_callback_response(200)
