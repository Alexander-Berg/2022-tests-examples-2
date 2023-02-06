async def test_auth_apikey_simple_no_key(taxi_userver_sample):
    response = await taxi_userver_sample.get('auth/apikey/simple')
    assert response.status_code == 400
    assert response.content == b''


async def test_auth_apikey_simple_invalid_key(taxi_userver_sample):
    headers_set = {'X-YaTaxi-API-Key': 'incorrect-apikey'}
    response = await taxi_userver_sample.get(
        'auth/apikey/simple', headers=headers_set,
    )
    assert response.status_code == 403
    assert response.content == b''


async def test_auth_apikey_simple_good_key(taxi_userver_sample):
    headers_set = {'X-YaTaxi-API-Key': 'sample-key-123'}
    response = await taxi_userver_sample.get(
        'auth/apikey/simple', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.content == b''


async def test_auth_apikey_by_method_no_key(taxi_userver_sample):
    response = await taxi_userver_sample.get('auth/apikey/by-method')
    assert response.status_code == 400
    assert response.content == b''


async def test_auth_apikey_by_method_good_key(taxi_userver_sample):
    headers_set = {'X-YaTaxi-API-Key': 'sample-key-321'}
    response = await taxi_userver_sample.get(
        'auth/apikey/by-method', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.content == b''
    headers_set = {'X-YaTaxi-API-Key': 'sample-key-321456'}
    response = await taxi_userver_sample.put(
        'auth/apikey/by-method', headers=headers_set,
    )
    assert response.status_code == 200
    assert response.content == b''


async def test_auth_apikey_by_method_other_method_key(taxi_userver_sample):
    headers_set = {'X-YaTaxi-API-Key': 'sample-key-321456'}
    response = await taxi_userver_sample.get(
        'auth/apikey/by-method', headers=headers_set,
    )
    assert response.status_code == 403
    assert response.content == b''
    headers_set = {'X-YaTaxi-API-Key': 'sample-key-321'}
    response = await taxi_userver_sample.put(
        'auth/apikey/by-method', headers=headers_set,
    )
    assert response.status_code == 403
    assert response.content == b''


async def test_auth_apikey_by_method_missing_method_in_config_no_key(
        taxi_userver_sample,
):
    response = await taxi_userver_sample.delete('auth/apikey/by-method')
    assert response.status_code == 200
    assert response.content == b''
