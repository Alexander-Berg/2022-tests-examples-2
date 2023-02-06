import hashlib

import pytest

from tests_uapi_keys import auth
from tests_uapi_keys import utils


ENDPOINT_URL = '/v2/authorization'


CONSUMER_ID = 'fleet-api'
CLIENT_ID = 'taxi/park/abc'
ENTITY_ID = 'bream'
KEY = 'ANTONTODUA-TOP-SECRET-KEY-0123456789'
KEY_ID = 777

INVALID_KEY_MESSAGE = 'invalid client id or api key'
INSUFFICIENT_PERMISSIONS_MESSAGE = (
    'api key does not have sufficient permissions'
)


def make_headers(key=KEY):
    return {'X-API-Key': key}


def make_request(
        consumer_id=CONSUMER_ID,
        client_id=CLIENT_ID,
        entity_id=ENTITY_ID,
        permission_ids=None,
):
    return {
        'consumer_id': consumer_id,
        'client_id': client_id,
        'entity_id': entity_id,
        'permission_ids': permission_ids or [],
    }


def make_response(key_id=KEY_ID):
    return {'key_id': str(key_id)}


def make_forbidden_response(message=INVALID_KEY_MESSAGE):
    return {'code': '403', 'message': message}


def insert_key(
        pgsql,
        client_id=2,
        key=KEY,
        is_enabled=True,
        entity_id=ENTITY_ID,
        permission_ids=None,
):
    def _make_hash():
        client_salt = 'SaltSalt' if client_id == 1 else 'S0ltS0lt'
        raw = f'top-secret-salt{key}{client_salt}'
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()

    def _make_permissions():
        if not permission_ids:
            return '{}'
        return '{"' + '","'.join(permission_ids) + '"}'

    db = pgsql['api-keys'].cursor()
    db.execute(
        """
            INSERT INTO db.keys (
                id,
                client_id_,
                hash,
                is_enabled,
                entity_id,
                permission_ids,
                comment,
                creator_uid,
                creator_uid_provider,
                created_at,
                updated_at
            )
            VALUES (
                {id},
                {client_id},
                '{hash}',
                {is_enabled},
                '{entity_id}',
                '{permission_ids}'::text[],
                'комментарий',
                '54591353',
                'yandex',
                current_timestamp,
                current_timestamp
            )
        """.format(
            id=KEY_ID,
            client_id=client_id,
            hash=_make_hash(),
            is_enabled=is_enabled,
            entity_id=entity_id,
            permission_ids=_make_permissions(),
        ),
    )


BAD_PARAMS = [
    (
        make_request(consumer_id='trash'),
        'consumer_not_found',
        'consumer with id `trash` was not found',
    ),
    (
        make_request(permission_ids=['trash']),
        'invalid_permission_id',
        'permission with id `trash` does not exist',
    ),
    (
        make_request(
            consumer_id='routeinfo',
            permission_ids=['fleet-api:v1-users-list:POST'],
        ),
        'invalid_permission_id',
        'permission with id `fleet-api:v1-users-list:POST` does not exist',
    ),
    (
        make_request(
            consumer_id='fleet-api-internal',
            permission_ids=[
                'fleet-api:v1-users-list:POST',
                'fleet-api:v1-users-list:POST',
            ],
        ),
        'duplicate_permission_id',
        'permission with id `fleet-api:v1-users-list:POST` is duplicated',
    ),
]


@pytest.mark.parametrize('request_json, code, message', BAD_PARAMS)
async def test_bad(taxi_uapi_keys, request_json, code, message):
    response = await taxi_uapi_keys.post(
        ENDPOINT_URL, headers=make_headers(), json=request_json,
    )
    assert response.status_code == 400, response.text
    assert response.json() == {'code': code, 'message': message}


async def test_ok(taxi_uapi_keys):
    consumer_id = 'fleet-api'
    client_id = 'taxi/park/abc'
    entity_id = 'abc'
    permission_ids = [
        'fleet-api:v1-users-list:POST',
        'fleet-api:v1-parks-cars-list:POST',
    ]

    response = await taxi_uapi_keys.post(
        utils.USER_ENDPOINT_URL,
        headers=auth.DISPATCHER_HEADERS,
        json={
            'consumer_id': consumer_id,
            'client_id': client_id,
            'entity_id': entity_id,
            'permission_ids': permission_ids,
            'comment': 'testsuite',
        },
    )

    assert response.status_code == 200, response.text
    api_key = response.json()['auth']['api_key']
    key_id = response.json()['key']['id']

    await taxi_uapi_keys.invalidate_caches()

    for auth_permission_ids in (permission_ids[:1], permission_ids):
        response = await taxi_uapi_keys.post(
            ENDPOINT_URL,
            headers=make_headers(api_key),
            json=make_request(
                client_id=client_id,
                entity_id=entity_id,
                permission_ids=auth_permission_ids,
            ),
        )

        assert response.status_code == 200, response.text
        assert response.json() == {'key_id': key_id}


