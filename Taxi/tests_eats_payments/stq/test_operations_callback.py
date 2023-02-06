# pylint: disable=import-error
# pylint: disable=too-many-lines

from tests_eats_payments import helpers


async def test_create_operation(
        experiments3,
        stq_runner,
        upsert_order,
        upsert_order_payment,
        insert_operation,
        fetch_operation,
        mock_transactions_invoice_retrieve,
        mock_transactions_invoice_update,
        mock_order_revision_customer_services,
        mock_order_revision_customer_services_details,
):
    experiments3.add_config(**helpers.make_operations_config())

    upsert_order('test_order', api_version=2)
    upsert_order_payment(
        'test_order',
        '27affbc7-de68-4a79-abba-d9bdf48e6e09',
        'card',
        'RUB',
        True,
    )

    insert_operation(
        'test_order', '123456', '123456', 'create', 'in_progress', 1,
    )
    fetch_operation('test_order', '123456')

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products-1',
            name='big_mac',
            cost_for_customer='10.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='burger',
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

    mock_transactions_invoice_retrieve(
        file_to_load='retrieve_invoice_paid_by_personal_wallet.json',
    )

    transactions_items = helpers.make_transactions_payment_items(
        payment_type='card',
        items=[
            helpers.make_transactions_item(
                item_id='composition-products-1', amount='10.00',
            ),
            helpers.make_transactions_item(
                item_id='delivery', amount='3.00', product_id='eda-product-id',
            ),
        ],
    )
    mock_transactions_invoice_update(
        items=[transactions_items], operation_id='create:1:123456', version=2,
    )

    kwargs = {'id': 'test_order:1:1', 'operation_id': 1}
    await stq_runner.eats_payments_operations.call(
        task_id=f'test:1', kwargs=kwargs, exec_tries=0,
    )
