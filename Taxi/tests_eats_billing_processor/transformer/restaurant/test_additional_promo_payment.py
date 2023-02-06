from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.restaurant import helper


async def test_happy_path(transformer_fixtures):
    await (
        helper.TransformerRestaurantTest()
        .on_additional_promo_payment(amount='50', place_id='place_1')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='50',
                    product_id='product__002',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_update(transformer_fixtures):
    await (
        helper.TransformerRestaurantTest()
        .on_additional_promo_payment(amount='50', place_id='place_1')
        .on_additional_promo_payment(amount='100', place_id='place_1')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='50',
                    product_id='product__002',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                refund=common.refund(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='50',
                    product_id='product__002',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='100',
                    product_id='product__002',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_delivered_and_update(transformer_fixtures):
    await (
        helper.TransformerRestaurantTest()
        .on_order_delivered(
            place_id='place_1',
            products=[
                common.make_marketing_payment(
                    marketing_type='marketing',
                    amount='25',
                    product_type='product',
                ),
            ],
        )
        .on_additional_promo_payment(amount='50', place_id='place_1')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='10',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='25',
                    product_id='product/native',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                refund=common.refund(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='25',
                    product_id='product__002',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    payment_method='marketing',
                    payment_service='yaeda',
                    product_type='product',
                    amount='50',
                    product_id='product__002',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
