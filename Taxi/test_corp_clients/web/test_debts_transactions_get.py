import pytest


@pytest.mark.parametrize(
    ['contract_id'], [pytest.param(101), pytest.param(102)],
)
async def test_debts_transactions(web_app_client, contract_id):
    response = await web_app_client.get(
        '/v1/debts/transactions', params={'contract_id': contract_id},
    )
    assert response.status == 200
    response_json = await response.json()

    if len(response_json['debt_transactions']) > 1:
        assert (
            response_json['debt_transactions'][0]['created']
            > response_json['debt_transactions'][1]['created']
        )
