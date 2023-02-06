def test_simple(taxi_integration):

    """
    All tests are in protocol's zonaltariffdescription!
    As at the curent time int-api's zonaltariffdescription
    is protocols's zonaltariffdescription
    (just a proxy in fastcgi)
    """
    request = {
        'supported': ['call_center', 'category_type'],
        'zone_name': 'moscow',
        'id': 'moscow',
    }

    response = taxi_integration.post(
        'v1/zonaltariffdescription',
        request,
        headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data['max_tariffs']) > 0
    assert data['layout'] == 'tight'
    assert len(data['max_tariffs'][0]['intervals']) > 0
    assert data['paid_cancel_enabled'] is True
