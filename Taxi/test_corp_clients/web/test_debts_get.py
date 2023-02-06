async def test_debts(web_app_client):
    response = await web_app_client.get(
        '/v1/debts', params={'contract_id': 101},
    )
    assert response.status == 200
    response_json = await response.json()

    assert response_json['debts'][0]['contract_id'] == 101
