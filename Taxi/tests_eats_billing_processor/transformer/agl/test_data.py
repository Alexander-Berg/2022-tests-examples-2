import pytest
import yaml

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - using:
            test#object:
              - some_string: bla
              - some_number: 100
            not_evaluated#error: This will never happen
      - skip:
          - data#xget: /data/test
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_data(testpoint, transformer_fixtures):
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            currency='RUB',
            amount='1500',
            payment_terminal_id='553344',
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
    assert result == {'data': {'some_string': 'bla', 'some_number': 100}}


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - with:
            event#string: outer
            do:
              - using:
                    test#xget: /event
              - with:
                    event#string: inner
                    do:
                      - skip:
                         - data#xget: /data/test
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_data_nested(testpoint, transformer_fixtures):
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            currency='RUB',
            amount='1500',
            payment_terminal_id='553344',
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
    assert result == {'data': 'outer'}


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - with:
            event#string: outer
            do:
              - using:
                    test#xget: /event
              - with:
                    event#string: inner
                    do:
                      - using:
                            test#xget: /event
                      - skip:
                         - data#xget: /data/test
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_data_override_inner(load_json, testpoint, transformer_fixtures):
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            currency='RUB',
            amount='1500',
            payment_terminal_id='553344',
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
    assert result == {'data': 'inner'}


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - with:
            event#string: outer
            do:
              - using:
                    test#xget: /event
              - with:
                    event#string: inner
                    do:
                      - using:
                            test#xget: /event
              - skip:
                 - data#xget: /data/test
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_data_override_outer(testpoint, transformer_fixtures):
    payment = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            currency='RUB',
            amount='1500',
            payment_terminal_id='553344',
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
    assert result == {'data': 'outer'}
