import pytest

from tests_eats_billing_processor.input_processor import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES={
        'grocery': {'payment_received': [{'skip': {}}]},
    },
    EATS_BILLING_PROCESSOR_FEATURES={
        'grocery_rules_enabled': True,
        'create_handler_enabled': True,
    },
)
async def test_feature_enabled_payment_received(input_processor_fixtures):
    data = input_processor_fixtures.load_json('v1/payment_received.json')
    data['client_id'] = helper.GROCERY_CLIENT_ID
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='payment_received/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind='payment_received',
            data=data,
            rule_name='grocery',
        )
        .run(input_processor_fixtures)
    )


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES={
        'grocery': {'payment_refund': [{'skip': {}}]},
    },
    EATS_BILLING_PROCESSOR_FEATURES={
        'grocery_rules_enabled': True,
        'create_handler_enabled': True,
    },
)
async def test_feature_enabled_payment_refund(input_processor_fixtures):
    data = input_processor_fixtures.load_json('v1/payment_refund.json')
    data['client_id'] = helper.GROCERY_CLIENT_ID
    await (
        helper.InputProcessorTest()
        .request(
            order_nr='123456',
            external_id='create/123456',
            event_at='2021-03-18T15:00:00+00:00',
            kind='payment_refund',
            data=data,
            rule_name='grocery',
        )
        .run(input_processor_fixtures)
    )
