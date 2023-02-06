import uuid

import pytest

from tests_uapi_keys import auth
from tests_uapi_keys import utils


ENDPOINTS = [
    (
        utils.USER_ENDPOINT_URL,
        auth.DISPATCHER_HEADERS,
        auth.DISPATCHER_CREATOR,
    ),
    (utils.USER_ENDPOINT_URL, auth.SUPPORT_HEADERS, auth.SUPPORT_CREATOR),
    ('/v2/keys/by-admin', auth.ADMIN_HEADERS, auth.ADMIN_CREATOR),
    ('/internal/v2/keys', auth.INTERNAL_HEADERS, auth.DISPATCHER_CREATOR),
    ('/internal/v2/keys', auth.INTERNAL_HEADERS, auth.SUPPORT_CREATOR),
    ('/internal/v2/keys', auth.INTERNAL_HEADERS, auth.ADMIN_CREATOR),
]


def _make_key(
        consumer_id='fleet-api-internal',
        client_id='antontodua',
        entity_id='abc',
        permission_ids=None,
        comment='Тестовый ключ',
):
    return {
        'consumer_id': consumer_id,
        'client_id': client_id,
        'entity_id': entity_id,
        'permission_ids': (
            ['fleet-api:v1-users-list:POST']
            if permission_ids is None
            else permission_ids
        ),
        'comment': comment,
    }


def _make_request(headers, creator, key, api_key=None):
    return (
        {
            'key': key,
            **({'auth': {'api_key': api_key}} if api_key else {}),
            'creator': creator,
        }
        if headers == auth.INTERNAL_HEADERS
        else key
    )


@pytest.mark.config(TVM_ENABLED=True)
@pytest.mark.config(TVM_USER_TICKETS_ENABLED=True)
async def test_unauthorized(taxi_uapi_keys):
    response = await taxi_uapi_keys.post(
        utils.USER_ENDPOINT_URL,
        headers={
            **auth.DISPATCHER_HEADERS,
            'X-Ya-User-Ticket-Provider': 'trash',
        },
        json=_make_key(),
    )
    assert response.status_code == 401


BAD_PARAMS = [
    (
        _make_key(consumer_id='trash'),
        'consumer_not_found',
        'consumer with id `trash` was not found',
    ),
    (
        _make_key(client_id='taxi/park/abc'),
        'client_not_found',
        'client with id `taxi/park/abc` was not found',
    ),
    (
        _make_key(consumer_id='fleet-api', client_id='antontodua'),
        'client_not_found',
        'client with id `antontodua` was not found',
    ),
    (
        _make_key(client_id='trash'),
        'client_not_found',
        'client with id `trash` was not found',
    ),
    (
        _make_key(consumer_id='fleet-api', client_id='trash'),
        'client_not_found',
        'client with id `trash` was not found',
    ),
    (
        _make_key(permission_ids=['trash']),
        'invalid_permission_id',
        'permission with id `trash` does not exist',
    ),
    (
        _make_key(
            consumer_id='routeinfo',
            permission_ids=['fleet-api:v1-users-list:POST'],
        ),
        'invalid_permission_id',
        'permission with id `fleet-api:v1-users-list:POST` does not exist',
    ),
    (
        _make_key(
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
@pytest.mark.parametrize('endpoint, headers, creator', ENDPOINTS)
@pytest.mark.parametrize('key, code, message', BAD_PARAMS)
async def test_bad(
        taxi_uapi_keys, endpoint, headers, creator, key, code, message,
):
    response = await taxi_uapi_keys.post(
        endpoint, headers=headers, json=_make_request(headers, creator, key),
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': code, 'message': message}


OK_PARAMS = [
    _make_key(),
    _make_key(entity_id='xyz', permission_ids=[], comment=''),
    _make_key(
        consumer_id='fleet-api',
        client_id='taxi/park/abc',
        entity_id='xyz',
        permission_ids=[],
        comment='c' * 512,
    ),
]


@pytest.mark.parametrize('endpoint, headers, creator', ENDPOINTS)
@pytest.mark.parametrize('key', OK_PARAMS)
async def test_ok(taxi_uapi_keys, endpoint, headers, creator, key):
    response = await taxi_uapi_keys.post(
        endpoint, headers=headers, json=_make_request(headers, creator, key),
    )

    assert response.status_code == 200, response.text
    assert response.json()['auth']['api_key'], response.text

    response_key = response.json()['key']
    assert utils.check_key_after_creation(response_key.copy()) == {
        **key,
        'creator': creator,
        'is_enabled': True,
    }

    await taxi_uapi_keys.invalidate_caches()

    get_response = await taxi_uapi_keys.get(
        '/v2/keys', params={'id': response_key['id']},
    )
    assert get_response.status_code == 200, get_response.text
    assert get_response.json() == response_key


async def _create_specific_key(
        taxi_uapi_keys, api_key, creator=None, key=None,
):
    request_json = _make_request(
        auth.INTERNAL_HEADERS,
        creator or auth.ADMIN_CREATOR,
        key or _make_key(),
        api_key=api_key,
    )
    response = await taxi_uapi_keys.post(
        '/internal/v2/keys', headers=auth.INTERNAL_HEADERS, json=request_json,
    )

    assert response.status_code == 200, response.text
    assert response.json()['auth']['api_key'] == api_key, response.text


ASCII = ''.join([chr(c) for c in range(0, 128)])
SPECIFIC_KEY_PARAMS = [ASCII[33:73], ASCII[64:96], ASCII[87:127]]


@pytest.mark.parametrize('api_key', SPECIFIC_KEY_PARAMS)
async def test_specific_key(taxi_uapi_keys, api_key):
    for _ in range(0, 3):
        await _create_specific_key(taxi_uapi_keys, api_key)


@pytest.mark.parametrize(
    'creator, key',
    [
        (auth.DISPATCHER_CREATOR, _make_key()),
        (auth.SUPPORT_CREATOR, _make_key()),
        (auth.ADMIN_CREATOR, _make_key(entity_id='abcd')),
        (auth.ADMIN_CREATOR, _make_key(permission_ids=[])),
        (auth.ADMIN_CREATOR, _make_key(comment='другой комментарий')),
    ],
)
async def test_specific_key_conflict(taxi_uapi_keys, creator, key):
    api_key = uuid.uuid4().hex * 2
    await _create_specific_key(taxi_uapi_keys, api_key)

    request_json = _make_request(
        auth.INTERNAL_HEADERS, creator, key, api_key=api_key,
    )
    response = await taxi_uapi_keys.post(
        '/internal/v2/keys', headers=auth.INTERNAL_HEADERS, json=request_json,
    )

    assert response.status_code == 409, response.text
    assert response.json() == {'code': '409', 'message': 'key already exists'}
