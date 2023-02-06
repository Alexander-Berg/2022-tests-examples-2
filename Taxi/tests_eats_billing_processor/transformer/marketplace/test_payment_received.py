from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.marketplace import helper


async def test_payment_received_fuelfood(transformer_fixtures):
    await (
        helper.TransformerMarketplaceTest()
        .on_payment_received(
            counteragent_id='place_1',
            client_id='12345',
            product_type='product',
            amount='200',
            order_type='marketplace',
            flow_type='fuelfood',
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='12345'),
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
                client_id='12345',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='product',
                    amount='200',
                    product_id='product/native',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
