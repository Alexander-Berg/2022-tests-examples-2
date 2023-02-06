async def test_get(web_app_client, mockserver, load_json):
    response = await web_app_client.get(
        '/v2/test/mock/', params={'consumer': 'taxi-surge', 'id': 'id_0'},
    )
    assert response.status == 200
    assert await response.json() == {
        'id': 'id_0',
        'is_prefetched': False,
        'mock': {'mock_body': 'return {total: 10, free: 5}'},
        'name': 'dummy_candidates',
        'resource': 'candidates',
    }

    response = await web_app_client.get(
        '/v2/test/mock/', params={'consumer': 'taxi-surge', 'id': 'id_1'},
    )
    assert response.status == 200
    assert await response.json() == {
        'id': 'id_1',
        'is_prefetched': False,
        'mock': {'foo': 'bar'},
        'name': 'dummy_input',
    }

    # query missing
    response = await web_app_client.get(
        '/v2/test/mock/',
        params={'consumer': 'taxi-surge', 'id': 'missing_mock'},
    )
    assert response.status == 404

    # query wrong consumer
    response = await web_app_client.get(
        '/v2/test/mock/',
        params={'consumer': 'lavka-surge', 'id': 'test_mock'},
    )
    assert response.status == 404

    # query unexpected consumer
    response = await web_app_client.get(
        '/v2/test/mock/',
        params={'consumer': 'market-surge', 'id': 'test_mock'},
    )
    assert response.status == 400
