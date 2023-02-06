# pylint: disable=C5521
from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.grocery_eats_flow import helper
from tests_eats_billing_processor.transformer.helper import PLUS_CLIENT_ID


async def test_plus_cashback_emission(transformer_fixtures):
    await (
        helper.TransformerGroceryEatsFlowTest()
        .with_order_nr('123456-grocery')
        .on_plus_cashback_emission(
            client_id='123456',
            amount='200',
            plus_cashback_amount_per_place='100',
            payload={'payload': 'test'},
        )
        .using_business_rules(
            place_id='place_1',
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='2',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={'payload': 'test'},
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
                contract_id='1',
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
