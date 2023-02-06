import pytest


async def test_empty_params(web_app_client):
    response = await web_app_client.get('/v1/contracts', params={})
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['contracts']


async def test_unknown_client(web_app_client):
    response = await web_app_client.get(
        '/v1/contracts', params={'client_id': 'unknown'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['contracts']


@pytest.mark.parametrize(
    ['client_id'], [pytest.param('client_id_2'), pytest.param('client_id_3')],
)
async def test_empty_contracts(web_app_client, client_id):
    response = await web_app_client.get(
        '/v1/contracts', params={'client_id': client_id},
    )
    assert response.status == 200
    response_json = await response.json()
    assert not response_json['contracts']


async def test_base(web_app_client, load_json):
    response = await web_app_client.get(
        '/v1/contracts', params={'client_id': 'client_id_1'},
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['contracts'] == load_json('expected_contracts.json')


async def test_contracts_is_active(web_app_client):
    response = await web_app_client.get(
        '/v1/contracts',
        params={'client_id': 'client_id_1', 'is_active': 'true'},
    )
    assert response.status == 200
    response_json = await response.json()
    contracts_ids = [c['contract_id'] for c in response_json['contracts']]
    assert contracts_ids == [101, 103, 104, 105]


async def test_contracts_by_contract_ids(web_app_client):
    response = await web_app_client.get(
        '/v1/contracts', params={'contract_ids': '101,103'},
    )
    assert response.status == 200
    response_json = await response.json()
    contracts_ids = [c['contract_id'] for c in response_json['contracts']]
    assert contracts_ids == [101, 103]
