import json
import typing

import pytest

from eats_integration_offline_orders.internal import enums


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'orders.sql'],
)
async def test_order_payment(
        web_app_client, web_context, payture_mocks, table_uuid, order_uuid,
):

    response = await web_app_client.get(
        f'/v1/pay?uuid={table_uuid}&order_uuid={order_uuid}',
    )
    assert response.status == 200
    data = await response.json()

    assert data['redirect_link'] == (
        f'{web_context.payture_client.pay_url}'
        f'?SessionId=a333582e-ec0b-43ba-a7b9-717c753b38d1'
    )
    assert data['transaction_uuid']


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'orders.sql'],
)
async def test_order_payment_create_transaction(
        web_app_client, order_uuid, payture_mocks, web_context, table_uuid,
):
    response = await web_app_client.get(
        f'/v1/pay?uuid={table_uuid}&order_uuid={order_uuid}',
    )
    assert response.status == 200

    transaction = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM payment_transactions LIMIT 1;',
    )
    assert transaction
    assert transaction['order_id'] == 1
    assert transaction['payment_type'] == 'payture'
    assert (
        transaction['status']
        == enums.PaymentTransactionStatus.IN_PROGRESS.value
    )
    transaction_items = json.loads(transaction['order_items'])
    assert len(transaction_items) == 2
    assert transaction_items[0]['id'] == 'product_id__1'
    assert transaction_items[0]['quantity'] == 2
    assert transaction_items[1]['id'] == 'product_id__2'
    assert transaction_items[1]['quantity'] == 1


@pytest.mark.parametrize(
    'receipt_email, receipt_phone, expected_status, is_init_success, '
    'is_get_qr_success, expected_transaction_status',
    [
        pytest.param(
            'some@mail.com',
            None,
            200,
            True,
            True,
            enums.PaymentTransactionStatus.IN_PROGRESS,
            id='success pay',
            marks=pytest.mark.config(
                EATS_INTEGRATION_OFFLINE_ORDERS_TINKOFF_SBP_TERMINAL={
                    'terminal_key': '1605280872049',
                    'minimal_payment_copeck': 1,
                },
            ),
        ),
        pytest.param(
            'some@mail.com',
            None,
            400,
            False,
            False,
            enums.PaymentTransactionStatus.CANCELED,
            id='too small count',
            marks=pytest.mark.config(
                EATS_INTEGRATION_OFFLINE_ORDERS_TINKOFF_SBP_TERMINAL={
                    'terminal_key': '1605280872049',
                    'minimal_payment_copeck': 1000,
                },
            ),
        ),
        pytest.param(
            'some@mail.com',
            None,
            400,
            False,
            False,
            enums.PaymentTransactionStatus.CANCELED,
            id='failed init',
            marks=pytest.mark.config(
                EATS_INTEGRATION_OFFLINE_ORDERS_TINKOFF_SBP_TERMINAL={
                    'terminal_key': '1605280872049',
                    'minimal_payment_copeck': 1,
                },
            ),
        ),
        pytest.param(
            'some@mail.com',
            None,
            400,
            True,
            False,
            enums.PaymentTransactionStatus.CANCELED,
            id='failed get qr',
            marks=pytest.mark.config(
                EATS_INTEGRATION_OFFLINE_ORDERS_TINKOFF_SBP_TERMINAL={
                    'terminal_key': '1605280872049',
                    'minimal_payment_copeck': 1,
                },
            ),
        ),
    ],
)
@pytest.mark.config(
    TVM_RULES=[{'src': 'eats-integration-offline-orders', 'dst': 'personal'}],
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'orders.sql'],
)
async def test_order_payment_sbp(
        web_app_client,
        web_context,
        mock_tinkoff_securepay,
        mockserver,
        load_json,
        order_uuid,
        table_uuid,
        receipt_email,
        receipt_phone,
        expected_status,
        is_init_success,
        is_get_qr_success,
        expected_transaction_status,
):
    def make_phone_id(phone):
        return phone[:-1]

    def make_email_id(email):
        return email.split('@')[0]

    @mock_tinkoff_securepay('/v2/Init')
    def _mock_init(request):
        return mockserver.make_response(
            json=load_json(
                f'tinkoff/response_init'
                f'{"" if is_init_success else "_fail"}.json',
            ),
        )

    @mock_tinkoff_securepay('/v2/GetQr')
    def _mock_get_qr(request):
        return mockserver.make_response(
            json=load_json(
                f'tinkoff/response_getqr'
                f'{"" if is_get_qr_success else "_fail"}.json',
            ),
        )

    @mockserver.json_handler('/personal/v1/phones/store')
    def _mock_phones_store(request):
        assert request.json == {'value': '+' + receipt_phone, 'validate': True}
        return {
            'value': '+' + receipt_phone,
            'id': make_phone_id(receipt_phone),
        }

    @mockserver.json_handler('/personal/v1/emails/store')
    def _store_email(request):
        assert request.json == {'value': receipt_email, 'validate': True}
        return {'id': make_email_id(receipt_email), 'value': receipt_email}

    params = {'uuid': table_uuid, 'order_uuid': order_uuid, 'pay_type': 'sbp'}
    if receipt_email:
        params['receipt_email'] = receipt_email
    if receipt_phone:
        params['receipt_phone'] = receipt_phone
    response = await web_app_client.get(
        f'/v1/pay?'
        + '&'.join(f'{key}={value}' for key, value in params.items()),
    )
    assert response.status == expected_status

    transaction = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM payment_transactions LIMIT 1;',
    )
    assert transaction
    assert transaction['order_id'] == 1
    assert transaction['place_id'] == 'place_id__1'
    if is_get_qr_success:
        assert transaction['side_payment_id'] == '1204138470'
    assert transaction['payment_type'] == 'sbp'
    if is_get_qr_success and receipt_email:
        assert transaction['receipt_email_id'] == make_email_id(receipt_email)
    elif not receipt_email:
        assert not transaction['receipt_email_id']
    if is_get_qr_success and receipt_phone:
        assert transaction['receipt_phone_id'] == make_phone_id(receipt_phone)
    elif not receipt_phone:
        assert not transaction['receipt_phone_id']
    assert transaction['status'] == expected_transaction_status.value
    transaction_items = json.loads(transaction['order_items'])
    assert len(transaction_items) == 2
    assert transaction_items[0]['id'] == 'product_id__1'
    assert transaction_items[0]['quantity'] == 2
    assert transaction_items[1]['id'] == 'product_id__2'
    assert transaction_items[1]['quantity'] == 1


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'orders.sql'],
)
async def test_order_payment_mark_as_in_pay(
        web_app_client, order_uuid, payture_mocks, web_context, table_uuid,
):

    response = await web_app_client.get(
        f'/v1/pay?uuid={table_uuid}&order_uuid={order_uuid}',
    )
    assert response.status == 200

    order = await web_context.pg.secondary.fetchrow(
        'SELECT * FROM orders WHERE uuid = $1;', order_uuid,
    )
    order_items = json.loads(order['items'])
    assert order_items[0]['id'] == 'product_id__1'
    assert order_items[0]['in_pay_count'] == 2
    assert order_items[1]['id'] == 'product_id__2'
    assert order_items[1]['in_pay_count'] == 1


