import decimal

import pytest


@pytest.mark.skip('FIX IN PERSEYCORE-402')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
@pytest.mark.parametrize(
    'need_free, create_basket',
    [(False, 'create_basket_simple.json'), (True, 'create_basket_free.json')],
)
@pytest.mark.parametrize('sampling_cost', ['75', None])
@pytest.mark.parametrize(
    'clear_action', ['clear_all', 'clear_delivery', 'cancel_all'],
)
async def test_simple(
        web_app_client,
        mockserver,
        pgsql,
        load_json,
        mock_uuid,
        fill_service_orders_success,
        trust_create_basket_success,
        trust_pay_basket_success,
        trust_clear_init_success,
        mock_trust_check_basket,
        trust_create_refund_success,
        mock_do_refund,
        stq,
        need_free,
        create_basket,
        sampling_cost,
        clear_action,
):
    db = pgsql['persey_payments']

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token/'
        'orders/2104653bdac343e39ac57869d0bd738d/resize/',
    )
    def _trust_resize(request):
        assert request.json == {'amount': '75', 'qty': '1'}
        return {'status': 'success', 'status_code': 'payment_is_updated'}

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token/'
        'orders/2104653bdac343e39ac57869d0bd738d/unhold/',
    )
    def _trust_test_cancel(request):
        return {'status': 'success', 'status_code': 'payment_is_updated'}

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token/'
        'orders/2104653bdac343e39ac57869d0bd738d/clear/',
    )
    def _trust_test_clear(request):
        return {'status': 'success', 'status_code': 'payment_is_updated'}

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token/'
        'orders/26ea1098014144a99b8e2ea3307ab562/clear/',
    )
    def _trust_delivery_clear(request):
        return {'status': 'success', 'status_code': 'payment_is_updated'}

    @mockserver.json_handler(
        '/trust-payments/v2/payments/trust-basket-token/unhold/',
    )
    def _trust_cancel_basket(request):
        return {'status': 'success', 'status_code': 'payment_is_updated'}

    orders_mock = fill_service_orders_success('create_orders_simple.json')
    create_mock = trust_create_basket_success(create_basket)
    start_mock = trust_pay_basket_success('900.893')
    clear_mock = trust_clear_init_success()
    if need_free:
        check_mock = mock_trust_check_basket(
            [
                {'payment_status': 'not_started'},
                {'trust_payment_id': 'tpid', 'payment_status': 'not_started'},
                load_json('check_basket_not_authorized.json'),
                {'payment_status': 'not_started'},
                {'payment_status': 'not_started'},
                {'trust_payment_id': 'tpid', 'payment_status': 'not_started'},
                load_json('check_basket_not_authorized.json'),
                {'payment_status': 'not_started'},
            ],
        )
    else:
        check_mock = mock_trust_check_basket({'payment_status': 'not_started'})
    create_refund_mock = trust_create_refund_success()
    do_refund_mock = mock_do_refund('wait_for_notification')

    request = {'order_id': 'some_order', 'need_free': need_free}

    if not need_free:
        request['payment_method_id'] = 'some_payment_method_id'

    response = await web_app_client.post('/v1/order/create', json=request)

    assert response.status == 200
    assert await response.json() == {}

    cursor = db.cursor()
    cursor.execute(
        'SELECT fund_id FROM persey_payments.basket '
        'WHERE order_id = \'some_order\'',
    )
    assert not list(cursor)

    for index in range(1, 3):
        mock_uuid(2, 0)
        response = await web_app_client.post(
            '/v1/order/hold',
            json={
                'order_id': 'some_order',
                'mark': str(index),
                'user': {
                    'email': 'me@me.com',
                    'phone': '+79157777777',
                    'user_uid': '777',
                },
                'tariff': {
                    'lab_id': 'some_lab',
                    'delivery_cost': '777.77',
                    'test_cost': '123.123',
                    'sampling_cost': sampling_cost,
                },
            },
        )

        assert response.status == 200
        assert await response.json() == {}

        fund_id = 'some_fund' if need_free else None
        cursor = db.cursor()
        cursor.execute(
            'SELECT fund_id, mark, hold_amount, status '
            'FROM persey_payments.basket '
            f'WHERE order_id = \'some_order\' AND mark = \'{index}\'',
        )
        rows = list(cursor)
        assert rows == [
            (fund_id, str(index), decimal.Decimal('900.893'), 'started'),
        ]

        if need_free:
            assert start_mock.times_called == index - 1
            assert create_mock.times_called == 1 + 2 * (index - 1)
        else:
            assert start_mock.times_called == index
            assert create_mock.times_called == index

        mock_uuid(2, 0)
        response = await web_app_client.post(
            '/v1/order/clear',
            json={
                'order_id': 'some_order',
                'mark': str(index),
                'action': clear_action,
            },
        )

        assert response.status == 200
        assert await response.json() == {}

        assert stq.persey_payments_deliver.times_called == index

        if need_free:
            assert orders_mock.times_called == 4 * index
        else:
            assert orders_mock.times_called == 2 * index

        if need_free:
            assert check_mock.times_called == 4 * index
        else:
            assert check_mock.times_called == 2 * index

        if clear_action == 'clear_all':
            if need_free:
                assert clear_mock.times_called == 0
            else:
                assert clear_mock.times_called == index

            assert _trust_resize.times_called == 0
            assert _trust_test_cancel.times_called == 0
            assert _trust_test_clear.times_called == 0
            assert _trust_delivery_clear.times_called == 0
            assert _trust_cancel_basket.times_called == 0
            assert create_refund_mock.times_called == 0
            assert do_refund_mock.times_called == 0
        elif clear_action == 'clear_delivery':
            assert clear_mock.times_called == 0
            assert _trust_cancel_basket.times_called == 0

            if need_free:
                assert create_refund_mock.times_called == index
                assert do_refund_mock.times_called == index
                assert _trust_resize.times_called == 0
                assert _trust_test_clear.times_called == 0
                assert _trust_test_cancel.times_called == 0
                assert _trust_delivery_clear.times_called == 0
            else:
                assert create_refund_mock.times_called == 0
                assert do_refund_mock.times_called == 0
                assert _trust_delivery_clear.times_called == index

                if sampling_cost is None:
                    assert _trust_resize.times_called == 0
                    assert _trust_test_clear.times_called == 0
                    assert _trust_test_cancel.times_called == index
                else:
                    assert _trust_resize.times_called == index
                    assert _trust_test_clear.times_called == index
                    assert _trust_test_cancel.times_called == 0
        elif clear_action == 'cancel_all':
            assert clear_mock.times_called == 0
            assert _trust_resize.times_called == 0
            assert _trust_test_cancel.times_called == 0
            assert _trust_test_clear.times_called == 0
            assert _trust_delivery_clear.times_called == 0

            if need_free:
                assert create_refund_mock.times_called == index
                assert do_refund_mock.times_called == index
                assert _trust_cancel_basket.times_called == 0
            else:
                assert create_refund_mock.times_called == 0
                assert do_refund_mock.times_called == 0
                assert _trust_cancel_basket.times_called == index
        else:
            raise ValueError('Wrong clear action')


