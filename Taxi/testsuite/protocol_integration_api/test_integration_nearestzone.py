def test_simple(taxi_integration, load_json):

    """
    All tests are in protocol's nearestzone!
    As at the curent time int-api's nearestzone is protocols's nearestzone
    (just a proxy in fastcgi)
    """
    request = {'point': [37.54360088427136, 55.645922677413886]}

    response = taxi_integration.post(
        'v1/nearestzone', request, headers={'Accept-Language': 'ru'},
    )

    assert response.status_code == 200

    assert response.json() == {'nearest_zone': 'moscow'}
