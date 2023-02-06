import pytest


@pytest.mark.pgsql('balance-replica', files=['default.sql'])
async def test_by_contract_id_200(taxi_balance_replica):
    response = await taxi_balance_replica.post(
        'v1/personal_accounts/by_contract_id', json={'contract_id': 1},
    )
    assert response.status == 200
    assert response.json() == {
        'accounts': [
            {
                'id': 1,
                'contract_id': 1,
                'service_code': 'AGENT_REWARD',
                'external_id': 'ЛСТ-1',
            },
        ],
    }


async def test_by_contract_id_400(taxi_balance_replica):
    response = await taxi_balance_replica.post(
        'v1/personal_accounts/by_contract_id', json={},
    )
    assert response.status == 400