@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['tables.sql', 'orders.sql'],
)
async def test_order_payment_rollback_if_payture_fail(
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

    response = await web_app_client.get(
        f'/v1/pay?uuid={table_uuid}&order_uuid={order_uuid}',
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


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'orders_with_noninteger_quantities.sql'],
)
async def test_order_payment_with_noninteger_quantities(
        web_app_client, web_context, payture_mocks, table_uuid, order_uuid,
):

    response = await web_app_client.get(
        f'/v1/pay?uuid={table_uuid}&order_uuid={order_uuid}',
    )
    assert response.status == 200
    data = await response.json()

    assert data['redirect_link'] == (
        f'{web_context.payture_client.pay_url}'
        f'?SessionId=a333582e-ec0b-43ba-a7b9-717c753b38d1'
    )
    assert data['transaction_uuid']


def _make_params(
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
    'params,expected_status,expected_response,',
    [
        pytest.param(_make_params(), 200, None, id='success'),
        pytest.param(
            _make_params(
                pay_type='badge', pay_method_id='badge:yandex_badge:RUB',
            ),
            200,
            None,
            id='success (badge)',
        ),
        pytest.param(
            _make_params(pay_method_id=None),
            403,
            {'message': 'payment method trust_card is not available'},
            id='without pay_method_id for card',
        ),
        pytest.param(
            _make_params(pay_type='applepay', pay_method_id=None),
            403,
            {'message': 'payment method applepay is not available'},
            id='non available payment type',
        ),
    ],
)
async def test_order_payment_trust(
        web_app_client,
        web_context,
        table_uuid,
        order_uuid,
        mock_epma_v1_payment_methods_availability,
        stq,
        # params:
        params,
        expected_status,
        expected_response,
):
    response = await web_app_client.get(
        f'/v1/pay',
        headers={
            'X-Eats-User': 'personal_phone_id=test_personal_phone_id',
            'X-Yandex-Uid': 'test_yandex_uid',
        },
        params={'uuid': table_uuid, 'order_uuid': order_uuid, **params},
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


async def test_order_payment_cash(taxi_eats_integration_offline_orders_web):
    response = await taxi_eats_integration_offline_orders_web.get(
        f'/v1/pay',
        params={'uuid': 'uuid', 'order_uuid': 'uuid', 'pay_type': 'cash'},
    )
    assert response.status == 400
    body = await response.json()
    assert body == {'message': 'cash is not available in this handler'}
