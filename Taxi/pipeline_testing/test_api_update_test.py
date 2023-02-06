async def test_update(web_app_client, load_json):
    test = load_json('test.json')
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200
    assert await response.json() == test

    # update test
    test['name'] = 'new_name'
    response = await web_app_client.put(
        '/v2/test/',
        json=test,
        params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200

    # check if updated
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200
    assert await response.json() == test


async def test_remove_mock_and_check(web_app_client, load_json):
    test = load_json('test.json')
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200
    assert await response.json() == test

    # update test
    del test['output_checks']
    del test['resources_mocks']['pin_stats']
    response = await web_app_client.put(
        '/v2/test/',
        json=test,
        params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200

    # check if updated
    response = await web_app_client.get(
        '/v2/test/', params={'consumer': 'taxi-surge', 'id': 'test_id'},
    )
    assert response.status == 200
    assert await response.json() == test
