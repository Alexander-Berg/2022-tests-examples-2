from eats_integration_offline_orders.components.payture import (
    payload as payture_payload,
)
from test_eats_integration_offline_orders import utils


base_database = utils.BaseDatabase(  # pylint:disable=invalid-name
    restaurants='restaurants.sql',
    tables='tables.sql',
    orders='orders.sql',
    payment_transactions='payment_transactions.sql',
)


@base_database()
async def test_payture_init_payload(  # pylint: disable=W0621
        web_context, payment_transaction_uuid, load_json,
):

    transaction = await web_context.queries.payment_transactions.get_by_uuid(
        payment_transaction_uuid,
    )

    init_payload = payture_payload.InitPayload(
        web_context.config.EI_OFFLINE_ORDERS_PAYTURE_SETTINGS,
        web_context.secdist['payture'],
    )(transaction)

    assert (
        init_payload['Data']
        == load_json('client_init_payload.json')['default']['Data']
    )


@base_database(
    payment_transactions='payment_transactions_with_service_fee.sql',
)
async def test_payture_init_payload_with_service_fee(  # pylint: disable=W0621
        web_context, payment_transaction_uuid, load_json,
):

    transaction = await web_context.queries.payment_transactions.get_by_uuid(
        payment_transaction_uuid,
    )

    init_payload = payture_payload.InitPayload(
        web_context.config.EI_OFFLINE_ORDERS_PAYTURE_SETTINGS,
        web_context.secdist['payture'],
    )(transaction)

    assert (
        init_payload['Data']
        == load_json('client_init_payload.json')['with_service_fee']['Data']
    )


@base_database()
async def test_payture_init_true(  # pylint: disable=W0621
        web_context, payture_mocks, payment_transaction_uuid, load_json,
):

    transaction = await web_context.queries.payment_transactions.get_by_uuid(
        payment_transaction_uuid,
    )

    result = await web_context.payture_client.init(transaction)
    assert result == (True, 'a333582e-ec0b-43ba-a7b9-717c753b38d1')
