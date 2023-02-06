from tests_eats_billing_processor import rules
from tests_eats_billing_processor.transformer import common
from tests_eats_billing_processor.transformer.donation import helper


async def test_happy_path_with_commission(transformer_fixtures):
    await (
        helper.TransformerDonationTest()
        .on_payment_received(
            counteragent_id='counterparty_1',
            client_id=common.DONATION_CLIENT_ID,
            product_type='donation',
            amount='200',
        )
        .using_business_rules(
            client_id=common.DONATION_CLIENT_ID,
            place_id=common.DONATION_CLIENT_ID,
            commission=rules.make_commission(
                commission_type='donation',
                params=rules.simple_commission(
                    commission='0',
                    acquiring_commission='0',
                    fix_commission='0.01',
                ),
            ),
        )
        .expect(
            common.billing_event(
                client_info=rules.client_info(
                    client_id=common.DONATION_CLIENT_ID,
                    contract_id=common.DONATION_CONTRACT_ID,
                    mvp='MSKc',
                ),
                payment=common.payment(
                    payment_method='card',
                    payment_terminal_id='terminal_1',
                    product_type='donation',
                    amount='200',
                ),
            ),
            common.billing_event(
                client_info=rules.client_info(
                    client_id=common.DONATION_CLIENT_ID,
                    contract_id=common.DONATION_CONTRACT_ID,
                    mvp='MSKc',
                ),
                commission=common.make_commission(
                    product_type='donation', amount='0.01',
                ),
            ),
        )
        .run(transformer_fixtures)
    )
