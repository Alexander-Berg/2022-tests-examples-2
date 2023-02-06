async def test_delete(web_app_client, mockserver, load_json):
    response = await web_app_client.get(
        '/v2/test/check/',
        params={'consumer': 'taxi-surge', 'id': 'test_check'},
    )
    assert response.status == 200
    assert await response.json() == {
        'id': 'test_check',
        'name': 'the_check',
        'check': {
            'source_code': (
                'assert(classes.econom.value > 0, "schould be gte 0");'
            ),
        },
    }

    response = await web_app_client.delete(
        '/v2/test/check/',
        params={'consumer': 'taxi-surge', 'id': 'test_check'},
    )
    assert response.status == 200

    # now missing
    response = await web_app_client.get(
        '/v2/test/check/',
        params={'consumer': 'taxi-surge', 'id': 'test_check'},
    )
    assert response.status == 404
