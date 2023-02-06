import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'sync/v1/parks/users'

HEADERS = {'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET}


def build_payload(
        email='user1@yandex.ru',
        group_id='group_valid1',
        name='User',
        is_enabled=True,
        is_superuser=False,
        phone=None,
):
    payload = {
        'email': email,
        'group_id': group_id,
        'is_enabled': is_enabled,
        'is_superuser': is_superuser,
    }
    if name:
        payload.update(name=name)
    if phone:
        payload.update(phone=phone)
    return payload


def build_redis_response(payload, uid, created_at):
    redis_response = {
        'Email': payload['email'],
        'Group': payload['group_id'],
        'Enable': payload['is_enabled'],
        'IsYandex': True,
        'YandexLogin': payload['email'],
        'YandexUid': uid,
        'IsSuperUser': payload['is_superuser'],
        'IsMultiFactorAuthenticationRequired': False,
    }

    if 'name' in payload:
        redis_response['Name'] = payload['name']
    if 'phone' in payload:
        redis_response['Phones'] = payload['phone']
    if created_at:
        redis_response['CreatedAt'] = created_at

    return redis_response


CREATE_OK_PARAMS = [
    # 0
    (build_payload(), '101'),
    # 1
    (build_payload(email='newuser@yandex.ru'), '102'),
    # 2
    (build_payload(group_id='group_valid2'), '101'),
    # 3
    (build_payload(name='NewUser'), '101'),
    # 4
    (build_payload(is_enabled=False), '101'),
    # 5
    (build_payload(is_superuser=True), '101'),
    # 6
    (build_payload(phone='88005553535'), '101'),
    # 7
    (build_payload(name=''), '101'),
    # 8
    (build_payload(name=None), '101'),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {
            'group_valid1': json.dumps({'Name': 'Администратор'}),
            'group_valid2': json.dumps({'Name': 'Users'}),
        },
    ],
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'admin': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    ['hmset', 'USER:BYUID:100', {'park_valid1': 'admin'}],
)
@pytest.mark.parametrize('payload, uid', CREATE_OK_PARAMS)
async def test_create_user_success(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        mock_fleet_parks_list,
        redis_store,
        blackbox_service,
        testpoint,
        payload,
        uid,
):
    @testpoint('sync_user_created_at')
    def testpoint_user_created_at(data):
        return data

    blackbox_service.set_user_info('100', 'admin@yandex.ru')
    blackbox_service.set_user_info('101', 'user1@yandex.ru')
    blackbox_service.set_user_info('102', 'newuser@yandex.ru')
    response = await taxi_dispatcher_access_control.put(
        ENDPOINT,
        params={'park_id': 'park_valid1', 'user_id': 'user_valid1'},
        json=payload,
        headers=HEADERS,
    )

    user_created_at = testpoint_user_created_at.next_call()['data'][
        'created_at'
    ]

    assert response.status_code == 200, response.text
    assert response.json() == payload

    assert (
        json.loads(redis_store.hget('User:Items:park_valid1', 'user_valid1'))
        == build_redis_response(
            payload=payload, uid=uid, created_at=user_created_at,
        )
    )
    if payload['is_enabled']:
        assert redis_store.hgetall('USER:BYUID:' + uid) == {
            b'park_valid1': b'user_valid1',
        }


MODIFY_OK_PARAMS = [
    (build_payload(), '100'),
    (build_payload(group_id='group_valid2'), '100'),
    (build_payload(name='NewUser'), '100'),
    (build_payload(is_enabled=False), '100'),
    (build_payload(is_superuser=True), '100'),
    (build_payload(phone='88005553535'), '100'),
    (build_payload(email='user2@yandex.ru'), '101'),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {
            'group_valid1': json.dumps({'Name': 'Administrators'}),
            'group_valid2': json.dumps({'Name': 'Users'}),
        },
    ],
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'User',
                    'Email': 'user1@yandex.ru',
                    'Phones': '81234567890',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'user1@yandex.ru',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    ['hmset', 'USER:BYUID:100', {'park_valid1': 'user_valid1'}],
)
@pytest.mark.parametrize('payload, uid', MODIFY_OK_PARAMS)
async def test_modify_user_success(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        mock_fleet_parks_list,
        redis_store,
        blackbox_service,
        testpoint,
        payload,
        uid,
):
    @testpoint('sync_user_created_at')
    def testpoint_user_created_at(data):
        return data

    blackbox_service.set_user_info('100', 'user1@yandex.ru')
    blackbox_service.set_user_info('101', 'user2@yandex.ru')
    response = await taxi_dispatcher_access_control.put(
        ENDPOINT,
        params={'park_id': 'park_valid1', 'user_id': 'user_valid1'},
        json=payload,
        headers=HEADERS,
    )

    user_created_at = testpoint_user_created_at.next_call()['data'][
        'created_at'
    ]
    assert response.status_code == 200, response.text
    assert response.json() == payload

    assert (
        json.loads(redis_store.hget('User:Items:park_valid1', 'user_valid1'))
        == build_redis_response(
            payload=payload, uid=uid, created_at=user_created_at,
        )
    )

    assert redis_store.hgetall('USER:BYUID:100') == (
        {b'park_valid1': b'user_valid1'} if payload['is_enabled'] else {}
    )


BAD_PARAMS = [
    (
        'park_invalid',
        'user_valid1',
        build_payload(),
        404,
        {'code': 'park_not_found', 'message': 'Park not found'},
    ),
    (
        'park_valid1',
        'user_valid1',
        build_payload(group_id='group_invalid'),
        400,
        {'code': 'group_not_found', 'message': 'Group not found'},
    ),
    (
        'park_valid1',
        'user_valid1',
        build_payload(group_id='group_valid2'),
        400,
        {'code': 'superuser_exists', 'message': 'Superuser already exists'},
    ),
    (
        'park_valid1',
        'user_valid2',
        build_payload(email='invalid@yandex.ru'),
        400,
        {'code': 'passport_not_found', 'message': 'Email not found'},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {
            'group_valid1': json.dumps({'Name': 'Users'}),
            'group_valid2': json.dumps(
                {'Name': 'Administrators', 'IsSuper': True},
            ),
        },
    ],
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'admin': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid2',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'YandexConfirmed': True,
                    'IsSuperUser': True,
                    'YandexLogin': 'admin@yandex.ru',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'User1',
                    'Email': 'user1@yandex.ru',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'user1@yandex.ru',
                    'YandexUid': '101',
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'park_id, user_id, payload, code, message', BAD_PARAMS,
)
async def test_modify_user_fail(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        mock_fleet_parks_list,
        redis_store,
        blackbox_service,
        park_id,
        user_id,
        payload,
        code,
        message,
):
    blackbox_service.set_user_info('100', 'admin@yandex.ru')
    blackbox_service.set_user_info('101', 'user1@yandex.ru')
    blackbox_service.set_user_info('102', 'user2@yandex.ru')
    response = await taxi_dispatcher_access_control.put(
        ENDPOINT,
        params={'park_id': park_id, 'user_id': user_id},
        json=payload,
        headers=HEADERS,
    )
    assert response.status_code == code, response.text
    assert response.json() == message
