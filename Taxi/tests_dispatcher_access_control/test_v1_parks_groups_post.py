import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/groups'
FLEET_ENDPOINT = '/fleet/dac/v1/parks/groups'
ENDPOINTS = [ENDPOINT, FLEET_ENDPOINT]


def build_headers(
        endpoint,
        park_id,
        user_ticket='ticket_valid1',
        user_ticket_provider='yandex',
        token='extra_super_token',
        remote_ip='1.2.3.4',
        yandex_uid='100',
        service_ticket=utils.MOCK_SERVICE_TICKET,
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


def build_params(endpoint, park_id):
    if endpoint == ENDPOINT:
        return {'park_id': park_id}
    return {}


def build_request(group_name):
    return {'name': group_name}


def check_logs(pgsql, log_info):
    cursor = pgsql['misc'].conn.cursor()
    cursor.execute('SELECT * FROM changes_0')
    res = []
    for row in cursor.fetchall():
        res.append({})
        for col in range(len(cursor.description)):
            res[len(res) - 1][cursor.description[col][0]] = row[col]

    for pg_group in res:
        assert pg_group['user_id'] == log_info['user_id']
        assert pg_group['object_id']
        assert pg_group['object_type'] == 'Taximeter.Core.Models.Group'
        assert pg_group['park_id'] == 'park_valid1'
        assert json.loads(pg_group['values']) == {
            'Name': {'current': 'GroupNew', 'old': ''},
        }
        assert pg_group['user_name'] == log_info['user_name']
        assert pg_group['counts'] == log_info['counts']
        assert pg_group['ip'] == log_info['ip']


OK_PAYLOAD = {'name': ' GroupNew  '}

OK_PARAMS = ['yandex', 'yandex_team']


@pytest.mark.now('2020-01-01T12:00:00Z')
@pytest.mark.redis_store(
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
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Group1'})},
    ],
    ['sadd', 'admin:rolemembers:Admin', 'user@yandex.ru'],
)
@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize('provider', OK_PARAMS)
async def test_create_group_ok(
        taxi_dispatcher_access_control,
        blackbox_service,
        fleet_parks_shard,
        mock_fleet_parks_list,
        mock_fleet_synchronizer,
        pgsql,
        redis_store,
        endpoint,
        provider,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'user@yandex.ru',
    )
    headers = build_headers(
        endpoint=endpoint,
        park_id='park_valid1',
        user_ticket_provider=provider,
    )
    response = await taxi_dispatcher_access_control.post(
        endpoint,
        params=build_params(endpoint=endpoint, park_id='park_valid1'),
        json=OK_PAYLOAD,
        headers=headers,
    )
    assert response.status_code == 200, response.text
    group_id = response.json()['id']
    assert response.json() == {'id': group_id, 'name': 'GroupNew'}

    log_info = {
        'user_id': (
            'user_valid1'
            if headers['X-Ya-User-Ticket-Provider'] == 'yandex'
            else ''
        ),
        'user_name': (
            'User'
            if headers['X-Ya-User-Ticket-Provider'] == 'yandex'
            else 'Tech support'
        ),
        'counts': 1,
        'ip': '1.2.3.4',
    }
    check_logs(pgsql, log_info)

    assert redis_store.hgetall('UserGroup:Items:park_valid1') == {
        b'group_valid1': b'{"Name": "Group1"}',
        str.encode(
            group_id,
        ): b'{"Name":"GroupNew","CreatedAt":"2020-01-01T12:00:00+00:00"}',
    }
    assert mock_fleet_synchronizer.times_called == 1


BAD_PARAMS = [
    (
        'park_invalid',
        'ticket_valid1',
        '100',
        'Group1',
        404,
        {'code': 'park_not_found', 'message': 'Park not found'},
    ),
    (
        'park_valid1',
        'ticket_valid1',
        '100',
        ' гРуппа   ',
        400,
        {'code': 'group_exists', 'message': 'Group already exists'},
    ),
    (
        'park_valid1',
        'ticket_valid1',
        '999',
        'GroupNew',
        400,
        {'code': 'author_not_found', 'message': 'Author not found'},
    ),
]


@pytest.mark.redis_store(
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
            'user_valid2': json.dumps(
                {
                    'Enable': True,
                    'Group': 'group_valid2',
                    'Name': 'User2',
                    'Email': 'user2@yandex.ru',
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
        'UserGroup:Items:park_valid1',
        {
            'group_valid1': json.dumps({'Name': 'Group1'}),
            'group_valid2': json.dumps({'Name': 'Group2'}),
            'group_valid3': json.dumps({'Name': 'Группа'}),
        },
    ],
    [
        'hmset',
        'Access:park_valid1:group_valid2',
        {'User': json.dumps({'disableEdit': True})},
    ],
    ['sadd', 'admin:rolemembers:Admin', 'user@yandex.ru'],
)
@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize(
    'park_id, ticket, uid, group_name, expected_code, expected_result',
    BAD_PARAMS,
)
async def test_create_group_error(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        redis_store,
        endpoint,
        park_id,
        ticket,
        uid,
        group_name,
        expected_code,
        expected_result,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'user@yandex.ru',
    )
    blackbox_service.set_user_ticket_info(
        'ticket_valid2', '101', 'user2@yandex.ru',
    )
    response = await taxi_dispatcher_access_control.post(
        endpoint,
        params=build_params(endpoint=endpoint, park_id=park_id),
        json={'name': group_name},
        headers=build_headers(
            endpoint=endpoint,
            park_id=park_id,
            user_ticket=ticket,
            yandex_uid=uid,
        ),
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_result
