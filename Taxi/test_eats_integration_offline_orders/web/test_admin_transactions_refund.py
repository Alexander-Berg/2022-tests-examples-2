import json

import pytest

from eats_integration_offline_orders.internal import enums


@pytest.mark.parametrize(
    'transaction_uuid, expected_code, expected_response, is_cancel_succeeded, '
    'expected_transaction_status, expected_order_paid_counters, '
    'expected_trust_refund_counter',
    [
        pytest.param(
            'transaction_uuid__1',
            200,
            {},
            True,
            enums.PaymentTransactionStatus.REFUNDED.value,
            {'product_id__1': 0, 'product_id__2': 0},
            0,
            id='sbp refunded not closed order',
        ),
        pytest.param(
            'transaction_uuid__2',
            200,
            {},
            True,
            enums.PaymentTransactionStatus.REFUNDED.value,
            {'product_id__1': 1, 'product_id__2': 1},
            0,
            id='sbp refunded closed order',
        ),
        pytest.param(
            'transaction_uuid__None',
            404,
            {
                'code': 'not_found',
                'message': 'transaction not found: transaction_uuid__None',
            },
            True,
            None,
            {},
            0,
            id='sbp refunded closed order',
        ),
        pytest.param(
            'transaction_uuid__1',
            400,
            {
                'code': 'refund_failed',
                'message': (
                    'Tinkoff cancel payment failed | 4 | '
                    'Запрашиваемое состояние транзакции является '
                    'неверным. | Изменение статуса не разрешено.'
                ),
            },
            False,
            enums.PaymentTransactionStatus.SUCCESS.value,
            {'product_id__1': 1, 'product_id__2': 1},
            0,
            id='sbp not refunded(400 from sbp) not closed order',
        ),
        pytest.param(
            'transaction_uuid__3',
            400,
            {
                'code': 'refund_failed',
                'message': (
                    'Transaction transaction_uuid__3 in status in_progress'
                ),
            },
            False,
            enums.PaymentTransactionStatus.IN_PROGRESS.value,
            {'product_id__1': 1, 'product_id__2': 1},
            0,
            id='sbp not refunded(transaction in progress) not closed order',
        ),
        pytest.param(
            'transaction_uuid__4',
            200,
            {},
            True,
            enums.PaymentTransactionStatus.REFUNDED.value,
            {'product_id__1': 0, 'product_id__2': 0},
            0,
            id='payture refunded not closed order',
        ),
        pytest.param(
            'transaction_uuid__5',
            200,
            {},
            True,
            enums.PaymentTransactionStatus.REFUNDED.value,
            {'product_id__1': 1, 'product_id__2': 1},
            0,
            id='payture refunded closed order',
        ),
        pytest.param(
            'transaction_uuid__6',
            200,
            {},
            True,
            enums.PaymentTransactionStatus.REFUNDED.value,
            {'product_id__1': 0, 'product_id__2': 0},
            1,
            id='payture refunded not closed order',
        ),
        pytest.param(
            'transaction_uuid__7',
            200,
            {},
            True,
            enums.PaymentTransactionStatus.REFUNDED.value,
            {'product_id__1': 1, 'product_id__2': 1},
            1,
            id='payture refunded closed order',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=[
        'restaurants.sql',
        'tables.sql',
        'orders.sql',
        'payment_transactions.sql',
    ],
)
async def test_admin_tables_delete(
        web_app_client,
        pgsql,
        mock_eats_payments_py3,
        web_context,
        mock_tinkoff_securepay,
        mockserver,
        load_json,
        transaction_uuid,
        expected_code,
        expected_response,
        is_cancel_succeeded,
        expected_transaction_status,
        expected_order_paid_counters,
        expected_trust_refund_counter,
):
    @mock_tinkoff_securepay('/v2/Cancel')
    def _mock_cancel(request):
        return mockserver.make_response(
            json=load_json(
                f'tinkoff/response_cancel'
                f'{"" if is_cancel_succeeded else "_fail"}.json',
            ),
        )

    @mock_eats_payments_py3('/v1/orders/retrieve')
    async def _mock_v1_orders_retrieve(request):
        return {
            'id': '',
            'currency': '',
            'status': 'holding',
            'version': 3,
            'sum_to_pay': [],
            'held': [],
            'cleared': [],
            'debt': [],
            'yandex_uid': '',
            'payment_types': [],
            'payments': [],
        }

    trust_refund_counter = 0

    @mock_eats_payments_py3('/v1/orders/refund')
    async def _mock_v1_orders_refund(request):
        assert request.json['version'] == 3
        nonlocal trust_refund_counter
        trust_refund_counter += 1
        return {}

    response = await web_app_client.post(
        '/admin/v1/transactions/refund',
        json={'transaction_uuid': transaction_uuid},
    )
    body = await response.json()
    assert response.status == expected_code
    assert body == expected_response
    if expected_code == 404:
        return
    db_result = await web_context.pg.secondary.fetchrow(
        'SELECT pt.status, o.items '
        'FROM payment_transactions as pt '
        'LEFT JOIN orders as o on o.id=pt.order_id '
        'where pt.uuid=$1;',
        transaction_uuid,
    )
    assert expected_transaction_status == db_result['status']
    paid_orders_items = {
        item['id']: item['paid_count']
        for item in json.loads(db_result['items'])
    }
    assert paid_orders_items == expected_order_paid_counters
    assert trust_refund_counter == expected_trust_refund_counter
