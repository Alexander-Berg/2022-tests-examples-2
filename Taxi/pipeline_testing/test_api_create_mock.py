async def test_create(web_app_client):
    mock = {
        'id': 'test_mock',
        'name': 'dummy_candidates',
        'is_prefetched': False,
        'resource': 'candidates',
        'mock': {'mock_body': 'return {total: 10, free: 5}'},
    }
    response = await web_app_client.post(
        '/v2/test/mock/', params={'consumer': 'taxi-surge'}, json=mock,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v2/test/mock/', params={'consumer': 'taxi-surge', 'id': 'test_mock'},
    )
    assert response.status == 200
    data = await response.json()

    assert data == {
        'id': 'test_mock',
        'is_prefetched': False,
        'mock': {'mock_body': 'return {total: 10, free: 5}'},
        'name': 'dummy_candidates',
        'resource': 'candidates',
    }

    # create duplicate
    response = await web_app_client.post(
        '/v2/test/mock/', params={'consumer': 'taxi-surge'}, json=mock,
    )
    assert response.status == 400
