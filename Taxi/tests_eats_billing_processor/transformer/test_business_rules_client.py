import pytest
import yaml

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import helper


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - skip:
          - rule1#load-business-rule:
                counterparty-id: '21'
                commission-type: picker_delivery
                timestamp: '2021-06-22T14:00:00+00:00'
          - rule2#load-business-rule:
                counterparty-id: 'all'
                commission-type: requisitions
                timestamp: today
                enabled#boolean: false
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_load_business_rule_commission(
        load_json, testpoint, transformer_fixtures,
):
    result = {}

    @testpoint('skip_event')
    def skip_testpoint(data):
        nonlocal result
        result = data

    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(
            kind='billing_payment', data=load_json('billing_payment_1.json'),
        )
        .using_business_rules(
            picker_id='21',
            client_info=rules.client_info(client_id='12345'),
            commission=rules.make_commission(
                rule_id='commission_1',
                commission_type='picker_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
                    fix_commission='20',
                ),
            ),
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result['rule1'] == {
        'client_id': '12345',
        'rule_id': 'commission_1',
        'commission_params': {
            'acquiring_commission': '5',
            'commission': '10',
            'fix_commission': '20',
        },
        'billing_frequency': 'none',
    }
    assert result['rule2'] is None
