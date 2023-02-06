# import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.pickup_alco_booking import helper


async def test_happy_path_one_event(transformer_fixtures):
    await (
        helper.TransformerPickupAlcoBookingTest()
        .on_order_gmv(place_id='place_1', gmv_amount='200')
        .using_business_rules(
            place_id='place_1',
            client_info=rules.client_info(client_id='123456'),
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
                    amount='40',
                    commission_type='alco_booking',
                ),
            ),
        )
        .expect_accounting(
            account_type='gmv', client_id='123456', amount='200.00',
        )
        .run(transformer_fixtures)
    )
