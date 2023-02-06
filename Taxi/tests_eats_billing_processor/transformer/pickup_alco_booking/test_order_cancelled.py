# import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.pickup_alco_booking import helper


async def test_happy_path_one_event(transformer_fixtures):
    await (
        helper.TransformerPickupAlcoBookingTest()
        .on_order_cancelled(
            is_place_fault=True,
            place_id='place_1',
            products=[
                common.make_reimbursement_payment(
                    payment_type='our_refund',
                    amount='200',
                    product_type='product',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='pickup',
                reason='cancellation',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
            commission=rules.make_commission(
                commission_type='pickup',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
                    fix_commission='10',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(client_id='123456'),
                commission=common.make_commission(
                    product_type='product',
                    product_id='pickup_alco_booking',
                    amount='14',
                    commission_type='alco_booking',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='123456', amount='200.00',
        )
        .expect_fine(
            client_id='123456',
            fine_reason='cancel',
            actual_amount='14.00',
            calculated_amount='14.00',
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_one_event_no_fault(transformer_fixtures):
    await (
        helper.TransformerPickupAlcoBookingTest()
        .on_order_cancelled(
            is_place_fault=False,
            is_reimbursement_required=False,
            place_id='place_1',
            products=[
                common.make_reimbursement_payment(
                    payment_type='incorrect_type',
                    amount='200',
                    product_type='incorrect_product',
                ),
            ],
        )
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
            fine=rules.make_fine(
                business_type='restaurant',
                delivery_type='pickup',
                reason='cancellation',
                params=rules.simple_fine(fine='10', fix_fine='10'),
            ),
            commission=rules.make_commission(
                commission_type='pickup',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='5',
                    fix_commission='10',
                ),
            ),
        )
        .no_stq_call_expected()
        .run(transformer_fixtures)
    )
