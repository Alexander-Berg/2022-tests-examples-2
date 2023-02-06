import copy

import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


OVERRIDDEN_RULES = {'default': {'billing_payment': [{'update': None}]}}


@pytest.mark.config(EATS_BILLING_PROCESSOR_RULES=OVERRIDDEN_RULES)
async def test_update_race(load_json, transformer_fixtures):
    input_data_1 = load_json('billing_payment_1.json')
    input_data_2 = copy.deepcopy(input_data_1)
    input_data_2['payment']['amount'] = '1600'
    result_1 = load_json('billing_payment_1.json')
    result_2 = copy.deepcopy(result_1)
    result_2['refund'] = result_2.pop('payment')
    result_3 = input_data_2
    await (
        helper.TransformerTest()
        .with_order_nr('555555')
        .insert_input_event(kind='billing_payment', data=input_data_1)
        .insert_input_event(
            kind='billing_payment', data=input_data_2, status='complete',
        )
        .insert_billing_event(
            input_event_id=1, data=result_1, external_id='1/0',
        )
        .insert_billing_event(
            input_event_id=2, data=result_2, external_id='2/0',
        )
        .insert_billing_event(
            input_event_id=2, data=result_3, external_id='2/1',
        )
        .expect_billing_events(events=[result_1, result_2, result_3])
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )


async def test_update_with_lazy_load(transformer_fixtures):
    await (
        helper.TransformerTest()
        .on_plus_cashback_emission(
            client_id='123456',
            amount='200',
            plus_cashback_amount_per_place='100',
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(commission_type='place_delivery'),
        )
        .expect(
            common.billing_event(
                client_id=helper.PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
    await (
        helper.TransformerTest()
        .on_payment_refund(
            counteragent_id='place_1',
            client_id='123456',
            product_type='product',
            amount='300',
            flow_type='native',
        )
        .on_plus_cashback_emission(
            client_id='123456',
            amount='100',
            plus_cashback_amount_per_place='50',
            payload={'place_id': 'place_1', 'cashback_service': 'eda'},
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id=helper.PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='100',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id='123456',
                refund=common.refund(
                    payment_method='card',
                    product_type='product',
                    amount='300',
                    payment_terminal_id='terminal_1',
                ),
            ),
            common.billing_event(
                client_id=helper.PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                refund=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='200',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id=helper.PLUS_CLIENT_ID,
                contract_id='1',
                payload={'place_id': 'place_1', 'cashback_service': 'eda'},
                payment=common.payment(
                    payment_method='yandex_account_topup',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='-100',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery',
                    amount='50',
                    product_id='plus_cashback_default',
                    commission_type='plus_cashback',
                ),
            ),
        )
        .expect_stq_call_id(call_id=2)
        .run(transformer_fixtures)
    )
