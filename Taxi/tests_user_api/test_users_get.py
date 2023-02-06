import pytest


@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_get_simple(taxi_user_api):
    response = await taxi_user_api.post(
        'users/get', json={'id': '8fa869dd9e684cbe945f7a73df621e25'},
    )
    assert response.status_code == 200
    _check_response(response.json(), [])


@pytest.mark.now('2019-02-01T14:00:00Z')
async def test_get_uber(taxi_user_api):
    response = await taxi_user_api.post(
        'users/get',
        json={
            'id': '00148347-c7b9-4058-88a8-4b44f7a2477c',
            'lookup_uber': True,
        },
    )
    assert response.status_code == 200
    _check_response(response.json(), [])


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'fields_request, fields_response',
    [
        ([], ['id']),
        (['_id'], ['id']),
        (['id'], ['id']),
        (['unknown'], ['id']),
        (['application', 'yandex_uuuid', 'unknown'], ['id', 'application']),
        (['yandex_uuid', 'yandex_uuuid', 'unknown'], ['id']),
        (['metrica_device_id'], ['id', 'metrica_device_id']),
    ],
)
async def test_get_fields(taxi_user_api, fields_request, fields_response):
    response = await taxi_user_api.post(
        'users/get',
        json={
            'id': '8fa869dd9e684cbe945f7a73df621e25',
            'fields': fields_request,
        },
    )
    assert response.status_code == 200
    _check_response(response.json(), fields_response)


@pytest.mark.now('2019-02-01T14:00:00Z')
@pytest.mark.parametrize(
    'fields_request, fields_response',
    [
        ([], ['id']),
        (['_id'], ['id']),
        (['id'], ['id']),
        (['unknown'], ['id']),
        (['uber_id'], ['id', 'uber_id']),
    ],
)
async def test_get_fields_uber(taxi_user_api, fields_request, fields_response):
    response = await taxi_user_api.post(
        'users/get',
        json={
            'id': '00148347-c7b9-4058-88a8-4b44f7a2477c',
            'lookup_uber': True,
            'fields': fields_request,
        },
    )
    assert response.status_code == 200
    _check_response(response.json(), fields_response)


@pytest.mark.parametrize(
    'request_id, lookup_uber',
    [('wrong_id', True), ('00148347-c7b9-4058-88a8-4b44f7a2477c', False)],
)
async def test_not_found(taxi_user_api, request_id, lookup_uber):
    response = await taxi_user_api.post(
        'users/get', json={'id': request_id, 'lookup_uber': lookup_uber},
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': '404',
        'message': 'No user with id ' + request_id,
    }


@pytest.mark.parametrize(
    'reuqest_id',
    ['8fa869dd9e684cbe945f7a73df621eff', '8fa869dd9e684cbe945f7a73df621e00'],
)
async def test_null_field_omitted(taxi_user_api, reuqest_id):
    response = await taxi_user_api.post(
        'users/get', json={'id': reuqest_id, 'lookup_uber': False},
    )
    assert response.status_code == 200
    assert response.json() == {
        'id': reuqest_id,
        'last_tariff_imprint': {'category_name': 'category'},
    }


@pytest.mark.parametrize(
    'body, message',
    [
        ({'foo': 'bar'}, 'Field \'id\' is missing'),
        (
            {'id': 123},
            (
                'Field \'id\' is of a wrong type. '
                'Expected: stringValue, actual: intValue'
            ),
        ),
        (
            {'id': '123459e1e7e5b1f539abcdef', 'lookup_uber': 'not_a_bool'},
            (
                'Field \'lookup_uber\' is of a wrong type. '
                'Expected: booleanValue, actual: stringValue'
            ),
        ),
        (
            {'id': '123459e1e7e5b1f539abcdef', 'fields': 'not_a_list'},
            (
                'Field \'fields\' is of a wrong type. '
                'Expected: arrayValue, actual: stringValue'
            ),
        ),
    ],
)
async def test_bad_request(taxi_user_api, body, message):
    response = await taxi_user_api.post('users/get', json=body)
    assert response.status_code == 400
    assert response.json()['code'] == '400'


def _check_response(response_json, fields):
    expected_response = {
        'id': '8fa869dd9e684cbe945f7a73df621e25',
        'uber_id': '00148347-c7b9-4058-88a8-4b44f7a2477c',
        'zuser_id': 'zuser-id',
        'created': '2019-02-01T13:00:00+0000',
        'updated': '2019-02-01T13:00:00+0000',
        'phone_id': '5ab0319b611972dbc1a3d71b',
        'authorized': True,
        'yandex_uid': '4010989734',
        'application': 'uber_android',
        'device_id': 'E9168F93-D098-43AF-8D4C-43E50702EB36',
        'token_only': True,
        'has_ya_plus': True,
        'has_cashback_plus': True,
        'metrica_device_id': 'metrica_device_id',
        'wns_url': 'wns-url',
        'mpns_url': 'mpns-url',
        'last_order_created': '2019-02-01T13:00:00+0000',
        'last_tariff_imprint': {
            'category_name': 'category',
            'service_level': 50,
        },
        'confirmation': {
            'attempts': 0,
            'code': '123',
            'created': '2019-02-01T13:00:00+0000',
        },
        'antifraud': {
            'user_id': '8fa869dd9e684cbe945f7a73df621e25',
            'started_in_emulator': True,
            'position': {'dx': 123, 'point': [1.23, 4.56]},
        },
    }
    if not fields:
        assert response_json == expected_response
    else:
        assert len(response_json) == len(fields)
        for field in fields:
            assert response_json[field] == expected_response[field]
