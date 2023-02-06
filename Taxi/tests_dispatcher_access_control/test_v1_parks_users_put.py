import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/users'
FLEET_ENDPOINT = 'fleet/dac/v1/parks/users'

PARK_ID = 'park_valid1'


def build_headers(
        user_ticket='ticket_valid1',
        user_ticket_provider='yandex',
        token='extra_super_token',
        remote_ip='1.2.3.4',
        yandex_uid='100',
        service_ticket=utils.MOCK_SERVICE_TICKET,
        endpoint=ENDPOINT,
        park_id=PARK_ID,
):
    headers = {
        'X-Ya-User-Ticket': user_ticket,
        'X-Ya-User-Ticket-Provider': user_ticket_provider,
        'X-Idempotency-Token': token,
        'X-Remote-IP': remote_ip,
        'X-Yandex-UID': yandex_uid,
        'X-Ya-Service-Ticket': service_ticket,
    }
    if endpoint == FLEET_ENDPOINT:
        headers['X-Park-ID'] = park_id
    return headers


def build_params(user_id, endpoint, park_id):
    params = {'user_id': user_id}
    if endpoint == ENDPOINT:
        params['park_id'] = park_id
    return params


def build_payload(
        is_enabled=True,
        group_id='group_valid1',
        name='User',
        is_superuser=False,
        phone=None,
):
    payload = {
        'is_enabled': is_enabled,
        'group_id': group_id,
        'name': name,
        'is_superuser': is_superuser,
    }
    if phone:
        payload.update(phone=phone)
    return payload


def build_get_users_payload(passport_uid='100'):
    return {
        'query': {
            'park': {'id': 'park_valid1'},
            'user': {'passport_uid': [passport_uid]},
        },
    }


def check_logs(pgsql, diff, log_info):
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
        assert json.loads(pg_user['values']) == diff
        assert pg_user['user_name'] == log_info['user_name']
        assert pg_user['counts'] == log_info['counts']
        assert pg_user['ip'] == log_info['ip']


