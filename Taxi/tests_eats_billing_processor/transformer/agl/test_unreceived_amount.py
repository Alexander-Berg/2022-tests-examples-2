import pytest
import yaml

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_commission:
      - skip:
          - amount1#unreceived-amount:
                product-type: product
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_unreceived_amount(testpoint, transformer_fixtures):
    commission = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        external_payment_id='ext1',
        version='2',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product',
            currency='RUB',
            amount='100',
        ),
    )
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        external_payment_id='payment_1',
        version='2',
        payment=common.payment(
            payment_method='payment_not_received',
            product_type='product',
            product_id='some_product',
            currency='RUB',
            amount='250.55',
            payment_terminal_id='12345-00',
        ),
    )
    refund = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        external_payment_id='payment_1',
        version='2',
        refund=common.refund(
            payment_method='payment_not_received',
            product_type='product',
            product_id='some_product',
            currency='RUB',
            amount='100',
            payment_terminal_id='12345-00',
        ),
    )

    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='billing_payment', data=payment)
        .insert_input_event(kind='billing_refund', data=refund)
        .insert_input_event(kind='billing_commission', data=commission)
        .expect_billing_events(events=[payment, refund])
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {'amount1': '150.55'}


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_commission:
      - skip:
          - amount1#unreceived-amount:
                product-type: product
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_unreceived_amount_weekly(testpoint, transformer_fixtures):
    commission = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        external_payment_id='ext1',
        version='2',
        commission=common.make_commission(
            product_type='product',
            product_id='some_product',
            currency='RUB',
            amount='100',
        ),
    )
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        external_payment_id='payment_1',
        version='2',
        payment=common.payment(
            payment_method='payment_not_received',
            product_type='product_weekly',
            product_id='some_product',
            currency='RUB',
            amount='150.55',
            payment_terminal_id='12345-00',
        ),
    )
    refund = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        external_payment_id='payment_1',
        version='2',
        refund=common.refund(
            payment_method='payment_not_received',
            product_type='product',
            product_id='some_product',
            currency='RUB',
            amount='100',
            payment_terminal_id='12345-00',
        ),
    )

    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='billing_payment', data=payment)
        .insert_input_event(kind='billing_refund', data=refund)
        .insert_input_event(kind='billing_commission', data=commission)
        .expect_billing_events(events=[payment, refund])
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {'amount1': '50.55'}
