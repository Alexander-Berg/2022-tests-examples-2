import pytest

from tests_eats_billing_processor.deal_id import helper


@pytest.mark.parametrize(
    'currency, mvp, client_id, contract_id',
    [
        pytest.param(
            'RUB',
            'MSKc',
            helper.SERVICE_FEE_RUB_CLIENT_ID,
            helper.SERVICE_FEE_RUB_CONTRACT_ID,
        ),
        pytest.param(
            'BYN',
            'MNKc',
            helper.SERVICE_FEE_BYN_CLIENT_ID,
            helper.SERVICE_FEE_BYN_CONTRACT_ID,
        ),
        pytest.param(
            'KZT',
            'AST',
            helper.SERVICE_FEE_KZT_CLIENT_ID,
            helper.SERVICE_FEE_KZT_CONTRACT_ID,
        ),
    ],
)
async def test_happy_path_service_fee(
        deal_id_fixtures, currency, mvp, client_id, contract_id,
):
    await (
        helper.DealIdTest()
        .on_service_fee(
            info=helper.deal_info(
                client_id=client_id, contract_id=contract_id, mvp=mvp,
            ),
            currency=currency,
            place_type='restaurant',
            delivery_type='native',
        )
        .expected_rule_name('restaurant')
        .run(deal_id_fixtures)
    )