OK_PARAMS = [
    (
        'user_valid1',
        'user_valid1',
        'User',
        '100',
        'ticket_valid1',
        'yandex',
        build_payload(),
        0,
        {},
        [b'session_valid1', b'session_valid2'],
        {b'db': b'park_valid1', b'guid': b'user_valid1'},
        {b'park_valid1': b'user_valid1', b'park_valid10': b'user_valid10'},
        {b'park_valid5': b'user_valid5'},
    ),
    (
        'user_valid1',
        'user_valid1',
        'User',
        '100',
        'ticket_valid1',
        'yandex',
        build_payload(name='Modified User'),
        1,
        {'Name': {'old': 'User', 'current': 'Modified User'}},
        [b'session_valid1', b'session_valid2'],
        {b'db': b'park_valid1', b'guid': b'user_valid1'},
        {b'park_valid1': b'user_valid1', b'park_valid10': b'user_valid10'},
        {b'park_valid5': b'user_valid5'},
    ),
    (
        'user_valid1',
        'user_valid1',
        'User',
        '100',
        'ticket_valid1',
        'yandex',
        build_payload(phone='+70123456789'),
        1,
        {'Phones': {'old': '', 'current': '+70123456789'}},
        [b'session_valid1', b'session_valid2'],
        {b'db': b'park_valid1', b'guid': b'user_valid1'},
        {b'park_valid1': b'user_valid1', b'park_valid10': b'user_valid10'},
        {b'park_valid5': b'user_valid5'},
    ),
    (
        'user_valid1',
        'user_valid1',
        'User',
        '100',
        'ticket_valid1',
        'yandex',
        build_payload(group_id='group_valid2'),
        1,
        {'Group': {'old': 'Администраторы', 'current': 'Users'}},
        [b'session_valid1', b'session_valid2'],
        {b'db': b'park_valid1', b'guid': b'user_valid1'},
        {b'park_valid1': b'user_valid1', b'park_valid10': b'user_valid10'},
        {b'park_valid5': b'user_valid5'},
    ),
    (
        'user_valid1',
        'user_valid1',
        'User',
        '100',
        'ticket_valid1',
        'yandex',
        build_payload(is_enabled=False),
        1,
        {'Enable': {'old': 'True', 'current': 'False'}},
        [b'session_valid2'],
        {},
        {b'park_valid10': b'user_valid10'},
        {b'park_valid5': b'user_valid5'},
    ),
    (
        'user_valid2',
        'user_valid2',
        'User2',
        '101',
        'ticket_valid2',
        'yandex',
        build_payload(name='User2'),
        2,
        {
            'Phones': {'old': '"88005553535"', 'current': ''},
            'Enable': {'old': 'False', 'current': 'True'},
        },
        [b'session_valid1', b'session_valid2'],
        {b'db': b'park_valid1', b'guid': b'user_valid1'},
        {b'park_valid1': b'user_valid1', b'park_valid10': b'user_valid10'},
        {b'park_valid1': b'user_valid2', b'park_valid5': b'user_valid5'},
    ),
    (
        'superuser',
        'superuser',
        'Director',
        '1',
        'ticket_valid0',
        'yandex',
        build_payload(group_id='supergroup', name='NewDirector'),
        1,
        {'Name': {'old': 'Director', 'current': 'NewDirector'}},
        [b'session_valid1', b'session_valid2'],
        {b'db': b'park_valid1', b'guid': b'user_valid1'},
        {b'park_valid1': b'user_valid1', b'park_valid10': b'user_valid10'},
        {b'park_valid5': b'user_valid5'},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {
            'supergroup': json.dumps({'Name': 'Директор', 'IsSuper': True}),
            'group_valid1': json.dumps({'Name': 'Администраторы'}),
            'group_valid2': json.dumps({'Name': 'Users'}),
        },
    ],
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'superuser': json.dumps(
                {
                    'Enable': True,
                    'Group': 'supergroup',
                    'Name': 'Director',
                    'Email': 'superuser@yandex.ru',
                    'YandexConfirmed': True,
                    'IsSuperUser': True,
                    'YandexLogin': 'superuser',
                    'YandexUid': '1',
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
                    'Name': 'User',
                    'Email': 'user1@yandex.ru',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'user1',
                    'YandexUid': '100',
                },
            ),
        },
    ],
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_valid2': json.dumps(
                {
                    'Enable': False,
                    'Group': 'group_valid1',
                    'Name': 'User2',
                    'Email': 'user2@yandex.ru',
                    'Phones': '88005553535',
                    'YandexConfirmed': True,
                    'IsSuperUser': False,
                    'YandexLogin': 'user2',
                    'YandexUid': '101',
                },
            ),
        },
    ],
    [
        'hmset',
        'USER:BYUID:100',
        {'park_valid1': 'user_valid1', 'park_valid10': 'user_valid10'},
    ],
    ['hmset', 'USER:BYUID:101', {'park_valid5': 'user_valid5'}],
    ['rpush', 'Session:ByDb:park_valid1', 'session_valid1'],
    ['rpush', 'Session:ByDb:park_valid1', 'session_valid2'],
    [
        'hmset',
        'Session:session_valid1',
        {'guid': 'user_valid1', 'db': 'park_valid1'},
    ],
    [
        'hmset',
        'Session:session_valid2',
        {'guid': 'user_valid3', 'db': 'park_valid1'},
    ],
    ['sadd', 'admin:rolemembers:PartnerSupport', 'user@yandex.ru'],
)
@pytest.mark.parametrize('endpoint', [ENDPOINT, FLEET_ENDPOINT])
@pytest.mark.parametrize(
    'user_id, author_id, author_name,'
    'yandex_uid, user_ticket, ticket_provider,'
    'payload, counts, diff, redis_session_by_db,'
    'redis_session, redis_user100, redis_user101',
    OK_PARAMS,
)
async def test_modify_user_success(
        taxi_dispatcher_access_control,
        pgsql,
        fleet_parks_shard,
        mock_fleet_parks_list,
        mock_fleet_synchronizer,
        redis_store,
        blackbox_service,
        endpoint,
        user_id,
        author_id,
        author_name,
        yandex_uid,
        user_ticket,
        ticket_provider,
        payload,
        counts,
        diff,
        redis_session_by_db,
        redis_session,
        redis_user100,
        redis_user101,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid0', '1', 'superuser@yandex.ru',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'user@yandex.ru',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid2', '101', 'user2@yandex.ru',
    )
    response = await taxi_dispatcher_access_control.put(
        endpoint,
        params=build_params(
            user_id=user_id, endpoint=endpoint, park_id=PARK_ID,
        ),
        json=payload,
        headers=build_headers(
            user_ticket=user_ticket,
            user_ticket_provider=ticket_provider,
            endpoint=endpoint,
            park_id=PARK_ID,
            yandex_uid=yandex_uid,
        ),
    )
    assert response.status_code == 200, response.text

    log_info = {
        'user_id': author_id if ticket_provider == 'yandex' else '',
        'user_name': (
            author_name if ticket_provider == 'yandex' else 'Tech support'
        ),
        'counts': counts,
        'ip': '1.2.3.4',
    }
    check_logs(pgsql, diff, log_info)

    assert (
        redis_store.lrange('Session:ByDb:park_valid1', 0, -1)
        == redis_session_by_db
    )
    assert redis_store.hgetall('Session:session_valid1') == redis_session
    assert redis_store.hgetall('Session:session_valid2') == {
        b'db': b'park_valid1',
        b'guid': b'user_valid3',
    }
    assert redis_store.hgetall('USER:BYUID:100') == redis_user100
    assert redis_store.hgetall('USER:BYUID:101') == redis_user101
    assert mock_fleet_synchronizer.times_called == 1


