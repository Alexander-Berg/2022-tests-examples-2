async def test_create(web_app_client, load_json):
    test = load_json('test.json')
    response = await web_app_client.post(
        '/v2/test/', params={'consumer': 'taxi-surge'}, json=test,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200
    data = await response.json()

    assert data == test

    # create duplicate
    response = await web_app_client.post(
        '/v2/test/', params={'consumer': 'taxi-surge'}, json=test,
    )
    assert response.status == 400
