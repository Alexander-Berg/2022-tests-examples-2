import json

import pytest

from tests_dispatcher_access_control import utils

FLEET_ENDPOINT = 'fleet/dac/v1/parks/users'
GET_USERS_ENDPOINT = 'v1/parks/users/list'

PARK_ID = 'park_valid1'


def build_headers(
        user_ticket='ticket_valid1',
        user_ticket_provider='yandex',
        token='extra_super_token',
        remote_ip='1.2.3.4',
        yandex_uid='100',
        service_ticket=utils.MOCK_SERVICE_TICKET,
        park_id=PARK_ID,
):
    headers = {
        'X-Ya-User-Ticket': user_ticket,
        'X-Ya-User-Ticket-Provider': user_ticket_provider,
        'X-Idempotency-Token': token,
        'X-Remote-IP': remote_ip,
        'X-Yandex-UID': yandex_uid,
        'X-Ya-Service-Ticket': service_ticket,
        'X-Park-ID': park_id,
    }
    return headers


def build_payload(
        email='newuser@yandex.ru',
        group_id='group_valid1',
        name='User',
        phone=None,
):
    payload = {'email': email, 'group_id': group_id, 'name': name}
    if phone:
        payload['phone'] = phone
    return payload


def build_response(payload, user_id='user_valid1'):
    payload.update(
        [('id', user_id), ('is_enabled', True), ('is_superuser', False)],
    )
    return payload


def build_get_users_payload(passport_uid='100'):
    return {
        'query': {
            'park': {'id': 'park_valid1'},
            'user': {'passport_uid': [passport_uid]},
        },
    }


def build_get_users_response(
        payload, created_at, email='user1@yandex.ru', uid='100',
):
    user = {
        'created_at': created_at,
        'display_name': payload.get('name', ''),
        'email': email,
        'group_id': payload.get('group_id', ''),
        'group_name': 'Administrators',
        'id': payload.get('id', ''),
        'is_confirmed': payload.get('is_confirmed', False),
        'is_enabled': payload.get('is_enabled', True),
        'is_multifactor_authentication_required': False,
        'is_superuser': payload.get('is_superuser', False),
        'is_usage_consent_accepted': payload.get(
            'is_usage_consent_accepted', False,
        ),
        'park_id': payload.get('park_id', 'park_valid1'),
        'passport_uid': uid,
        'yandex_uid': uid,
    }
    if 'phone' in payload:
        user.update(phone=payload.get('phone'))

    return {'offset': 0, 'users': [user]}


def get_park_bindings(park_id=b'park_valid1', user_id='user_valid1'):
    return {park_id: str.encode(user_id)}


def get_user_log(user):
    values = {
        'Email': {'current': user['email'], 'old': ''},
        'Enable': {'current': 'True', 'old': ''},
        'Group': {'current': 'Administrators', 'old': ''},
        'IsSuperUser': {'current': 'False', 'old': ''},
        'Name': {'current': user['name'], 'old': ''},
        'YandexLogin': {'current': user['login'], 'old': ''},
        'YandexUid': {'current': user['uid'], 'old': ''},
    }
    if 'phone' in user:
        values['Phones'] = {'current': user['phone'], 'old': ''}
    return values


def check_logs(pgsql, user, log_info):
    cursor = pgsql['misc'].conn.cursor()
    cursor.execute('SELECT * FROM changes_0')
    res = []
    for row in cursor.fetchall():

        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]

    for pg_user in res:
        assert pg_user['user_id'] == log_info['user_id']
        assert pg_user['object_id']
        assert pg_user['object_type'] == 'Taximeter.Core.Models.User'
        assert pg_user['park_id'] == 'park_valid1'
        assert json.loads(pg_user['values']) == get_user_log(user)
        assert pg_user['user_name'] == log_info['user_name']
        assert pg_user['counts'] == log_info['counts']
        assert pg_user['ip'] == log_info['ip']


