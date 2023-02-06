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
async def test_commission(testpoint, transformer_fixtures):
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
        .using_business_rules(
            picker_id='21',
            client_id='12345',
            commission=rules.make_commission(
                rule_id='commission_1',
                commission_type='picker_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
                    fix_commission='20',
                ),
                billing_frequency='daily',
            ),
        )
        .insert_input_event(kind='billing_payment', data=payment)
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
        'billing_frequency': 'daily',
    }
    assert result['rule2'] is None


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - skip:
          - rule1#load-business-rule:
                counterparty-token: 'place_token'
                commission-type: place_delivery
                timestamp: '2021-06-22T14:00:00+00:00'
""",
        Loader=yaml.SafeLoader,
    ),
)
@pytest.mark.pgsql('eats_billing_processor', files=['test_tokens.sql'])
async def test_token_commission(testpoint, transformer_fixtures):
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
        .using_business_rules(
            place_id='place_1',
            client_id='12345',
            commission=rules.make_commission(
                rule_id='commission_1',
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
                    fix_commission='20',
                ),
            ),
        )
        .insert_input_event(kind='billing_payment', data=payment)
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


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - skip:
          - rule1#load-business-rule:
                timestamp: '2021-06-22T14:00:00+00:00'
                place-id: '1234'
                business-type: restaurant
                fine-reason: return
                delivery-type: native
          - rule2#load-business-rule:
                timestamp: now
                courier-id: 'test'
                business-type: type
                fine-reason: reason
                delivery-type: type
                enabled#boolean: false
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_fine(testpoint, transformer_fixtures):
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
        .using_business_rules(
            place_id='1234',
            client_info=rules.client_info(client_id='1'),
            fine=rules.make_fine(
                rule_id='fine_1',
                business_type='restaurant',
                delivery_type='native',
                reason='return',
                params=rules.simple_fine(
                    application_period=100000,
                    fine='10',
                    fix_fine='10',
                    min_fine='0',
                    max_fine='10000',
                    gmv_limit='0',
                ),
                billing_frequency='daily',
            ),
        )
        .insert_input_event(kind='billing_payment', data=payment)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result['rule1'] == {
        'client_id': '1',
        'rule_id': 'fine_1',
        'fine_params': {
            'application_period': 100000,
            'fine': '10',
            'fix_fine': '10',
            'gmv_limit': '0',
            'max_fine': '10000',
            'min_fine': '0',
        },
        'billing_frequency': 'daily',
    }
    assert result['rule2'] is None


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - skip:
          - rule1#load-business-rule:
                timestamp: '2021-06-22T14:00:00+00:00'
                counterparty-token: 'place_token'
                business-type: restaurant
                fine-reason: return
                delivery-type: native
""",
        Loader=yaml.SafeLoader,
    ),
)
@pytest.mark.pgsql('eats_billing_processor', files=['test_tokens.sql'])
async def test_token_fine(testpoint, transformer_fixtures):
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
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='1'),
            fine=rules.make_fine(
                rule_id='fine_1',
                business_type='restaurant',
                delivery_type='native',
                reason='return',
                params=rules.simple_fine(
                    application_period=100000,
                    fine='10',
                    fix_fine='10',
                    min_fine='0',
                    max_fine='10000',
                    gmv_limit='0',
                ),
            ),
        )
        .insert_input_event(kind='billing_payment', data=payment)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result['rule1'] == {
        'client_id': '1',
        'rule_id': 'fine_1',
        'fine_params': {
            'application_period': 100000,
            'fine': '10',
            'fix_fine': '10',
            'gmv_limit': '0',
            'max_fine': '10000',
            'min_fine': '0',
        },
        'billing_frequency': 'none',
    }
