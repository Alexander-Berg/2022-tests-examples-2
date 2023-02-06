async def test_front_storage_list(taxi_corp_auth_client):
    path = '/1.0/client/{client}/front_storage/list'.format(client='client1')
    response = await taxi_corp_auth_client.post(path, json={'keys': ['key1']})
    assert response.status == 200
    front_values = await response.json()

    assert front_values['items'] == [{'key': 'key1', 'value': '{fromdb1}'}]
