import pytest


from tests_eats_payments import consts
from tests_eats_payments import db_item_payment_type_plus
from tests_eats_payments import helpers


@pytest.mark.parametrize(
    'kwargs, clear_times_called',
    [
        pytest.param(
            {
                'invoice_id': 'test_order-debt',
                'operation_id': 'create:123456:100500',
                'operation_status': 'done',
                'notification_type': 'operation_finish',
            },
            0,
            id='Transactions callback: create, done',
        ),
        pytest.param(
            {
                'invoice_id': 'test_order-debt',
                'operation_id': 'create:123456:100500',
                'operation_status': 'failed',
                'notification_type': 'operation_finish',
            },
            0,
            id='Transactions callback: create, fail',
        ),
        pytest.param(
            {
                'invoice_id': 'test_order-debt',
                'operation_id': 'update:123456:100500',
                'operation_status': 'done',
                'notification_type': 'operation_finish',
            },
            1,
            id='Transactions callback: update, done',
        ),
        pytest.param(
            {
                'invoice_id': 'test_order-debt',
                'operation_id': 'update:123456:100500',
                'operation_status': 'failed',
                'notification_type': 'operation_finish',
            },
            0,
            id='Transactions callback: update, failed',
        ),
        pytest.param(
            {
                'invoice_id': 'test_order-debt',
                'operation_id': 'update:123456:100500',
                'operation_status': 'done',
                'notification_type': 'transaction_clear',
            },
            0,
            id='Transactions callback: update, done, transaction_clear',
        ),
    ],
)
async def test_transactions_callback(
        stq,
        stq_runner,
        upsert_order,
        upsert_debt_status,
        pgsql,
        mock_transactions_invoice_retrieve,
        mock_order_revision_customer_services_details,
        mock_transactions_invoice_clear,
        kwargs,
        clear_times_called,
):
    upsert_order(
        order_id='test_order', business_type=consts.BUSINESS, api_version=2,
    )

    db_item_payment_type_plus.DBItemPaymentTypePlus(
        pgsql=pgsql,
        item_id='identity_1',
        order_id='test_order',
        payment_type='debt-collector',
        plus_amount='0.00',
        customer_service_type='composition_products',
    ).insert()

    upsert_debt_status(order_id='test_order', debt_status='updated')

    transactions_items = [
        helpers.make_transactions_item(
            item_id='big_mac',
            amount='2.00',
            fiscal_receipt_info={
                'personal_tin_id': 'personal-tin-id',
                'title': 'Big Mac Burger',
                'vat': 'nds_20',
            },
        ),
    ]

    transaction_1 = helpers.make_transaction(
        operation_id='create:123456:100500',
        status='clear_success',
        sum=[{'amount': '2.00', 'item_id': 'composition-products-1'}],
    )

    payment_items_list = [
        helpers.make_transactions_payment_items(
            payment_type='card', items=transactions_items,
        ),
    ]

    mock_transactions_invoice_retrieve(
        id='test_order-debt',
        cleared=payment_items_list,
        transactions=[transaction_1],
        status='cleared',
    )

    customer_services = [
        helpers.make_customer_service(
            customer_service_id='composition-products-1',
            name='big_mac',
            cost_for_customer='2.00',
            currency='RUB',
            customer_service_type='composition_products',
            vat='nds_20',
            trust_product_id='burger',
            place_id='place_1',
            balance_client_id='123456789',
            details={
                'composition_products': [
                    {
                        'id': 'big_mac',
                        'name': 'Big Mac Burger',
                        'cost_for_customer': '2.00',
                        'type': 'product',
                    },
                ],
                'discriminator_type': 'composition_products_details',
            },
        ),
    ]
    mock_order_revision_customer_services_details(
        customer_services=customer_services, expected_revision_id='100500',
    )

    mock_clear = mock_transactions_invoice_clear()

    kwargs['transactions'] = [transaction_1]
    await stq_runner.eats_payments_transactions_callback.call(
        task_id=f'test_order:create:123456:100500:done:transaction_clear',
        kwargs=kwargs,
        exec_tries=0,
    )

    assert mock_clear.times_called == clear_times_called
    assert stq.eda_order_processing_payment_events_callback.times_called == 0
