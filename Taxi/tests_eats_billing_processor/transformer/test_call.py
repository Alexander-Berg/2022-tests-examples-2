import pytest
import yaml

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    custom_handler:
      - skip:
            - val#string: Data from custom handler
    billing_payment:
      - with:
            event#object:
              - val#string: Data from standard handler
            do:
              - call: custom_handler
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_call_operand(testpoint, transformer_fixtures):
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        payment=common.payment(
            payment_method='card', product_type='product', amount='1500',
        ),
    )
    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=payment)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {'val': 'Data from custom handler'}


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    __init__:
      - skip:
        - val#string: Data from __init__ called handler
restaurant:
    __init__:
      - call: __default__
    billing_payment:
      - with:
          event#object:
          do:
            - skip
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_call_operand1(testpoint, transformer_fixtures):
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        payment=common.payment(
            payment_method='card', product_type='product', amount='1500',
        ),
    )
    result = []

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result.append(data)

    await (
        helper.TransformerTest('restaurant')
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=payment)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 2
    assert result == [{'val': 'Data from __init__ called handler'}, {}]


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    custom_handler:
      - skip:
            - val#string: Data from custom handler
    billing_payment:
      - with:
            event#object:
              - val#string: Data from standard handler
            do:
              - call: custom_handler_misspelled
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_call_operand_fail(testpoint, transformer_fixtures):
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        payment=common.payment(
            payment_method='card', product_type='product', amount='1500',
        ),
    )
    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=payment)
        .no_stq_call_expected()
        .expected_fail()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 0
