async def test_update(web_app_client, mockserver, load_json):
    mock = {
        'id': 'test_mock',
        'is_prefetched': False,
        'mock': {'mock_body': 'return {total: 10, free: 5}'},
        'name': 'dummy_candidates',
        'resource': 'candidates',
    }
    response = await web_app_client.get(
        '/v2/test/mock/', params={'consumer': 'taxi-surge', 'id': 'test_mock'},
    )
    assert response.status == 200
    assert await response.json() == mock

    # update mock
    mock['mock']['mock_body'] = 'return: {};'
    response = await web_app_client.put(
        '/v2/test/mock/',
        json=mock,
        params={'consumer': 'taxi-surge', 'id': 'test_mock'},
    )
    assert response.status == 200

    # check if updated
    response = await web_app_client.get(
        '/v2/test/mock/', params={'consumer': 'taxi-surge', 'id': 'test_mock'},
    )
    assert response.status == 200
    assert await response.json() == mock
