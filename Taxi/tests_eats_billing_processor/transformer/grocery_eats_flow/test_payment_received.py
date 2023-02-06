from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.grocery_eats_flow import helper


async def test_happy_path_product_type_product(transformer_fixtures):
    await (
        helper.TransformerGroceryEatsFlowTest()
        .on_payment_received(
            counteragent_id='1234',
            client_id='1234',
            product_type='product',
            amount='200',
            flow_type='native',
        )
        .using_business_rules(
            place_id='1234',
            client_info=rules.client_info(client_id='1234'),
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
                client_id='1234',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='product',
                    amount='200',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_product_type_delivery(transformer_fixtures):
    await (
        helper.TransformerGroceryEatsFlowTest()
        .on_payment_received(
            counteragent_id='1234',
            client_id='1234',
            product_type='delivery',
            amount='200',
        )
        .using_business_rules(
            courier_id='1234',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='2',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id='1234',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_id='1234',
                commission=common.make_commission(
                    product_type='delivery', amount='4',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_product_type_tips(transformer_fixtures):
    await (
        helper.TransformerGroceryEatsFlowTest()
        .on_payment_received(
            counteragent_id='1234',
            client_id='1234',
            product_type='tips',
            amount='200',
        )
        .using_business_rules(
            courier_id='1234',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='2',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id='1234',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='tips',
                    amount='200',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
