from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.inplace import helper


async def test_happy_path_payment_refund(transformer_fixtures):
    await (
        helper.TransformerInplaceTest()
        .on_payment_refund(
            counteragent_id=helper.INPLACE_CLIENT_ID,
            client_id=helper.INPLACE_CLIENT_ID,
            product_type='product',
            amount='200',
        )
        .using_business_rules(
            place_id=helper.INPLACE_CLIENT_ID,
            client_info=rules.client_info(client_id=helper.INPLACE_CLIENT_ID),
            commission=rules.make_commission(
                commission_type='qr_pay',
                params=rules.simple_commission(
                    commission='2',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_id=helper.INPLACE_CLIENT_ID,
                refund=common.refund(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='inplace',
                    amount='200',
                    product_id='product/native',
                ),
            ),
            common.billing_event(
                client_id=helper.INPLACE_CLIENT_ID,
                commission=common.make_commission(
                    amount='-4',
                    product_type='product',
                    product_id='product/native',
                    commission_type='inplace',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
