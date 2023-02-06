from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.grocery import helper


async def test_happy_path_with_product_type_product(transformer_fixtures):
    await (
        helper.TransformerGroceryTest()
        .on_payment_refund(
            counteragent_id=helper.GROCERY_FAKE_CLIENT_ID,
            client_id=helper.GROCERY_FAKE_CLIENT_ID,
            product_type='product',
            amount='200',
        )
        .using_business_rules(
            place_id=helper.GROCERY_CLIENT_ID,
            client_id=helper.GROCERY_CLIENT_ID,
            commission=rules.make_commission(
                commission_type='grocery_product',
                params=rules.simple_commission(
                    commission='2',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id=helper.GROCERY_CLIENT_ID,
                contract_id=helper.GROCERY_CONTRACT_ID,
                refund=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='product',
                    amount='200',
                    product_id='product_grocery',
                ),
            ),
            common.billing_event(
                client_id=helper.GROCERY_CLIENT_ID,
                contract_id=helper.GROCERY_CONTRACT_ID,
                commission=common.make_commission(
                    amount='-4',
                    product_type='product',
                    commission_type='goods',
                    product_id='product_grocery',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_product_type_delivery(transformer_fixtures):
    await (
        helper.TransformerGroceryTest()
        .on_payment_refund(
            counteragent_id=helper.GROCERY_FAKE_CLIENT_ID,
            client_id=helper.GROCERY_FAKE_CLIENT_ID,
            product_type='delivery',
            amount='200',
        )
        .using_business_rules(
            place_id=helper.GROCERY_CLIENT_ID,
            client_id=helper.GROCERY_CLIENT_ID,
            commission=rules.make_commission(
                commission_type='grocery_delivery',
                params=rules.simple_commission(
                    commission='2',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id=helper.GROCERY_CLIENT_ID,
                contract_id=helper.GROCERY_CONTRACT_ID,
                refund=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='delivery',
                    amount='200',
                    product_id='delivery_grocery',
                ),
            ),
            common.billing_event(
                client_id=helper.GROCERY_CLIENT_ID,
                contract_id=helper.GROCERY_CONTRACT_ID,
                commission=common.make_commission(
                    product_type='delivery',
                    amount='-4',
                    commission_type='goods',
                    product_id='delivery_grocery',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_product_type_tips(transformer_fixtures):
    await (
        helper.TransformerGroceryTest()
        .on_payment_refund(
            counteragent_id=helper.GROCERY_FAKE_CLIENT_ID,
            client_id=helper.GROCERY_FAKE_CLIENT_ID,
            product_type='tips',
            amount='200',
        )
        .using_business_rules(
            place_id=helper.GROCERY_CLIENT_ID,
            client_id=helper.GROCERY_CLIENT_ID,
            commission=rules.make_commission(
                commission_type='grocery_product',
                params=rules.simple_commission(
                    commission='2',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id=helper.GROCERY_CLIENT_ID,
                contract_id=helper.GROCERY_CONTRACT_ID,
                refund=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='tips',
                    amount='200',
                    product_id='tips_grocery',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
