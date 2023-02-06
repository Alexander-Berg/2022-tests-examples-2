from tests_eats_billing_processor.transformer import helper


async def test_batch(load_json, transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_1.json'),
        )
        .insert_input_event(
            kind='billing_refund', data=load_json('billing_refund_1.json'),
        )
        .insert_input_event(kind='billing_payment', data={'broken': 'format'})
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_2.json'),
        )
        .expected_fail()
        .expect_billing_events(
            events=[
                load_json('billing_payment_1.json'),
                load_json('billing_refund_1.json'),
            ],
        )
        .run(transformer_fixtures)
    )
