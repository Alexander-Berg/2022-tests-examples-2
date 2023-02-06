import json

import pytest

from eats_integration_offline_orders.internal import enums


CORRECT_IP = '1.1.1.9'


@pytest.mark.config(
    EATS_INTEGRATION_OFFLINE_ORDERS_SETTINGS={
        'tinkoff_sbp_callback_ip_white_list': ['1.1.1.8/29'],
    },
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'tables.sql',
        'orders.sql',
        'restaurants.sql',
        'payment_transactions.sql',
    ],
)
@pytest.mark.parametrize(
    'request_ip, callback_file_suffix, expected_request_status, '
    'expected_error, expected_transaction_status, expected_in_pay, '
    'expected_paid, transaction_uuid, order_id',
    [
        pytest.param(
            '1.1.1.7',
            'token_failed',
            403,
            'Access denied for 1.1.1.7',
            enums.PaymentTransactionStatus.IN_PROGRESS,
            1,
            0,
            'transaction_uuid__4',
            1,
            id='whitelist check failed',
        ),
        pytest.param(
            CORRECT_IP,
            'token_failed',
            403,
            'Wrong Token',
            enums.PaymentTransactionStatus.IN_PROGRESS,
            1,
            0,
            'transaction_uuid__4',
            1,
            id='token check failed',
        ),
        pytest.param(
            CORRECT_IP,
            'got_no_success',
            200,
            '',
            enums.PaymentTransactionStatus.IN_PROGRESS,
            1,
            0,
            'transaction_uuid__4',
            1,
            id='got not success in request data',
        ),
        pytest.param(
            CORRECT_IP,
            'no_transaction',
            404,
            'Transaction not found',
            None,
            1,
            0,
            'non_existed_uuid',
            1,
            id='transaction not found',
        ),
        pytest.param(
            CORRECT_IP,
            'wrong_amount',
            400,
            'Failed amounts check',
            enums.PaymentTransactionStatus.IN_PROGRESS,
            1,
            0,
            'transaction_uuid__1',
            1,
            id='amount not matches',
        ),
        pytest.param(
            CORRECT_IP,
            'wrong_order',
            400,
            'Failed order check',
            enums.PaymentTransactionStatus.IN_PROGRESS,
            1,
            0,
            'transaction_uuid__1',
            1,
            id='order ids not matches',
        ),
        pytest.param(
            CORRECT_IP,
            'not_confirmed',
            200,
            '',
            enums.PaymentTransactionStatus.IN_PROGRESS,
            1,
            0,
            'transaction_uuid__1',
            1,
            id='got not supported callback status',
        ),
        pytest.param(
            CORRECT_IP,
            'non_progress',
            400,
            'Failed transaction status check',
            enums.PaymentTransactionStatus.FAILED,
            1,
            0,
            'transaction_uuid__3',
            1,
            id='transaction not in progress',
        ),
        pytest.param(
            CORRECT_IP,
            'already_success',
            200,
            '',
            enums.PaymentTransactionStatus.SUCCESS,
            0,
            1,
            'transaction_uuid__5',
            2,
            id='transaction already in success status',
        ),
        pytest.param(
            CORRECT_IP,
            'success',
            200,
            '',
            enums.PaymentTransactionStatus.SUCCESS,
            0,
            1,
            'transaction_uuid__4',
            1,
            id='success',
        ),
    ],
)
async def test_sbp_payment_callback(
        web_app_client,
        web_context,
        load_json,
        request_ip,
        callback_file_suffix,
        expected_request_status,
        expected_error,
        expected_transaction_status,
        expected_in_pay,
        expected_paid,
        transaction_uuid,
        order_id,
):
    response = await web_app_client.post(
        '/v1/sbp/callback',
        headers={'X-Forwarded-For-Y': request_ip},
        json=load_json(f'tinkoff/callback_{callback_file_suffix}.json'),
    )
    order = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM orders where id=$1;', order_id,
    )

    assert response.status == expected_request_status
    if expected_request_status != 200:
        data = await response.json()
        assert data['message'] == expected_error
    if (
            expected_transaction_status
            == enums.PaymentTransactionStatus.SUCCESS
            and order_id == 1
    ):
        assert order['status'] == 'paid'
    else:
        assert order['status'] == 'new'

    order_items = json.loads(order['items'])
    assert order_items[0]['id'] == 'product_id__1'
    assert order_items[0]['in_pay_count'] == expected_in_pay
    assert order_items[0]['paid_count'] == expected_paid
    assert order_items[1]['id'] == 'product_id__2'
    assert order_items[1]['in_pay_count'] == expected_in_pay
    assert order_items[1]['paid_count'] == expected_paid

    if not expected_transaction_status:
        return
    transaction = await web_context.pg.secondary.fetchrow(
        f'SELECT * FROM payment_transactions where uuid=$1;', transaction_uuid,
    )
    assert transaction['status'] == expected_transaction_status.value
