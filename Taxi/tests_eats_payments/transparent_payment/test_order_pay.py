import pytest

from tests_eats_payments import db_order
from tests_eats_payments import helpers

URL = '/eats/v1/eats-payments/v1/order/pay'
TEST_ORDER_ID = 'test_order'

BASE_REQUEST = {'order_id': TEST_ORDER_ID}


@pytest.mark.parametrize('invoice_file', ['retrieve_invoice.json'])
@pytest.mark.parametrize(
    'init_retry_count, expected_retry_count',
    [pytest.param(None, 1), pytest.param(1, 2)],
)
async def test_base(
        taxi_eats_payments,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        insert_operation,
        invoice_file,
        load_json,
        pgsql,
        assert_db_order_payment,
        upsert_order_payment,
        experiments3,
        init_retry_count,
        expected_retry_count,
):
    order = db_order.DBOrder(pgsql=pgsql, order_id=TEST_ORDER_ID)
    order.upsert()
    upsert_order_payment(
        order_id=TEST_ORDER_ID,
        payment_id='',
        payment_type='card',
        currency='RUB',
        retry_count=init_retry_count,
    )

    insert_operation(
        TEST_ORDER_ID, '123456', '123456', 'create', 'in_progress', 0,
    )

    mock_transactions_invoice_retrieve(file_to_load=invoice_file)

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products-1',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='composition_products',
            place_id='place_1',
            balance_client_id='123456789',
            details=helpers.make_customer_service_details(
                composition_products=[
                    helpers.make_composition_product(
                        composition_product_id='burger',
                        name='Product 1',
                        cost_for_customer='10.00',
                        composition_product_type='product',
                        vat='nds_20',
                    ),
                ],
            ),
        ),
        helpers.make_customer_service(
            customer_service_id='delivery',
            name='Delivery',
            cost_for_customer='3.00',
            currency='RUB',
            customer_service_type='delivery',
            vat='nds_20',
            trust_product_id='eda-product-id',
            place_id='place_1',
            balance_client_id='987654321',
        ),
    ]
    mock_order_revision_customer_services(customer_services=customer_services)
    mock_order_revision_customer_services_details(
        customer_services=customer_services,
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(
                item_id='composition-products-1',
                amount='10.00',
                product_id='composition_products',
            ),
            helpers.make_transactions_item(
                item_id='delivery', amount='3.00', product_id='eda-product-id',
            ),
        ],
    )
    mock_transactions_invoice_update(
        operation_id=f'create:0:tp_{expected_retry_count}:123456',
        items=[transactions_items],
    )

    response = await taxi_eats_payments.post(
        URL, json=BASE_REQUEST, headers={'X-Yandex-Uid': '25211664'},
    )

    assert_db_order_payment(
        TEST_ORDER_ID, '', 'card', expected_retry_count=expected_retry_count,
    )

    assert response.status == 200
