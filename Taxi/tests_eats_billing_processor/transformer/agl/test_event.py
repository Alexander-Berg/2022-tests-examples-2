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
      - skip:
          - transaction_date#xget: /event/transaction_date
          - external_payment_id#xget: /event/external_payment_id
          - client#xget: /event/client
          - version#xget: /event/version
          - rule#xget: /event/rule
          - payment#object:
              - amount#xget: /event/payment/amount
              - currency#xget: /event/payment/currency
              - payment_method#xget: /event/payment/payment_method
              - payment_terminal_id#xget: /event/payment/payment_terminal_id
              - product_id#xget: /event/payment/product_id
              - product_type#xget: /event/payment/product_type
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_event(testpoint, transformer_fixtures):
    event = common.billing_event(
        client_info=rules.client_info(client_id='12345'),
        payment=common.payment(
            payment_method='card',
            product_type='product',
            product_id='product__001',
            currency='RUB',
            amount='150',
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
        .insert_input_event(kind='billing_payment', data=event)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == event