@pytest.mark.config(
    PERSEY_PAYMENTS_LAB_SETTINGS={
        'labs': [
            {
                'lab_id': 'some_lab',
                'fiscal_title': {
                    'test': 'test_fiscal_title',
                    'delivery': 'delivery_fiscal_title',
                },
            },
        ],
    },
)
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
async def test_lab_settings(
        web_app_client,
        mockserver,
        pgsql,
        mock_uuid,
        fill_service_orders_success,
        trust_create_basket_success,
        trust_pay_basket_success,
        mock_trust_check_basket,
):
    mock_uuid(2)

    orders_mock = fill_service_orders_success('create_orders_simple.json')
    create_mock = trust_create_basket_success(
        'create_basket_lab_settings.json',
    )
    check_mock = mock_trust_check_basket({'payment_status': 'not_started'})
    start_mock = trust_pay_basket_success('900.893')

    response = await web_app_client.post(
        '/v1/order/create',
        json={
            'order_id': 'some_order',
            'need_free': False,
            'payment_method_id': 'some_pmid',
        },
    )

    assert response.status == 200
    assert await response.json() == {}

    response = await web_app_client.post(
        '/v1/order/hold',
        json={
            'order_id': 'some_order',
            'mark': 'mark',
            'user': {
                'email': 'me@me.com',
                'phone': '+79157777777',
                'user_uid': '777',
            },
            'tariff': {
                'lab_id': 'some_lab',
                'delivery_cost': '777.77',
                'test_cost': '123.123',
            },
        },
    )

    assert response.status == 200
    assert await response.json() == {}

    assert orders_mock.times_called == 2
    assert create_mock.times_called == 1
    assert start_mock.times_called == 1
    assert check_mock.times_called == 1


