import pytest

from tests_eats_billing_processor.transformer import helper

OVERRIDDEN_RULES = {
    'default': {
        'billing_payment': [
            {
                'create': [
                    {'transaction_date#xget': '/event/transaction_date'},
                    {'external_payment_id#xget': '/eventexternal_payment_id'},
                    {'client_id#xget': '/event/client_id'},
                ],
            },
        ],
    },
}


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=OVERRIDDEN_RULES)
async def test_billing_payment_incorrect_operator_xget(
        load_json, transformer_fixtures, testpoint,
):
    @testpoint('test_stacktrace')
    def _test_stacktrace(data):
        assert data == ['default', 'billing_payment', '0', 'create']

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='order_created', data={'rules': 'default'})
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_1.json'),
        )
        .expected_fail()
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert _test_stacktrace.times_called == 1


OVERRIDDEN_RULES_1 = {
    'default': {
        'billing_payment': [
            {
                'strategy': [
                    {'transaction_date#xget': '/event/transaction_date'},
                    {'external_payment_id#xget': '/event/external_payment_id'},
                    {'client_id#xget': '/event/client_id'},
                ],
            },
        ],
    },
}


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=OVERRIDDEN_RULES_1)
async def test_billing_payment_no_strategy(
        load_json, transformer_fixtures, testpoint,
):
    @testpoint('test_stacktrace')
    def _test_stacktrace(data):
        assert data == ['default', 'billing_payment', '0']

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='order_created', data={'rules': 'default'})
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_1.json'),
        )
        .expected_fail()
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert _test_stacktrace.times_called == 1


OVERRIDDEN_RULES_2 = {
    'default': {
        'billingpayment': [
            {
                'create': [
                    {'transaction_date#xget': '/event/transaction_date'},
                    {'external_payment_id#xget': '/event/external_payment_id'},
                    {'client_id#xget': '/event/client_id'},
                ],
            },
        ],
    },
}


OVERRIDDEN_RULES_3 = {
    'default': {'billing_payment': [{'for-each': [{'in#map': ''}]}]},
}


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=OVERRIDDEN_RULES_3)
async def test_billing_payment_error_for_each(
        load_json, transformer_fixtures, testpoint,
):
    @testpoint('test_stacktrace')
    def _test_stacktrace(data):
        assert data == ['default', 'billing_payment', '0', 'for-each']

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='order_created', data={'rules': 'default'})
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_1.json'),
        )
        .expected_fail()
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert _test_stacktrace.times_called == 1
