import pytest


from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import helper


@pytest.mark.pgsql('eats_billing_processor', files=['test_lock.sql'])
async def test_idempotency(load_json, transformer_fixtures):
    payment = load_json('payment_received.json')
    payment['product_type'] = 'delivery'
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .insert_input_event(kind='payment_received', data=payment)
        .using_business_rules(
            courier_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='15',
                    acquiring_commission='5',
                    fix_commission='10',
                ),
            ),
        )
        .expect_billing_events(
            events=[
                {
                    'client': {
                        'id': '1234',
                        'contract_id': 'test_contract_id',
                    },
                    'external_payment_id': 'payment_1',
                    'payment': {
                        'amount': '150.55',
                        'currency': 'RUB',
                        'payment_method': 'card',
                        'product_id': 'some_product',
                        'product_type': 'delivery',
                    },
                    'transaction_date': '2021-04-05T08:25:00+00:00',
                    'rule': 'default',
                    'version': '2.1',
                },
                {
                    'client': {
                        'id': '1234',
                        'contract_id': 'test_contract_id',
                    },
                    'commission': {
                        'amount': '40.11',
                        'currency': 'RUB',
                        'product_id': 'some_product',
                        'product_type': 'delivery',
                    },
                    'external_payment_id': 'payment_1',
                    'transaction_date': '2021-04-05T09:25:00+00:00',
                    'rule': 'default',
                    'version': '2.1',
                },
            ],
        )
        .expect_stq_call_id(2)
        .run(transformer_fixtures)
    )
