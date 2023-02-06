async def test_update(web_app_client, mockserver, load_json):
    check = {
        'id': 'test_check',
        'name': 'the_check',
        'check': {
            'source_code': (
                'assert(classes.econom.value > 0, "schould be gte 0");'
            ),
        },
    }
    response = await web_app_client.get(
        '/v2/test/check/',
        params={'consumer': 'taxi-surge', 'id': 'test_check'},
    )
    assert response.status == 200
    assert await response.json() == check

    # update check
    check['check']['source_code'] = 'return: {};'
    response = await web_app_client.put(
        '/v2/test/check/',
        json=check,
        params={'consumer': 'taxi-surge', 'id': 'test_check'},
    )
    assert response.status == 200

    # check if updated
    response = await web_app_client.get(
        '/v2/test/check/',
        params={'consumer': 'taxi-surge', 'id': 'test_check'},
    )
    assert response.status == 200
    assert await response.json() == check