async def test_hold_not_found(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.post(
        '/v1/order/hold',
        json={
            'order_id': 'nonexistent',
            'mark': '321',
            'user': {
                'email': 'me@me.com',
                'phone': '+79157777777',
                'user_uid': '777',
            },
            'tariff': {
                'lab_id': 'some_lab',
                'delivery_cost': '777.77',
                'test_cost': '123.123',
                'sampling_cost': '777',
            },
        },
    )

    assert response.status == 404
    assert await response.json() == {
        'code': 'ORDER_NOT_FOUND',
        'message': 'No order_id=nonexistent in db',
    }


async def test_clear_not_found(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.post(
        '/v1/order/clear',
        json={'order_id': 'nonexistent', 'mark': '321', 'action': 'clear_all'},
    )

    assert response.status == 404
    assert await response.json() == {
        'code': 'ORDER_NOT_FOUND',
        'message': 'No order_id=nonexistent in db',
    }


async def test_clear_basket_not_found(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.post(
        '/v1/order/create', json={'order_id': 'some_order', 'need_free': True},
    )

    assert response.status == 200
    assert await response.json() == {}

    response = await taxi_persey_payments_web.post(
        '/v1/order/clear',
        json={'order_id': 'some_order', 'mark': '321', 'action': 'clear_all'},
    )

    assert response.status == 404
    assert await response.json() == {
        'code': 'BASKET_NOT_FOUND',
        'message': 'No basket.mark=321 in db',
    }


@pytest.mark.pgsql('persey_payments', files=['bookings.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_FUNDS={
        'operator_uid': 'nonexistent',
        'enable_money_limit': True,
        'funds': [],
    },
)
@pytest.mark.parametrize('rearrange_bookings', ['keep', 'drop'])
async def test_bookings(
        taxi_persey_payments_web,
        testpoint,
        mockserver,
        pgsql,
        fill_service_orders_success,
        trust_create_basket_success,
        trust_pay_basket_success,
        mock_trust_check_basket,
        rearrange_bookings,
):
    db = pgsql['persey_payments']

    def check_db_state():
        cursor = db.cursor()
        cursor.execute(
            'SELECT order_id, mark, fund_id, amount '
            'FROM persey_payments.fund_booking',
        )
        assert list(cursor) == [
            ('some_order', '321', 'another_fund', decimal.Decimal(100)),
        ]

    @testpoint('before_create_success')
    def tp_before_cs_v1(data):
        assert data['fund_id'] == 'another_fund'

        check_db_state()

        return {'inject_failure': True}

    @testpoint('after_create_success')
    def tp_after_cs_v1(data):
        return {'inject_failure': True}

    check_mock = mock_trust_check_basket({'payment_status': 'not_started'})
    orders_mock = fill_service_orders_success(None)
    create_mock = trust_create_basket_success(None)

    request = {
        'order_id': 'some_order',
        'mark': '321',
        'user': {
            'email': 'me@me.com',
            'phone': '+79157777777',
            'user_uid': '777',
        },
        'tariff': {
            'lab_id': 'some_lab',
            'delivery_cost': '77.00',
            'test_cost': '23.00',
            'sampling_cost': '1',
        },
    }

    response = await taxi_persey_payments_web.post(
        '/v1/order/hold', json=request,
    )

    assert response.status == 500
    assert orders_mock.times_called == 2
    assert create_mock.times_called == 1
    assert check_mock.times_called == 0
    assert tp_before_cs_v1.times_called == 1
    assert tp_after_cs_v1.times_called == 0

    cursor = db.cursor()
    cursor.execute('SELECT SUM(hold_amount) FROM persey_payments.basket')
    assert list(cursor) == [(decimal.Decimal(0),)]

    @testpoint('before_create_success')
    def tp_before_cs_v2(data):
        assert data['fund_id'] == 'another_fund'

        check_db_state()

        return {'inject_failure': False}

    response = await taxi_persey_payments_web.post(
        '/v1/order/hold', json=request,
    )

    assert response.status == 500
    assert orders_mock.times_called == 4
    assert create_mock.times_called == 2
    assert check_mock.times_called == 0
    assert tp_before_cs_v2.times_called == 1
    assert tp_after_cs_v1.times_called == 1

    @testpoint('before_start_success')
    def tp_before_ss(data):
        check_db_state()

    @testpoint('after_create_success')
    def tp_after_cs_v2(data):
        return {'inject_failure': False}

    if rearrange_bookings == 'drop':
        cursor = db.cursor()
        cursor.execute('DELETE FROM persey_payments.fund_booking')

    response = await taxi_persey_payments_web.post(
        '/v1/order/hold', json=request,
    )

    assert response.status == 200
    assert orders_mock.times_called == 4
    assert create_mock.times_called == 2
    assert check_mock.times_called == 1
    assert tp_before_cs_v2.times_called == 1
    assert tp_after_cs_v2.times_called == 1
    assert tp_before_ss.times_called == 1

    cursor = db.cursor()
    cursor.execute('SELECT SUM(hold_amount) FROM persey_payments.basket')
    assert list(cursor) == [(decimal.Decimal(100),)]

    cursor = db.cursor()
    cursor.execute('SELECT COUNT(*) FROM persey_payments.fund_booking')
    assert list(cursor) == [(1,)]


@pytest.mark.pgsql('persey_payments', files=['bookings.sql'])
@pytest.mark.config(
    PERSEY_PAYMENTS_FUNDS={
        'operator_uid': 'nonexistent',
        'enable_money_limit': True,
        'funds': [],
    },
)
async def test_funds_empty(taxi_persey_payments_web, pgsql):
    db = pgsql['persey_payments']

    request = {
        'order_id': 'some_order',
        'mark': '321',
        'user': {
            'email': 'me@me.com',
            'phone': '+79157777777',
            'user_uid': '777',
        },
        'tariff': {
            'lab_id': 'some_lab',
            'delivery_cost': '666.00',
            'test_cost': '23.00',
            'sampling_cost': '1',
        },
    }

    response = await taxi_persey_payments_web.post(
        '/v1/order/hold', json=request,
    )

    assert response.status == 400
    assert await response.json() == {
        'code': 'FUNDS_EMPTY',
        'message': 'No money left in funds',
    }

    cursor = db.cursor()
    cursor.execute('SELECT status FROM persey_payments.basket')
    rows = list(cursor)
    assert rows == [('book_failed',)]

    cursor = db.cursor()
    cursor.execute('SELECT amount FROM persey_payments.fund_booking')
    rows = list(cursor)
    assert rows == []

    # now funds have enough money, nevertheless, hold fails to be idempotent
    request = {
        'order_id': 'some_order',
        'mark': '321',
        'user': {
            'email': 'me@me.com',
            'phone': '+79157777777',
            'user_uid': '777',
        },
        'tariff': {
            'lab_id': 'some_lab',
            'delivery_cost': '6.00',
            'test_cost': '23.00',
            'sampling_cost': '1',
        },
    }

    response = await taxi_persey_payments_web.post(
        '/v1/order/hold', json=request,
    )

    assert response.status == 400
    assert await response.json() == {
        'code': 'FUNDS_EMPTY',
        'message': 'No money left in funds',
    }

    cursor = db.cursor()
    cursor.execute('SELECT amount FROM persey_payments.fund_booking')
    rows = list(cursor)
    assert rows == [(decimal.Decimal(29),)]


@pytest.mark.skip('FIX IN PERSEYCORE-402')
@pytest.mark.pgsql('persey_payments', files=['simple.sql'])
@pytest.mark.config(TVM_RULES=[{'src': 'persey-payments', 'dst': 'stq-agent'}])
async def test_not_authorized(
        web_app_client,
        mockserver,
        pgsql,
        mock_uuid,
        fill_service_orders_success,
        trust_create_basket_success,
        trust_pay_basket_success,
        trust_clear_init_success,
        mock_trust_check_basket,
        trust_create_refund_success,
        mock_do_refund,
        stq,
        load_json,
):
    mock_uuid(2)
    db = pgsql['persey_payments']

    orders_mock = fill_service_orders_success('create_orders_simple.json')
    create_mock = trust_create_basket_success('create_basket_free.json')
    start_mock = trust_pay_basket_success('900.893')
    clear_mock = trust_clear_init_success()
    check_mock = mock_trust_check_basket({'payment_status': 'not_started'})

    response = await web_app_client.post(
        '/v1/order/create', json={'order_id': 'some_order', 'need_free': True},
    )

    assert response.status == 200
    assert await response.json() == {}

    cursor = db.cursor()
    cursor.execute(
        'SELECT fund_id FROM persey_payments.basket '
        'WHERE order_id = \'some_order\'',
    )
    assert not list(cursor)

    response = await web_app_client.post(
        '/v1/order/hold',
        json={
            'order_id': 'some_order',
            'mark': '0',
            'user': {
                'email': 'me@me.com',
                'phone': '+79157777777',
                'user_uid': '777',
            },
            'tariff': {
                'lab_id': 'some_lab',
                'delivery_cost': '777.77',
                'test_cost': '123.123',
            },
        },
    )

    assert response.status == 200
    assert await response.json() == {}

    fund_id = 'some_fund'
    cursor = db.cursor()
    cursor.execute(
        'SELECT fund_id, mark, hold_amount, status '
        'FROM persey_payments.basket '
        f'WHERE order_id = \'some_order\' AND mark = \'0\'',
    )
    rows = list(cursor)
    assert rows == [(fund_id, '0', decimal.Decimal('900.893'), 'started')]

    assert orders_mock.times_called == 2
    assert check_mock.times_called == 1
    assert create_mock.times_called == 1
    assert start_mock.times_called == 0

    check_mock = mock_trust_check_basket(
        [
            {'payment_status': 'not_started'},
            {'trust_payment_id': 'tpid', 'payment_status': 'not_started'},
            load_json('check_basket_not_authorized.json'),
        ],
    )
    mock_uuid(2, 0)

    response = await web_app_client.post(
        '/v1/order/clear',
        json={'order_id': 'some_order', 'mark': '0', 'action': 'clear_all'},
    )

    assert response.status == 200
    assert await response.json() == {}

    assert orders_mock.times_called == 4
    assert check_mock.times_called == 3
    assert create_mock.times_called == 2
    assert start_mock.times_called == 1
    assert clear_mock.times_called == 0
    assert stq.persey_payments_deliver.times_called == 1
