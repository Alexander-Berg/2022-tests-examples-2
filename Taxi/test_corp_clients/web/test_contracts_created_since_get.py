async def test_created_since(web_app_client, load_json):
    response = await web_app_client.get(
        '/v1/contracts/created-since',
        params={'created_since': '2020-11-01 14:00:00'},
    )
    assert response.status == 200

    expected_contracts = load_json('expected_contracts.json')
    response_json = await response.json()

    assert response_json['contracts'] == expected_contracts
