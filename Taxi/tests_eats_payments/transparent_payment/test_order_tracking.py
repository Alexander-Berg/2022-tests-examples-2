import pytest

from tests_eats_payments import db_order

URL = '/eats/v1/eats-payments/v1/order/tracking'
TEST_ORDER_ID = 'test_order'

BASE_REQUEST = {'order_id': TEST_ORDER_ID}


# pylint: disable=invalid-name
def make_transparent_payment_screen_config(load_json) -> dict:
    cfg = load_json('transparent_payment_screen.json')
    return cfg


@pytest.mark.parametrize('invoice_file', ['retrieve_invoice.json'])
async def test_base(
        taxi_eats_payments,
        mock_transactions_invoice_retrieve,
        invoice_file,
        load_json,
        pgsql,
        upsert_order_payment,
        experiments3,
):
    order = db_order.DBOrder(
        pgsql=pgsql, order_id=TEST_ORDER_ID, is_transparent_payment=True,
    )
    order.upsert()
    upsert_order_payment(
        order_id=TEST_ORDER_ID,
        payment_id='',
        payment_type='card',
        currency='RUB',
    )

    experiments3.add_config(
        **make_transparent_payment_screen_config(load_json),
    )

    mock_transactions_invoice_retrieve(file_to_load=invoice_file)
    response = await taxi_eats_payments.post(
        URL, json=BASE_REQUEST, headers={'X-Yandex-Uid': '25211664'},
    )

    assert response.status == 200

    # print(make_transparent_payment_config(load_json))
    # print(make_transparent_payment_screen_config(load_json))
