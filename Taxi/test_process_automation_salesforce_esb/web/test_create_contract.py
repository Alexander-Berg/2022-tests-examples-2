import json

import pytest

ROUTE = '/v1/billing/contract/create'


@pytest.fixture
def create_contract_mock(request, patch):
    @patch('taxi.clients.billing_v2.BalanceClient.create_common_contract')
    async def _create_contract(*args, **kwargs):
        return {'ID': '12321312', 'EXTERNAL_ID': '333333'}


@pytest.mark.servicetest
@pytest.mark.usefixtures('create_contract_mock')
async def test_create_contract(web_app_client):
    data = {
        'operator_uid': '793360492',
        'params': {'client_id': 88394285, 'partner_commission_sum': 0.1},
    }
    response = await web_app_client.post(ROUTE, data=json.dumps(data))

    assert response.status == 200
    content = await response.json()
    assert content == {'ID': '12321312', 'EXTERNAL_ID': '333333'}
