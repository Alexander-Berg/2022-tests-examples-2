import pytest

CONTRACT_ID = 123456
COLLATERAL_TYPE = 'common'


@pytest.mark.parametrize(
    ['passport_mock', 'status_code'],
    [pytest.param('client1', 200), pytest.param('unknown_client', 401)],
    indirect=['passport_mock'],
)
async def test_create_collateral(
        passport_mock,
        taxi_corp_real_auth_client,
        status_code,
        mock_corp_requests,
        pd_patch,
):
    response = await taxi_corp_real_auth_client.post(
        f'/1.0/client/{passport_mock}/collaterals/create',
        json={'contract_id': CONTRACT_ID, 'collateral_type': COLLATERAL_TYPE},
    )
    assert response.status == status_code
