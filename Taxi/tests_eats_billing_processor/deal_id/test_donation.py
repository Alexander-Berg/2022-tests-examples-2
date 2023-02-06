from tests_eats_billing_processor.deal_id import helper


async def test_happy_path_donation(deal_id_fixtures):
    await (
        helper.DealIdTest()
        .on_donation(
            currency='RUB',
            info=helper.deal_info(
                client_id=helper.DONATION_CLIENT_ID,
                contract_id=helper.DONATION_CONTRACT_ID,
                mvp='MSKc',
            ),
        )
        .expected_rule_name('donation')
        .run(deal_id_fixtures)
    )
