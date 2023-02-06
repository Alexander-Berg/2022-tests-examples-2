async def test_delete(web_app_client, mockserver, load_json):
    response = await web_app_client.get(
        '/v2/test/mock/', params={'consumer': 'taxi-surge', 'id': 'test_mock'},
    )
    assert response.status == 200
    assert await response.json() == {
        'id': 'test_mock',
        'is_prefetched': False,
        'mock': {'foo': 'bar'},
        'name': 'dummy_input',
    }

    response = await web_app_client.delete(
        '/v2/test/mock/', params={'consumer': 'taxi-surge', 'id': 'test_mock'},
    )
    assert response.status == 200

    # now missing
    response = await web_app_client.get(
        '/v2/test/mock/', params={'consumer': 'taxi-surge', 'id': 'test_mock'},
    )
    assert response.status == 404