CREATE_SUCCESS_PARAMS = [
    build_payload(phone='88005553535'),
    build_payload(name='User2'),
    build_payload(),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Administrators'})},
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
                    'Email': 'user@yandex.ru',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'user1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    ['sadd', 'admin:rolemembers:Admin', 'user@yandex.ru'],
)
@pytest.mark.parametrize('payload', CREATE_SUCCESS_PARAMS)
async def test_create_user_success(
        taxi_dispatcher_access_control,
        pgsql,
        fleet_parks_shard,
        mock_fleet_parks_list,
        mock_fleet_synchronizer,
        redis_store,
        blackbox_service,
        testpoint,
        payload,
):
    @testpoint('user_created_at')
    def testpoint_user_created_at(data):
        return data

    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'user@yandex.ru',
    )
    blackbox_service.set_user_info('101', 'newuser@yandex.ru')
    response = await taxi_dispatcher_access_control.post(
        FLEET_ENDPOINT, headers=build_headers(park_id=PARK_ID), json=payload,
    )
    user_created_at = testpoint_user_created_at.next_call()['data'][
        'created_at'
    ]
    assert response.status_code == 200, response.text
    user_id = response.json().get('id', '')
    passport_uid = '101'
    login = 'newuser@yandex.ru'
    assert response.json() == build_response(payload, user_id)

    received_user = response.json()
    received_user.pop('id')
    log_info = {
        'user_id': 'user_valid1',
        'user_name': 'User',
        'counts': len(received_user) + 2,
        'ip': '1.2.3.4',
    }
    received_user['login'] = login
    received_user['uid'] = passport_uid
    check_logs(pgsql, received_user, log_info)

    response = await taxi_dispatcher_access_control.post(
        GET_USERS_ENDPOINT,
        json=build_get_users_payload(passport_uid),
        headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == 200, response.text
    assert response.json() == build_get_users_response(
        payload, user_created_at, 'newuser@yandex.ru', passport_uid,
    )

    assert redis_store.hgetall('USER:BYUID:101') == get_park_bindings(
        user_id=user_id,
    )
    assert mock_fleet_synchronizer.times_called == 1


BAD_PARAMS = [
    (
        'park_invalid',
        '100',
        build_payload(),
        404,
        {'code': 'park_not_found', 'message': 'Park not found'},
    ),
    (
        'park_valid1',
        '999',
        build_payload(),
        400,
        {'code': 'author_not_found', 'message': 'Author not found'},
    ),
    (
        'park_valid1',
        '100',
        build_payload(email='invalid@yandex.ru'),
        400,
        {'code': 'passport_not_found', 'message': 'Email not found'},
    ),
    (
        'park_valid1',
        '100',
        build_payload(email='user@yandex.ru'),
        400,
        {'code': 'user_exists', 'message': 'User already exists'},
    ),
    (
        'park_valid1',
        '100',
        build_payload(group_id='group_invalid'),
        400,
        {'code': 'group_not_found', 'message': 'Group not found'},
    ),
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
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': True,
                    'YandexLogin': 'admin',
                    'YandexUid': '100',
                },
            ),
            'user_valid2': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid2',
                    'Name': 'User',
                    'Email': 'user@yandex.ru',
                    'Phones': '',
                    'YandexConfirmed': True,
                    'IsSuperUser': True,
                    'YandexLogin': 'user',
                    'YandexUid': '101',
                },
            ),
        },
    ],
    [
        'hmset',
        'Access:park_valid1:group_valid2',
        {'User': json.dumps({'disableEdit': True})},
    ],
    ['sadd', 'admin:rolemembers:Admin', 'admin@yandex.ru'],
)
@pytest.mark.parametrize(
    'park_id, passport_uid, payload, expected_code, expected_response',
    BAD_PARAMS,
)
async def test_create_user_error(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        mock_fleet_parks_list,
        redis_store,
        blackbox_service,
        park_id,
        passport_uid,
        payload,
        expected_code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'admin@yandex.ru',
    )
    blackbox_service.set_user_info('101', 'user@yandex.ru')
    blackbox_service.set_user_info('102', 'newuser@yandex.ru')
    response = await taxi_dispatcher_access_control.post(
        FLEET_ENDPOINT,
        json=payload,
        headers=build_headers(yandex_uid=passport_uid, park_id=park_id),
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response
