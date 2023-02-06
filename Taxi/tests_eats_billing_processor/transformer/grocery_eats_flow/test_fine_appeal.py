import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.grocery_eats_flow import helper


@pytest.mark.pgsql('eats_billing_processor', files=['fine.sql'])
async def test_happy_path_refund(transformer_fixtures):
    await (
        helper.TransformerGroceryEatsFlowTest()
        .with_order_nr('444444')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
            ),
        )
        .on_fine_appeal(
            fine_id='1',
            ticket='EDA-1',
            product_type='product',
            product_id='some_product_id',
            amount='200',
            place_id='place_1',
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                payment=common.payment(
                    product_type='product',
                    product_id='some_product_id',
                    amount='200',
                    payment_method='withholding_correct',
                    payment_service='yaeda',
                ),
            ),
        )
        .expect_accounting(
            client_id='123456', amount='-200.00', account_type='fine',
        )
        .expect_appeal(fine_id='1', ticket='EDA-1', amount='200.00')
        .run(transformer_fixtures)
    )


async def test_happy_path_cancel(transformer_fixtures):
    await (
        helper.TransformerGroceryEatsFlowTest()
        .with_order_nr('444444')
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='product',
                ),
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='100',
                    product_type='delivery',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='native',
                reason='cancellation',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='0',
                ),
            ),
        )
        .on_fine_appeal(
            fine_id='1',
            ticket='EDA-1',
            product_type='product',
            product_id='some_product_id',
            amount='200',
            place_id='place_1',
            fine_reason='cancel',
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='12',
                    commission_type='goods',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='product__002',
                    amount='-12',
                    commission_type='goods',
                ),
            ),
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='12.00',
            calculated_amount='12.00',
        )
        .expect_accounting(
            client_id='123456', amount='200.00', account_type='gmv',
        )
        .expect_appeal(fine_id='1', ticket='EDA-1', amount='200.00')
        .run(transformer_fixtures)
    )
