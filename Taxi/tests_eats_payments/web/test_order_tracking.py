import pytest

from tests_eats_payments import db_order

URL = '/eats/v1/eats-payments/v1/order/tracking'
TEST_ORDER_ID = 'test_order'

BASE_REQUEST = {'order_id': TEST_ORDER_ID}

PURCHASE_TOKEN = 'c964a582b3b4b3dcd514ab1914a7d2a8'


@pytest.mark.parametrize('invoice_file', ['retrieve_invoice.json'])
async def test_successful_payment(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        invoice_file,
        load_json,
        pgsql,
        upsert_order_payment,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id=TEST_ORDER_ID)
    order.upsert()
    upsert_order_payment(
        order_id=TEST_ORDER_ID,
        payment_id='',
        payment_type='card',
        currency='RUB',
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        file_to_load=invoice_file,
    )
    response = await taxi_eats_payments.post(
        URL, json=BASE_REQUEST, headers={'X-Yandex-Uid': '25211664'},
    )

    assert response.status == 200
    assert invoice_retrieve_mock.times_called == 1
    assert response.json()['order']['order']['order_id'] == TEST_ORDER_ID
    assert response.json()['order']['payment']['status'] == 'done'
    assert response.json()['order']['title'] == 'Done title'
    assert response.json()['order']['description'] == 'Done description'


@pytest.mark.parametrize('invoice_file', ['retrieve_invoice_3ds.json'])
@pytest.mark.config(
    EATS_PAYMENTS_FEATURE_FLAGS={
        'check_trust_for_payment_status': {'description': '', 'enabled': True},
    },
)
async def test_3ds_required(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        mock_trust_payments_get,
        invoice_file,
        load_json,
        pgsql,
        upsert_order_payment,
):
    mock_trust_payments_get(PURCHASE_TOKEN)
    order = db_order.DBOrder(pgsql=pgsql, order_id=TEST_ORDER_ID)
    order.upsert()
    upsert_order_payment(
        order_id=TEST_ORDER_ID,
        payment_id='',
        payment_type='card',
        currency='RUB',
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        file_to_load=invoice_file,
    )
    response = await taxi_eats_payments.post(
        URL, json=BASE_REQUEST, headers={'X-Yandex-Uid': '25211664'},
    )

    assert response.status == 200
    assert invoice_retrieve_mock.times_called == 1
    assert response.json()['order']['order']['order_id'] == TEST_ORDER_ID
    assert response.json()['order']['payment']['status'] == '3ds_required'
    assert (
        response.json()['order']['payment']['payload']['url']
        == 'https://trust.yandex.ru/web/redirect_3ds?'
        'purchase_token=' + PURCHASE_TOKEN
    )
    assert response.json()['order']['title'] == '3ds required title'
    assert (
        response.json()['order']['description'] == '3ds required description'
    )


@pytest.mark.parametrize('invoice_file', ['retrieve_invoice_sbp.json'])
@pytest.mark.config(
    EATS_PAYMENTS_FEATURE_FLAGS={
        'check_trust_for_payment_status': {'description': '', 'enabled': True},
    },
)
async def test_sbp_required(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        mock_trust_payments_get,
        invoice_file,
        load_json,
        pgsql,
        upsert_order_payment,
):
    mock_trust_payments_get(PURCHASE_TOKEN)
    order = db_order.DBOrder(pgsql=pgsql, order_id=TEST_ORDER_ID)
    order.upsert()
    upsert_order_payment(
        order_id=TEST_ORDER_ID,
        payment_id='',
        payment_type='sbp',
        currency='RUB',
    )
    invoice_retrieve_mock = mock_transactions_invoice_retrieve(
        file_to_load=invoice_file,
    )
    response = await taxi_eats_payments.post(
        URL, json=BASE_REQUEST, headers={'X-Yandex-Uid': '25211664'},
    )

    assert response.status == 200
    assert invoice_retrieve_mock.times_called == 1
    assert response.json()['order']['order']['order_id'] == TEST_ORDER_ID
    assert response.json()['order']['payment']['status'] == 'sbp_required'
    assert (
        response.json()['order']['payment']['payload']['url']
        == 'http://payment.sbp.url'
    )
    assert response.json()['order']['title'] == 'sbp required title'
    assert (
        response.json()['order']['description'] == 'sbp required description'
    )


async def test_successful_cash_payment(
        taxi_eats_payments, pgsql, upsert_order_payment,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id=TEST_ORDER_ID)
    order.upsert()
    upsert_order_payment(
        order_id=TEST_ORDER_ID,
        payment_id='cash',
        payment_type='cash',
        currency='RUB',
    )

    response = await taxi_eats_payments.post(
        URL, json=BASE_REQUEST, headers={'X-Yandex-Uid': '25211664'},
    )

    assert response.status == 200
    assert response.json()['order']['order']['order_id'] == TEST_ORDER_ID
    assert response.json()['order']['payment']['status'] == 'done'
    assert response.json()['order']['title'] == 'Cash done title'
    assert response.json()['order']['description'] == 'Cash done description'
