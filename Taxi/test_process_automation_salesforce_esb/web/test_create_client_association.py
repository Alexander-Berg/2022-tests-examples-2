import json


import pytest


@pytest.fixture
def create_client_association_mock(request, patch):
    @patch(
        'taxi.clients.billing_v2.BalanceClient.create_user_client_association',
    )
    async def _create_client(*args, **kwargs):
        return 0, 'Success'


@pytest.mark.servicetest
@pytest.mark.usefixtures('create_client_association_mock')
async def test_create_client_association(web_app_client):
    data = {
        'operator_uid': '793360492',
        'params': {'client_id': 123, 'user_uid': '456'},
    }
    response = await web_app_client.post(
        '/v1/billing/client/create-association', data=json.dumps(data),
    )

    assert response.status == 200
    content = await response.json()
    assert content == {'code': 0, 'message': 'Success'}
