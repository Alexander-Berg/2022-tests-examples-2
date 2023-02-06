async def test_delete(web_app_client):
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200

    response = await web_app_client.delete(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200

    # now missing
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 404
