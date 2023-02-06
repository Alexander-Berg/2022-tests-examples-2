import json

import pytest

from eats_integration_offline_orders.internal import enums


@pytest.mark.parametrize(
    'transaction_front_uuid, expected_status, is_cancel_succeeded, '
    'expected_transaction_status, transaction_type',
    [
        pytest.param(
            'absent_transaction_uuid',
            404,
            False,
            enums.PaymentTransactionStatus.IN_PROGRESS,
            'sbp',
            id='no transaction found',
        ),
        pytest.param(
            'transaction_front_uuid__3',
            404,
            False,
            enums.PaymentTransactionStatus.SUCCESS,
            'sbp',
            id='not in progress',
        ),
        pytest.param(
            'transaction_front_uuid__2',
            200,
            False,
            enums.PaymentTransactionStatus.CANCELLED_BY_USER,
            'sbp',
            id='rollback - success, cancel in tinkoff - failed',
        ),
        pytest.param(
            'transaction_front_uuid__2',
            200,
            True,
            enums.PaymentTransactionStatus.CANCELLED_BY_USER,
            'sbp',
            id='success sbp',
        ),
        pytest.param(
            'transaction_front_uuid__1',
            200,
            True,
            enums.PaymentTransactionStatus.CANCELLED_BY_USER,
            'payture',
            id='success payture',
        ),
        pytest.param(
            'transaction_front_uuid__4',
            400,
            None,
            enums.PaymentTransactionStatus.IN_PROGRESS,
            'trust_card',
            id='trust payment (unable to unhold)',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'orders.sql', 'payment_transactions.sql'],
)
async def test_unhold_transaction(
        web_app_client,
        web_context,
        mock_tinkoff_securepay,
        mockserver,
        load_json,
        transaction_front_uuid,
        expected_status,
        is_cancel_succeeded,
        expected_transaction_status,
        transaction_type,
):
    @mock_tinkoff_securepay('/v2/Cancel')
    def _mock_cancel(request):
        return mockserver.make_response(
            json=load_json(
                f'tinkoff/response_cancel'
                f'{"" if is_cancel_succeeded else "_fail"}.json',
            ),
        )

    response = await web_app_client.post(
        '/v1/transaction/unhold',
        json={'transaction_uuid': transaction_front_uuid},
    )
    assert response.status == expected_status

    transaction = await web_context.pg.secondary.fetchrow(
        f'SELECT * FROM payment_transactions where '
        f'front_uuid = \'{transaction_front_uuid}\'',
    )

    if not transaction:
        return

    assert transaction
    assert transaction['order_id'] == 1
    assert transaction['payment_type'] == transaction_type
    assert transaction['status'] == expected_transaction_status.value

    order = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM orders LIMIT 1;',
    )
    assert order
    expected_in_pay_count = (
        0
        if expected_transaction_status
        == enums.PaymentTransactionStatus.CANCELLED_BY_USER
        else 1
    )
    transaction_items = json.loads(order['items'])
    assert len(transaction_items) == 2
    assert transaction_items[0]['id'] == 'product_id__1'
    assert transaction_items[0]['in_pay_count'] == expected_in_pay_count
    assert transaction_items[1]['id'] == 'product_id__2'
    assert transaction_items[1]['in_pay_count'] == expected_in_pay_count
