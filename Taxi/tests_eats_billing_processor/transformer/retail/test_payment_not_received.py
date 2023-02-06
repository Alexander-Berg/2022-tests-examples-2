import pytest

from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.retail import helper


async def test_happy_path(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_not_received(
            picker_id='picker_1',
            place_id='place_1',
            products=[
                common.make_unpaid_product(
                    amount='200', product_type='assembly',
                ),
                common.make_unpaid_product(
                    amount='300', product_type='retail',
                ),
            ],
        )
        .using_business_rules(
            place_id='picker_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(commission_type='place_delivery'),
        )
        .using_business_rules(
            picker_id='picker_1',
            client_info=rules.client_info(client_id='123456'),
            commission=rules.make_commission(
                commission_type='picker_delivery',
            ),
        )
        .expect(
            common.billing_event(
                client_id='123456',
                payment=common.payment(
                    payment_method='payment_not_received',
                    product_type='retail',
                    amount='300',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


async def test_happy_path_with_payment(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .on_payment_not_received(
            picker_id='picker_2',
            products=[
                common.make_unpaid_product(
                    amount='100', product_type='retail',
                ),
            ],
        )
        .on_payment_received(
            counteragent_id='picker_2',
            client_id='23456',
            product_type='retail',
            amount='200',
        )
        .using_business_rules(
            picker_id='picker_2',
            client_info=rules.client_info(client_id='23456'),
            commission=rules.make_commission(
                commission_type='picker_delivery',
            ),
        )
        .using_business_rules(
            place_id='picker_2',
            client_info=rules.client_info(client_id='23456'),
        )
        .expect(
            common.billing_event(
                client_id='23456',
                payment=common.payment(
                    payment_method='payment_not_received',
                    product_type='retail',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='23456',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='retail',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_id='23456',
                refund=common.refund(
                    payment_method='payment_not_received',
                    payment_terminal_id='terminal_1',
                    product_type='retail',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
        )
        .run(transformer_fixtures)
    )


@pytest.mark.pgsql(
    'eats_billing_processor', files=['payment_not_received.sql'],
)
async def test_refund_event_from_database(transformer_fixtures):
    await (
        helper.TransformerRetailTest()
        .with_order_nr('1234567')
        .on_payment_received(
            counteragent_id='counterparty_3',
            client_id='34567',
            product_type='retail',
            amount='200',
            external_payment_id='unpaid_1',
        )
        .on_payment_received(
            counteragent_id='counterparty_4',
            client_id='45678',
            product_type='retail',
            amount='100',
            external_payment_id='unpaid_1',
        )
        .using_business_rules(
            picker_id='counterparty_3',
            client_info=rules.client_info(client_id='34567'),
            commission=rules.make_commission(commission_type='place_delivery'),
        )
        .using_business_rules(
            picker_id='counterparty_4',
            client_info=rules.client_info(client_id='34567'),
            commission=rules.make_commission(commission_type='place_delivery'),
        )
        .expect(
            common.billing_event(
                client_id='34567',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='retail',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_id='34567',
                external_payment_id='unpaid_1',
                refund=common.refund(
                    payment_method='payment_not_received',
                    payment_terminal_id='terminal_1',
                    product_type='retail',
                    amount='100',
                    payment_service='yaeda',
                ),
            ),
            common.billing_event(
                client_id='34567',
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='retail',
                    amount='100',
                ),
            ),
        )
        .expect_stq_call_id(2)
        .run(transformer_fixtures)
    )