ASCII = ''.join([chr(c) for c in range(0, 128)])
DB_PARAMS = [
    (dict(key='a' * 31), dict(), 'a' * 31, 403, make_forbidden_response()),
    (dict(key='a' * 32), dict(), 'a' * 32, 200, make_response()),
    (dict(key='a' * 64), dict(), 'a' * 64, 200, make_response()),
    (dict(key='a' * 65), dict(), 'a' * 65, 403, make_forbidden_response()),
    (dict(key=ASCII[33:73]), dict(), ASCII[33:73], 200, make_response()),
    (dict(key=ASCII[64:96]), dict(), ASCII[64:96], 200, make_response()),
    (dict(key=ASCII[87:127]), dict(), ASCII[87:127], 200, make_response()),
    (dict(), dict(), KEY, 200, make_response()),
    (
        dict(client_id=1),
        dict(consumer_id='fleet-api-internal', client_id='antontodua'),
        KEY,
        200,
        make_response(),
    ),
    (dict(entity_id=''), dict(entity_id=''), KEY, 200, make_response()),
    (
        dict(permission_ids=['fleet-api:v1-users-list:POST']),
        dict(permission_ids=['fleet-api:v1-users-list:POST']),
        KEY,
        200,
        make_response(),
    ),
    (
        dict(entity_id='', permission_ids=['fleet-api:v1-users-list:POST']),
        dict(entity_id='', permission_ids=['fleet-api:v1-users-list:POST']),
        KEY,
        200,
        make_response(),
    ),
    (
        dict(
            entity_id='',
            permission_ids=[
                'fleet-api:v1-parks-cars-list:POST',
                'fleet-api:v1-users-list:POST',
            ],
        ),
        dict(entity_id='', permission_ids=['fleet-api:v1-users-list:POST']),
        KEY,
        200,
        make_response(),
    ),
    (
        dict(
            entity_id='',
            permission_ids=[
                'fleet-api:v1-parks-cars-list:POST',
                'fleet-api:v1-users-list:POST',
            ],
        ),
        dict(
            entity_id='',
            permission_ids=[
                'fleet-api:v1-parks-cars-list:POST',
                'fleet-api:v1-users-list:POST',
            ],
        ),
        KEY,
        200,
        make_response(),
    ),
    (dict(), dict(), KEY, 200, make_response()),
    (dict(), dict(), KEY[:-1], 403, make_forbidden_response()),
    (dict(client_id=1), dict(), KEY, 403, make_forbidden_response()),
    (dict(is_enabled=False), dict(), KEY, 403, make_forbidden_response()),
    (
        dict(entity_id=ENTITY_ID[:-1]),
        dict(),
        KEY,
        403,
        make_forbidden_response(INSUFFICIENT_PERMISSIONS_MESSAGE),
    ),
    (
        dict(permission_ids=['fleet-api:v1-parks-cars-list:POST']),
        dict(),
        KEY,
        200,
        make_response(),
    ),
    (
        dict(),
        dict(permission_ids=['fleet-api:v1-parks-cars-list:POST']),
        KEY,
        403,
        make_forbidden_response(INSUFFICIENT_PERMISSIONS_MESSAGE),
    ),
    (
        dict(
            entity_id='', permission_ids=['fleet-api:v1-parks-cars-list:POST'],
        ),
        dict(
            entity_id='',
            permission_ids=[
                'fleet-api:v1-parks-cars-list:POST',
                'fleet-api:v1-users-list:POST',
            ],
        ),
        KEY,
        403,
        make_forbidden_response(INSUFFICIENT_PERMISSIONS_MESSAGE),
    ),
]


@pytest.mark.parametrize(
    'insert_args, request_args, key, response_code, response_json', DB_PARAMS,
)
async def test_db(
        taxi_uapi_keys,
        pgsql,
        insert_args,
        request_args,
        key,
        response_code,
        response_json,
):
    insert_key(pgsql, **insert_args)

    response = await taxi_uapi_keys.post(
        ENDPOINT_URL,
        headers=make_headers(key),
        json=make_request(**request_args),
    )

    assert response.status_code == response_code, response.text
    assert response.json() == response_json
