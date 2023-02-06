import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer import helper


@pytest.mark.pgsql(
    'eats_billing_processor', files=['payment_not_received_result.sql'],
)
async def test_payment_not_received_with_payment(
        load_json, transformer_fixtures,
):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .using_business_rules(
            place_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
                billing_frequency='weekly',
            ),
        )
        .on_payment_received(
            counteragent_id='4321',
            client_id=1234,
            product_type='product',
            amount='150.55',
            external_payment_id='payment_1',
            currency='RUB',
            flow_type='native',
        )
        .expect(
            common.billing_event(
                client_id='1234',
                external_payment_id='payment_1',
                payment=common.payment(
                    payment_method='card',
                    product_type='product_weekly',
                    amount='150.55',
                    payment_terminal_id='terminal_1',
                    product_id='product/native_weekly',
                ),
            ),
            common.billing_event(
                client_id='1234',
                external_payment_id='payment_1',
                refund=common.refund(
                    payment_method='payment_not_received',
                    product_type='product_weekly',
                    amount='150.55',
                    payment_service='yaeda',
                    payment_terminal_id='terminal_1',
                    product_id='product/native_weekly',
                ),
            ),
        )
        .expect_stq_call_id(2)
        .run(transformer_fixtures)
    )


async def test_payment_not_received(transformer_fixtures):
    await (
        helper.TransformerTest()
        .with_order_nr('210405-000001')
        .using_business_rules(
            place_id='4321',
            client_info=rules.client_info(client_id='1234'),
            commission=rules.make_commission(
                commission_type='place_delivery',
                params=rules.simple_commission(
                    commission='10',
                    acquiring_commission='0',
                    fix_commission='10',
                ),
                billing_frequency='weekly',
            ),
        )
        .on_payment_not_received(
            products=[
                common.make_unpaid_product(
                    amount='200', product_type='delivery',
                ),
            ],
            place_id='4321',
            order_type='marketplace',
            flow_type='shop',
            external_payment_id='payment_1',
        )
        .expect(
            common.billing_event(
                client_id='1234',
                external_payment_id='payment_1',
                payment=common.payment(
                    payment_method='payment_not_received',
                    product_type='delivery_weekly',
                    amount='200',
                    payment_service='yaeda',
                    product_id='delivery/native_weekly',
                ),
            ),
        )
        .expect_stq_call_id(1)
        .run(transformer_fixtures)
    )
