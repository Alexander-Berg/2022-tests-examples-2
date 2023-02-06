from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.inplace import helper


async def test_payment_mercury_discount(load_json, transformer_fixtures):
    await (
        helper.TransformerInplaceTest()
        .with_order_nr('210405-000001')
        .insert_input_event(
            kind='mercury_discount', data=load_json('mercury_discount.json'),
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='qr_pay',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                transaction_date='2021-03-18T12:00:00+00:00',
                client_id='123456',
                payment=common.payment(
                    payment_method='marketing',
                    product_type='inplace',
                    amount='20',
                    product_id='inplace_coupons',
                ),
            ),
            common.billing_event(
                transaction_date='2021-03-18T12:00:00+00:00',
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    amount='3',
                    product_id='inplace_coupons',
                    commission_type='inplace',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )
