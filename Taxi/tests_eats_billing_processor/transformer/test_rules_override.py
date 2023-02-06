import pytest

from tests_eats_billing_processor.transformer import helper


OVERRIDDEN_RULES = {
    'retail': {
        'billing_payment': [
            {
                'create': [
                    {'client#object': [{'id#xget': '/event/client/id'}]},
                    {'external_payment_id#xget': '/event/external_payment_id'},
                    {'refund#xget': '/event/payment'},
                    {'transaction_date#xget': '/event/transaction_date'},
                ],
            },
        ],
    },
}


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=OVERRIDDEN_RULES)
async def test_rules_override(load_json, transformer_fixtures):
    input_data = load_json('billing_payment_1.json')
    result = load_json('billing_payment_1.json')
    result['refund'] = result.pop('payment')
    result['rule'] = 'retail'
    await (
        helper.TransformerTest('retail')
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=input_data)
        .expect_billing_events(events=[result])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


OVERRIDDEN_RULES_DEFAULT = {
    'default': {
        'billing_payment': [
            {
                'create': [
                    {'client#object': [{'id#xget': '/event/client/id'}]},
                    {'external_payment_id#xget': '/event/external_payment_id'},
                    {'refund#xget': '/event/payment'},
                    {'transaction_date#xget': '/event/transaction_date'},
                ],
            },
        ],
    },
}


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=OVERRIDDEN_RULES_DEFAULT)
async def test_rules_override_non_default(load_json, transformer_fixtures):
    input_data = load_json('billing_payment_1.json')
    result = load_json('billing_payment_1.json')
    result['refund'] = result.pop('payment')
    result['rule'] = 'restaurant'
    await (
        helper.TransformerTest('restaurant')
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=input_data)
        .expect_billing_events(events=[result])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )
