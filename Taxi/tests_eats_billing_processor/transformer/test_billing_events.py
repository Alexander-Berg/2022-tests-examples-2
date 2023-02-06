from tests_eats_billing_processor.transformer import helper


async def test_bypass_by_default(load_json, transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_1.json'),
        )
        .insert_input_event(
            kind='billing_refund', data=load_json('billing_refund_1.json'),
        )
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_2.json'),
        )
        .insert_input_event(
            kind='billing_commission',
            data=load_json('billing_commission_1.json'),
        )
        .expect_billing_events(
            events=[
                load_json('billing_payment_1.json'),
                load_json('billing_refund_1.json'),
                load_json('billing_payment_2.json'),
                load_json('billing_commission_1.json'),
            ],
        )
        .run(transformer_fixtures)
    )


async def test_bypass_rule(load_json, transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='order_created', data={'rules': 'default'})
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_1.json'),
        )
        .insert_input_event(
            kind='billing_refund', data=load_json('billing_refund_1.json'),
        )
        .insert_input_event(
            kind='billing_commission',
            data=load_json('billing_commission_1.json'),
        )
        .expect_stq_call_id(2)
        .expect_billing_events(
            events=[
                load_json('billing_payment_1.json'),
                load_json('billing_refund_1.json'),
                load_json('billing_commission_1.json'),
            ],
        )
        .run(transformer_fixtures)
    )
