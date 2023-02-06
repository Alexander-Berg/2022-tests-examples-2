from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.retail import helper


async def test_happy_path_with_commission(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_received(
            counteragent_id='counterparty_1',
            client_id='123456',
            product_type='delivery',
            amount='200',
        )
        .using_business_rules(
            courier_id='counterparty_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='courier_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_id='123456',
                commission=common.make_commission(
                    product_type='delivery', amount='50',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_without_commission(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_received(
            counteragent_id='counterparty_2',
            client_id='23456',
            product_type='retail',
            amount='200',
        )
        .using_business_rules(
            picker_id='counterparty_2',
            client_info=rules.client_info(client_id='23456'),
        )
        .expect(
            common.billing_event(
                client_id='23456',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='retail',
                    amount='200',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
