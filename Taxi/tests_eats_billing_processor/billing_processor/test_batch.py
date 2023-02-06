from tests_eats_billing_processor.billing_processor import helper


async def test_batch(billing_processor_fixtures):
    broken_event = billing_processor_fixtures.load_json('billing_payment.json')
    broken_event['payment']['product_id'] = 'invalid id'
    await (
        helper.BillingProcessorTest()
        .for_order_nr('123456-654321')
        .insert_billing_event(
            data=billing_processor_fixtures.load_json('billing_payment.json'),
        )
        .insert_billing_event(data=broken_event)
        .insert_billing_event(
            data=billing_processor_fixtures.load_json('billing_refund.json'),
        )
        .expected_fail()
        .checking_columns('kind')
        .expect_transfers(('payment',))
        .run(billing_processor_fixtures)
    )
