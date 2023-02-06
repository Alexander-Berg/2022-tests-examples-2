import pytest

from eats_integration_offline_orders.generated.cron import run_cron
from eats_integration_offline_orders.internal import enums


@pytest.mark.pgsql(
    'eats_integration_offline_orders',
    files=['tables.sql', 'orders.sql', 'payment_transactions.sql'],
)
async def test_send_billing_update_status(
        cron_context, billing_mocks, payment_transaction_uuid,
):

    transaction = await cron_context.queries.payment_transactions.get_by_uuid(
        payment_transaction_uuid,
    )
    assert transaction.status == enums.PaymentTransactionStatus.SUCCESS.value

    await run_cron.main(
        ['eats_integration_offline_orders.crontasks.send_billing', '-t', '0'],
    )

    transaction = await cron_context.queries.payment_transactions.get_by_uuid(
        payment_transaction_uuid,
    )
    assert transaction.status == enums.PaymentTransactionStatus.BILLED.value
