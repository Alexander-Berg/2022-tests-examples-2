# pylint: disable=C5521
from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.grocery_eats_flow import helper
from tests_eats_billing_processor.transformer.helper import PLUS_CLIENT_ID


async def test_payment_update_plus_cashback(transformer_fixtures):
    await (
        helper.TransformerGroceryEatsFlowTest()
        .with_order_nr('123456-grocery')
        .on_payment_update_plus_cashback(
            client_id='89012',
            amount='100',
            payment_method='card',
            product_type='product',
            product_id='plus_cashback',
            currency='RUB',
            payload={'place_id': '1'},
        )
        .using_business_rules(
            place_id='1',
            client_info=rules.client_info(client_id='89012'),
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
                client_id='89012',
                contract_id='test_contract_id',
                payment=common.payment(
                    payment_method='card',
                    product_type='product',
                    amount='100',
                    payment_service='yaeda',
                    product_id='plus_cashback',
                ),
            ),
            common.billing_event(
                client_id=PLUS_CLIENT_ID,
                contract_id='1',
                payload={
                    'product_type': 'product',
                    'amount': '100',
                    'cashback_service': 'eda',
                    'has_plus': 'true',
                    'order_id': '123456-grocery',
                    'service_id': '645',
                    'country_code': 'RU',
                },
                payment=common.payment(
                    payment_method='yandex_account_withdraw',
                    product_type='delivery',
                    product_id='plus_cashback',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