BAD_PARAMS = [
    (
        'yandex',
        'ticket_valid1',
        '1',
        'park_invalid',
        'user_valid1',
        build_payload(),
        404,
        {'code': 'park_not_found', 'message': 'Park not found'},
    ),
    (
        'yandex',
        'ticket_valid1',
        '1',
        'park_valid1',
        'user_invalid',
        build_payload(),
        404,
        {'code': 'user_not_found', 'message': 'User not found'},
    ),
    (
        'yandex',
        'ticket_valid1',
        '999',
        'park_valid1',
        'user_valid1',
        build_payload(),
        400,
        {'code': 'author_not_found', 'message': 'Author not found'},
    ),
    (
        'yandex',
        'ticket_valid1',
        '1',
        'park_valid1',
        'user_valid1',
        build_payload(group_id='group_invalid'),
        400,
        {'code': 'group_not_found', 'message': 'Group not found'},
    ),
    (
        'yandex',
        'ticket_invalid',
        '1',
        'park_valid1',
        'user_valid2',
        build_payload(group_id='group_valid2'),
        403,
        {
            'code': 'is_not_support',
            'message': (
                'Only tech support admin or '
                'partner support can change superuser state'
            ),
        },
    ),
    (
        'yandex_team',
        'ticket_invalid',
        '1',
        'park_valid1',
        'user_valid2',
        build_payload(group_id='group_valid2'),
        400,
        {'code': 'invalid_user_ticket', 'message': 'Invalid user ticket'},
    ),
    (
        'yandex_team',
        'ticket_valid1',
        '1',
        'park_valid1',
        'user_valid1',
        build_payload(group_id='group_valid2'),
        400,
        {'code': 'superuser_exists', 'message': 'Superuser already exists'},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user_admin': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid2',
                    'Name': 'Admin',
                    'Email': 'admin@yandex.ru',
                    'Phones': '',
                    'IsSuperUser': True,
                    'YandexLogin': 'admin',
                    'YandexUid': '1',
                },
            ),
            'user_valid1': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'User1',
                    'Email': 'user1@yandex.ru',
                    'Phones': '',
                    'IsSuperUser': False,
                    'YandexLogin': 'user1',
                    'YandexUid': '100',
                },
            ),
            'user_valid2': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid1',
                    'Name': 'User2',
                    'Email': 'user2@yandex.ru',
                    'Phones': '',
                    'IsSuperUser': False,
                    'YandexLogin': 'user2',
                    'YandexUid': '101',
                },
            ),
        },
    ],
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
        'Access:park_valid1:group_valid1',
        {'User': json.dumps({'disableEdit': True})},
    ],
    ['hmset', 'USER:BYUID:100', {'park_valid1': 'user_valid1'}],
    ['hmset', 'USER:BYUID:101', {'park_valid1': 'user_valid2'}],
    ['rpush', 'Session:ByDb:park_valid1', 'session_valid1'],
    ['rpush', 'Session:ByDb:park_valid1', 'session_valid2'],
    [
        'hmset',
        'Session:session_valid1',
        {'guid': 'user_valid1', 'db': 'park_valid1'},
    ],
    [
        'hmset',
        'Session:session_valid2',
        {'guid': 'user_valid2', 'db': 'park_valid1'},
    ],
    ['sadd', 'admin:rolemembers:Admin', 'admin@yandex.ru'],
)
@pytest.mark.parametrize('endpoint', [ENDPOINT, FLEET_ENDPOINT])
@pytest.mark.parametrize(
    'provider, ticket, author_uid, park_id, user_id,'
    'payload, expected_code, expected_response',
    BAD_PARAMS,
)
async def test_modify_user_failure(
        taxi_dispatcher_access_control,
        fleet_parks_shard,
        mock_fleet_parks_list,
        blackbox_service,
        endpoint,
        provider,
        ticket,
        author_uid,
        park_id,
        user_id,
        payload,
        expected_code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '1', 'admin@yandex.ru',
    )
    blackbox_service.set_user_info('100', 'user1@yandex.ru')
    blackbox_service.set_user_info('101', 'user2@yandex.ru')
    response = await taxi_dispatcher_access_control.put(
        endpoint,
        params=build_params(
            endpoint=endpoint, park_id=park_id, user_id=user_id,
        ),
        json=payload,
        headers=build_headers(
            user_ticket_provider=provider,
            user_ticket=ticket,
            yandex_uid=author_uid,
            endpoint=endpoint,
            park_id=park_id,
        ),
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_response
