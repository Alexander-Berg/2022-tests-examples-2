async def test_get(web_app_client, mockserver, load_json):
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

    # query missing
    response = await web_app_client.get(
        '/v2/test/check/',
        params={'consumer': 'taxi-surge', 'id': 'missing_check'},
    )
    assert response.status == 404

    # query wrong consumer
    response = await web_app_client.get(
        '/v2/test/check/',
        params={'consumer': 'lavka-surge', 'id': 'test_check'},
    )
    assert response.status == 404

    # query unexpected consumer
    response = await web_app_client.get(
        '/v2/test/mock/',
        params={'consumer': 'market-surge', 'id': 'test_check'},
    )
    assert response.status == 400
