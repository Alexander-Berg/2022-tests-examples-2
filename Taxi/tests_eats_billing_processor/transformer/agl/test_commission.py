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
          - amount1#commission:
                amount: '100'
                parameters:
                    commission: '50'
                    fix_commission: '10'
                    acquiring_commission: '5'
          - amount2#commission:
                amount: '-100'
                parameters:
                    commission: '50'
                    fix_commission: '10'
                    acquiring_commission: '5'
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_commission_operand(testpoint, transformer_fixtures):
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
    assert result['amount1'] == '65'
    assert result['amount2'] == '-65'
