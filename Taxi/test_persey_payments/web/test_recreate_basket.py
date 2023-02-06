import decimal

import pytest


@pytest.mark.skip('FIX IN PERSEYCORE-402')
@pytest.mark.pgsql('persey_payments', files=['recreate_basket_simple.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_UPDATE_PAYMENT={'attempts': 3, 'timeout-s': -1},
)
@pytest.mark.parametrize(
    'payment_status, refund_times_called',
    [('cleared', 1), ('not_started', 0), ('not_authorized', 0)],
)
@pytest.mark.now('2019-11-11T07:00:00+0')
async def test_simple(
        web_app_client,
        mockserver,
        pgsql,
        mock_trust_check_basket,
        load_json,
        fill_service_orders_success,
        trust_create_basket_success,
        trust_create_refund_success,
        mock_do_refund,
        mock_balance,
        mock_uuid,
        payment_status,
        refund_times_called,
):
    mock_uuid(2, refund_times_called)
    orders_mock = fill_service_orders_success('create_orders_simple.json')
    create_mock = trust_create_basket_success('create_basket_free.json')

    check_response = load_json('check_basket.json')
    check_response['payment_status'] = payment_status
    check_mock = mock_trust_check_basket(
        [
            {'trust_payment_id': 'tpid', 'payment_status': 'not_started'},
            check_response,
        ],
    )
    create_refund_mock = trust_create_refund_success(
        {
            'reason_desc': 'cancel payment',
            'orders': [
                {'order_id': 'some_order_test', 'delta_amount': '321'},
                {'order_id': 'some_order_delivery', 'delta_amount': '123'},
            ],
            'purchase_token': 'trust-basket-token',
        },
    )
    do_refund_mock = mock_do_refund('wait_for_notification')
    balance_mock = mock_balance(
        {'Balance2.UpdatePayment': 'update_payment_simple.xml'},
    )

    response = await web_app_client.post(
        '/v1/basket/recreate',
        json={
            'order_id': 'some_order',
            'mark': 'main',
            'tariff': {'test_cost': '-1', 'delivery_cost': '-2'},
        },
    )

    assert response.status == 200
    assert await response.json() == {}

    assert orders_mock.times_called == 2
    assert create_mock.times_called == 1
    assert check_mock.times_called == 2
    assert create_refund_mock.times_called == refund_times_called
    assert do_refund_mock.times_called == refund_times_called
    assert balance_mock.times_called == refund_times_called

    db = pgsql['persey_payments']
    cursor = db.cursor()
    cursor.execute(
        'SELECT purchase_token, order_id, mark, test_cost, delivery_cost, '
        'sampling_cost, fund_id, trust_payment_id, trust_order_id_test, '
        'trust_order_id_delivery, hold_amount, user_uid, status '
        'FROM persey_payments.basket',
    )
    rows = set(cursor)
    assert rows == {
        (
            'trust-basket-token',
            'some_order',
            'archived_main',
            '321',
            '123',
            None,
            None,
            'trust-payment-id',
            'some_order_test',
            'some_order_delivery',
            decimal.Decimal('777.7000'),
            'some_user_uid',
            'started',
        ),
        (
            'trust-basket-token',
            'some_order',
            'main',
            '-1',
            '-2',
            None,
            None,
            'tpid',
            '2104653bdac343e39ac57869d0bd738d',
            '26ea1098014144a99b8e2ea3307ab562',
            decimal.Decimal('-3.0000'),
            'some_user_uid',
            'started',
        ),
    }


@pytest.mark.pgsql('persey_payments', files=['recreate_basket_simple.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_UPDATE_PAYMENT={'attempts': 3, 'timeout-s': -1},
)
@pytest.mark.now('2019-11-11T07:00:00+0')
async def test_failure(
        taxi_persey_payments_web,
        mockserver,
        pgsql,
        mock_trust_check_basket,
        trust_create_refund_success,
        mock_do_refund,
        mock_balance,
):
    check_mock = mock_trust_check_basket({'payment_status': 'cleared'})
    create_refund_mock = trust_create_refund_success(
        {
            'reason_desc': 'cancel payment',
            'orders': [
                {'order_id': 'some_order_test', 'delta_amount': '321'},
                {'order_id': 'some_order_delivery', 'delta_amount': '123'},
            ],
            'purchase_token': 'trust-basket-token',
        },
    )
    do_refund_mock = mock_do_refund('wait_for_notification')
    balance_mock = mock_balance(
        {'Balance2.UpdatePayment': 'update_payment_failure.xml'},
    )

    response = await taxi_persey_payments_web.post(
        '/v1/basket/recreate',
        json={
            'order_id': 'some_order',
            'mark': 'main',
            'tariff': {'test_cost': '-1', 'delivery_cost': '-2'},
        },
    )

    assert response.status == 500
    assert await response.json() == {
        'code': 'UPDATE_PAYMENT_DT_FAIL',
        'message': 'Failed to update payment dt',
    }

    assert check_mock.times_called == 1
    assert create_refund_mock.times_called == 1
    assert do_refund_mock.times_called == 1
    assert balance_mock.times_called == 3
