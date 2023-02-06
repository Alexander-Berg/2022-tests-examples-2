import pytest


from tests_eats_billing_processor.billing_processor import helper


@pytest.mark.pgsql('eats_billing_processor', files=['test_lock.sql'])
async def test_idempotency(billing_processor_fixtures):
    await (
        helper.BillingProcessorTest()
        .for_order_nr('210405-000001')
        .insert_billing_event(
            data=billing_processor_fixtures.load_json('billing_payment.json'),
        )
        .checking_columns('kind')
        .expect_transfers(('payment',), ('payment',))
        .run(billing_processor_fixtures)
    )
