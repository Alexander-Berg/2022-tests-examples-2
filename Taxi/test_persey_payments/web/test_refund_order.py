import pytest


@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_simple(
        taxi_persey_payments_web,
        mockserver,
        pgsql,
        trust_create_refund_success,
        mock_do_refund,
):
    db = pgsql['persey_payments']

    create_refund_mock = trust_create_refund_success(
        {
            'reason_desc': 'cancel payment',
            'orders': [{'order_id': 'some_order_test', 'delta_amount': '723'}],
            'purchase_token': 'trust-basket-token',
        },
    )
    do_refund_mock = mock_do_refund('wait_for_notification')

    headers = {
        'X-Yandex-Login': 'some_login',
        'X-Idempotency-Token': 'idempotency_token',
    }
    request = {
        'order_id': 'some_order',
        'mark': 'main',
        'ticket': 'TICKET-777',
        'amount': {'test': '723', 'delivery': '0'},
    }

    response = await taxi_persey_payments_web.post(
        '/v1/order/refund', json=request, headers=headers,
    )

    assert response.status == 200
    assert await response.json() == {}

    cursor = db.cursor()
    cursor.execute(
        'SELECT order_id, mark, refund_id, trust_refund_id, '
        'operator_login, ticket '
        'FROM persey_payments.refund ',
    )
    assert list(cursor) == [
        (
            'some_order',
            'main',
            'idempotency_token',
            'trust-refund-id',
            'some_login',
            'TICKET-777',
        ),
    ]
    assert create_refund_mock.times_called == 1
    assert do_refund_mock.times_called == 1
