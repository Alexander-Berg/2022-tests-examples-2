async def test_get(web_app_client, load_json):
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200
    assert await response.json() == load_json('test.json')

    # query missing
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'missing_test'},
    )
    assert response.status == 404

    # query wrong consumer
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'lavka-surge', 'id': 'test_id'},
    )
    assert response.status == 404

    # query unexpected consumer
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'market-surge', 'id': 'test_id'},
    )
    assert response.status == 400
