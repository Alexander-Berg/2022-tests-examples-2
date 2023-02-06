import pytest

from tests_uapi_keys import auth
from tests_uapi_keys import utils


ENDPOINTS = [
    (utils.USER_ENDPOINT_URL, auth.DISPATCHER_HEADERS),
    (utils.USER_ENDPOINT_URL, auth.SUPPORT_HEADERS),
    ('/v2/keys/by-admin', auth.ADMIN_HEADERS),
]


def make_params(key_id='1'):
    return {'id': key_id}


def make_request(
        is_enabled=False, permission_ids=None, comment='Тестовый ключ',
):
    return {
        'is_enabled': is_enabled,
        'permission_ids': permission_ids or ['fleet-api:v1-users-list:POST'],
        'comment': comment,
    }


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(TVM_USER_TICKETS_ENABLED=True)
async def test_unauthorized(taxi_uapi_keys):
    response = await taxi_uapi_keys.put(
        utils.USER_ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'X-Ya-User-Ticket-Provider': 'trash',
        },
        params=make_params(),
        json=make_request(),
    )
    assert response.status_code == 401, response.text


BAD_PARAMS = [
    (
        make_request(permission_ids=['trash']),
        'invalid_permission_id',
        'permission with id `trash` does not exist',
    ),
    (
        make_request(permission_ids=['fleet-api:v1-parks-cars-list:POST']),
        'invalid_permission_id',
        'permission with id `'
        'fleet-api:v1-parks-cars-list:POST` does not exist',
    ),
    (
        make_request(
            permission_ids=[
                'fleet-api:v1-users-list:POST',
                'fleet-api:v1-users-list:POST',
            ],
        ),
        'duplicate_permission_id',
        'permission with id `fleet-api:v1-users-list:POST` is duplicated',
    ),
]


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint, headers', ENDPOINTS)
@pytest.mark.parametrize('request_json, code, message', BAD_PARAMS)
async def test_bad(
        taxi_uapi_keys, endpoint, headers, request_json, code, message,
):
    response = await taxi_uapi_keys.put(
        endpoint, headers=headers, params=make_params(), json=request_json,
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': code, 'message': message}


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(TVM_USER_TICKETS_ENABLED=True)
@pytest.mark.parametrize('endpoint, headers', ENDPOINTS)
@pytest.mark.parametrize('key_id', ['4', '5', '6', '7', '8', '123', 'x'])
async def test_not_found(taxi_uapi_keys, endpoint, headers, key_id):
    response = await taxi_uapi_keys.put(
        endpoint,
        headers=headers,
        params=make_params(key_id),
        json=make_request(),
    )

    assert response.status_code == 404, response.text
    assert response.json() == {
        'code': 'key_not_found',
        'message': f'key with id `{key_id}` was not found',
    }


@pytest.mark.parametrize('endpoint, headers', ENDPOINTS)
async def test_ok(taxi_uapi_keys, endpoint, headers):
    response = await taxi_uapi_keys.put(
        endpoint, headers=headers, params=make_params(), json=make_request(),
    )

    assert response.status_code == 200, response.text

    response_json = response.json()
    updated_at = response_json['updated_at']
    utils.check_updated_at(updated_at)

    expected_response_json = utils.V2KEY_1.copy()
    expected_response_json.update({**make_request(), 'updated_at': updated_at})

    assert response_json == expected_response_json
