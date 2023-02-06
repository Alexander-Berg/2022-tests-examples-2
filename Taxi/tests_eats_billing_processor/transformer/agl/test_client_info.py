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
          - place_info#client-info:
                place-id: 'place_1'
                timestamp: '2021-06-22T14:00:00+00:00'
          - courier_info#client-info:
                courier-id: 'courier_1'
                timestamp: '2021-06-22T14:00:00+00:00'
          - picker_info#client-info:
                picker-id: 'picker_1'
                timestamp: '2021-06-22T14:00:00+00:00'
          - place_info_fallback#client-info:
                place-id: 'place_2'
                timestamp: '2021-06-22T14:00:00+00:00'
                fallback#object:
                  - id: client_2
                  - contract_id: test_contract_id
""",
        Loader=yaml.SafeLoader,
    ),
)
async def test_happy_path(testpoint, transformer_fixtures):
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
            client_info=rules.client_info(
                client_id='place_client',
                contract_id='place_contract',
                country_code='RU',
                mvp='place_mvp',
            ),
        )
        .using_business_rules(
            courier_id='courier_1',
            client_info=rules.client_info(
                client_id='courier_client',
                employment='courier_service',
                contract_id='courier_contract',
                country_code='KZ',
                mvp='courier_mvp',
            ),
        )
        .using_business_rules(
            picker_id='picker_1',
            client_info=rules.client_info(
                client_id='picker_client',
                employment='self_employed',
                contract_id='picker_contract',
                country_code='BY',
                mvp='picker_mvp',
            ),
        )
        .insert_input_event(kind='billing_payment', data=payment)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {
        'place_info': {
            'id': 'place_client',
            'contract_id': 'place_contract',
            'country_code': 'RU',
            'mvp': 'place_mvp',
        },
        'courier_info': {
            'id': 'courier_client',
            'employment': 'courier_service',
            'contract_id': 'courier_contract',
            'country_code': 'KZ',
            'mvp': 'courier_mvp',
        },
        'picker_info': {
            'id': 'picker_client',
            'employment': 'self_employed',
            'contract_id': 'picker_contract',
            'country_code': 'BY',
            'mvp': 'picker_mvp',
        },
        'place_info_fallback': {
            'id': 'client_2',
            'contract_id': 'test_contract_id',
        },
    }


@pytest.mark.config(
    EATS_BILLING_PROCESSOR_RULES=yaml.load(
        """
default:
    billing_payment:
      - skip:
          - place_info#client-info:
                place-token: 'place_token'
                timestamp: '2021-06-22T14:00:00+00:00'
          - courier_info#client-info:
                courier-token: 'courier_token'
                timestamp: '2021-06-22T14:00:00+00:00'
          - picker_info#client-info:
                picker-token: 'picker_token'
                timestamp: '2021-06-22T14:00:00+00:00'
          - place_info_fallback#client-info:
                place-token: 'unknow'
                timestamp: '2021-06-22T14:00:00+00:00'
                fallback#object:
                  - id: client_2
                  - contract_id: test_contract_id
""",
        Loader=yaml.SafeLoader,
    ),
)
@pytest.mark.pgsql('eats_billing_processor', files=['test_tokens.sql'])
async def test_tokens(testpoint, transformer_fixtures):
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
            client_info=rules.client_info(
                client_id='place_client',
                contract_id='place_contract',
                country_code='RU',
                mvp='place_mvp',
            ),
        )
        .using_business_rules(
            courier_id='courier_1',
            client_info=rules.client_info(
                client_id='courier_client',
                employment='courier_service',
                contract_id='courier_contract',
                country_code='KZ',
                mvp='courier_mvp',
            ),
        )
        .using_business_rules(
            picker_id='picker_1',
            client_info=rules.client_info(
                client_id='picker_client',
                employment='self_employed',
                contract_id='picker_contract',
                country_code='BY',
                mvp='picker_mvp',
            ),
        )
        .insert_input_event(kind='billing_payment', data=payment)
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )

    assert skip_testpoint.times_called == 1
    assert result == {
        'place_info': {
            'id': '123456',
            'contract_id': 'place_contract',
            'country_code': 'RU',
            'mvp': 'place_mvp',
        },
        'courier_info': {
            'id': '123456',
            'contract_id': 'courier_contract',
            'country_code': 'RU',
            'mvp': 'courier_mvp',
            'employment': 'courier_service',
        },
        'picker_info': {
            'id': '123456',
            'contract_id': 'picker_contract',
            'country_code': 'RU',
            'mvp': 'picker_mvp',
            'employment': 'self_employed',
        },
        'place_info_fallback': {
            'id': 'client_2',
            'contract_id': 'test_contract_id',
        },
    }
