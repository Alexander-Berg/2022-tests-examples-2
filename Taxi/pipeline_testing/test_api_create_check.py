async def test_create(web_app_client):
    check = {
        'id': 'test_check',
        'name': 'surge_is_positive',
        'check': {
            'source_code': (
                'assert(classes.econom.value > 0, "schould be gte 0");'
            ),
        },
    }
    response = await web_app_client.post(
        '/v2/test/check/', params={'consumer': 'taxi-surge'}, json=check,
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v2/test/check/',
        params={'consumer': 'taxi-surge', 'id': 'test_check'},
    )
    assert response.status == 200
    data = await response.json()

    assert data == {
        'id': 'test_check',
        'name': 'surge_is_positive',
        'check': {
            'source_code': (
                'assert(classes.econom.value > 0, "schould be gte 0");'
            ),
        },
    }
