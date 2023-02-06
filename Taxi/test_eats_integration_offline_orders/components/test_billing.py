from test_eats_integration_offline_orders import utils

base_database = utils.BaseDatabase(  # pylint:disable=invalid-name
    restaurants='restaurants.sql',
    tables='tables.sql',
    orders='orders.sql',
    payment_transactions='payment_transactions.sql',
)


@base_database()
async def test_billing_process_default(
        web_context, place_id, payment_transaction_uuid, billing_mocks,
):

    transaction = await web_context.queries.payment_transactions.get_by_uuid(
        payment_transaction_uuid,
    )

    await web_context.billing.process(place_id, transaction)

    assert billing_mocks['for_order'].has_calls
    assert not billing_mocks['for_fee'].has_calls
    assert not billing_mocks['for_ya_discount'].has_calls


@base_database(
    payment_transactions='payment_transactions_with_service_fee.sql',
)
async def test_billing_process_service_fee(
        web_context, place_id, payment_transaction_uuid, billing_mocks,
):
    transaction = await web_context.queries.payment_transactions.get_by_uuid(
        payment_transaction_uuid,
    )

    await web_context.billing.process(place_id, transaction)

    assert billing_mocks['for_order'].has_calls
    assert billing_mocks['for_fee'].has_calls


@base_database(
    payment_transactions='payment_transactions_with_ya_discount.sql',
)
async def test_billing_process_ya_discount(
        web_context, payment_transaction_uuid, billing_mocks,
):
    place_id = '12345'  # billing_processor works only with INTable string
    transaction = await web_context.queries.payment_transactions.get_by_uuid(
        payment_transaction_uuid,
    )

    await web_context.billing.process(place_id, transaction)

    assert billing_mocks['for_order'].has_calls
    assert billing_mocks['for_ya_discount'].has_calls
