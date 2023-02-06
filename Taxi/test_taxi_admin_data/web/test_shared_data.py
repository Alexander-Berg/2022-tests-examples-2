async def test_empty(taxi_admin_data_web):
    # test against empty database
    response = await taxi_admin_data_web.get(
        '/v1/shared/data/', params={'key': 'John'},
    )
    assert response.status == 404


async def test_put(taxi_admin_data_web):
    # Put one object and ensure it is visible through API
    response = await taxi_admin_data_web.put(
        '/v1/shared/data/', params={'key': 'John'}, json={'value': 'Smith'},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'key': 'John', 'value': 'Smith'}

    response = await taxi_admin_data_web.get(
        '/v1/shared/data/', params={'key': 'John'},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'key': 'John', 'value': 'Smith'}


async def test_bulk(taxi_admin_data_web):
    # Test bulk handler

    response = await taxi_admin_data_web.put(
        '/v1/shared/data/', params={'key': 'John'}, json={'value': 'Smith'},
    )
    assert response.status == 200

    response = await taxi_admin_data_web.put(
        '/v1/shared/data/', params={'key': 'John2'}, json={'value': 'Smith2'},
    )
    assert response.status == 200

    response = await taxi_admin_data_web.post(
        '/v1/shared/data/list/', json={'keys': ['John', 'John2']},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {
        'data': [
            {'key': 'John', 'value': 'Smith'},
            {'key': 'John2', 'value': 'Smith2'},
        ],
    }

    response = await taxi_admin_data_web.post(
        '/v1/shared/data/list/', json={'keys': ['John1']},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'data': []}


async def test_edit(taxi_admin_data_web):
    response = await taxi_admin_data_web.put(
        '/v1/shared/data/', params={'key': 'John'}, json={'value': 'Smith'},
    )
    assert response.status == 200

    # Edit one object and ensure it is visible through API

    response = await taxi_admin_data_web.put(
        '/v1/shared/data/', params={'key': 'John'}, json={'value': 'Snow'},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'key': 'John', 'value': 'Snow'}

    response = await taxi_admin_data_web.get(
        '/v1/shared/data/', params={'key': 'John'},
    )
    assert response.status == 200

    content = await response.json()
    assert content == {'key': 'John', 'value': 'Snow'}

    # Delete object and ensure it is gone

    response = await taxi_admin_data_web.delete(
        '/v1/shared/data/', params={'key': 'John'},
    )
    assert response.status == 200

    response = await taxi_admin_data_web.delete(
        '/v1/shared/data/', params={'key': 'John'},
    )
    assert response.status == 404

    response = await taxi_admin_data_web.get(
        '/v1/shared/data/', params={'key': 'John'},
    )
    assert response.status == 404
