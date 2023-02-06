async def test_save(taxi_admin_data_web):
    headers = {'X-Yandex-Login': 'user1'}
    # test against empty database
    response = await taxi_admin_data_web.get(
        '/v1/private/data/', params={'key': 'John'}, headers=headers,
    )
    assert response.status == 404

    # Put one object and ensure it is visible through API
    response = await taxi_admin_data_web.put(
        '/v1/private/data/',
        params={'key': 'John'},
        json={'value': 'Smith'},
        headers=headers,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'key': 'John', 'value': 'Smith'}

    response = await taxi_admin_data_web.put(
        '/v1/private/data/',
        params={'key': 'John2'},
        json={'value': 'Smith2'},
        headers=headers,
    )
    assert response.status == 200

    response = await taxi_admin_data_web.get(
        '/v1/private/data/', params={'key': 'John'}, headers=headers,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'key': 'John', 'value': 'Smith'}

    # Edit one object and ensure it is visible through API

    response = await taxi_admin_data_web.put(
        '/v1/private/data/',
        params={'key': 'John'},
        json={'value': 'Snow'},
        headers=headers,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'key': 'John', 'value': 'Snow'}

    response = await taxi_admin_data_web.get(
        '/v1/private/data/', params={'key': 'John'}, headers=headers,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'key': 'John', 'value': 'Snow'}

    # Test bulk handler

    response = await taxi_admin_data_web.post(
        '/v1/private/data/list/',
        json={'keys': ['John', 'John2']},
        headers=headers,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        'data': [
            {'key': 'John', 'value': 'Snow'},
            {'key': 'John2', 'value': 'Smith2'},
        ],
    }

    response = await taxi_admin_data_web.post(
        '/v1/private/data/list/', json={'keys': ['John1']}, headers=headers,
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'data': []}

    # Delete object and ensure it is gone

    response = await taxi_admin_data_web.delete(
        '/v1/private/data/', params={'key': 'John'}, headers=headers,
    )
    assert response.status == 200

    response = await taxi_admin_data_web.delete(
        '/v1/private/data/', params={'key': 'John'}, headers=headers,
    )
    assert response.status == 404

    response = await taxi_admin_data_web.get(
        '/v1/private/data/', params={'key': 'John'}, headers=headers,
    )
    assert response.status == 404
