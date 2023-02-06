import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = '/fleet/dac/v1/parks/groups'


def build_headers(
        park_id='park_valid1',
        user_ticket='ticket_valid1',
        user_ticket_provider='yandex',
        token='extra_super_token',
        remote_ip='1.2.3.4',
        yandex_uid='100',
        service_ticket=utils.MOCK_SERVICE_TICKET,
):
    return {
        'X-Park-ID': park_id,
        'X-Ya-User-Ticket': user_ticket,
        'X-Ya-User-Ticket-Provider': user_ticket_provider,
        'X-Idempotency-Token': token,
        'X-Remote-IP': remote_ip,
        'X-Yandex-UID': yandex_uid,
        'X-Ya-Service-Ticket': service_ticket,
    }


def build_params(group_id='group_valid1'):
    return {'group_id': group_id}


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
            'Name': {'current': '', 'old': '"Group2"'},
        }
        assert pg_group['user_name'] == log_info['user_name']
        assert pg_group['counts'] == log_info['counts']
        assert pg_group['ip'] == log_info['ip']


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
        {
            'group_valid1': json.dumps({'Name': 'Group1'}),
            'group_valid2': json.dumps({'Name': 'Group2'}),
        },
    ],
    [
        'hmset',
        'Access:park_valid1:group_valid2',
        {'Menu': json.dumps({'hideMenu': ['52']})},
    ],
    ['sadd', 'admin:rolemembers:Admin', 'user@yandex.ru'],
)
@pytest.mark.parametrize('provider', ['yandex', 'yandex_team'])
async def test_delete_group_ok(
        taxi_dispatcher_access_control,
        blackbox_service,
        fleet_parks_shard,
        mock_fleet_parks_list,
        mock_fleet_synchronizer,
        pgsql,
        redis_store,
        provider,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'user@yandex.ru',
    )
    headers = build_headers(user_ticket_provider=provider)
    response = await taxi_dispatcher_access_control.delete(
        ENDPOINT,
        params=build_params(group_id='group_valid2'),
        headers=headers,
    )
    assert response.status_code == 200, response.text

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
    }
    assert redis_store.hgetall('Access:park_valid1:group_valid2') == {}
    assert mock_fleet_synchronizer.times_called == 1


BAD_PARAMS = [
    (
        'park_valid1',
        'group_invalid',
        'ticket_valid1',
        '100',
        404,
        {'code': 'group_not_found', 'message': 'Group not found'},
    ),
    (
        'park_valid1',
        'group_valid1',
        'ticket_valid1',
        '100',
        400,
        {'code': 'group_is_not_empty', 'message': 'Group is not empty'},
    ),
    (
        'park_valid1',
        'group_valid2',
        'ticket_valid1',
        '100',
        400,
        {
            'code': 'supergroup_cannot_be_deleted',
            'message': 'Supergroup cannot be deleted',
        },
    ),
    (
        'park_valid1',
        'group_valid3',
        'ticket_invalid',
        '999',
        403,
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
        },
    ],
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {
            'group_valid1': json.dumps({'Name': 'Group1'}),
            'group_valid2': json.dumps({'Name': 'Group2', 'IsSuper': True}),
            'group_valid3': json.dumps({'Name': 'Group3'}),
        },
    ],
)
@pytest.mark.parametrize(
    'park_id, group_id, ticket, uid, expected_code, expected_result',
    BAD_PARAMS,
)
async def test_delete_group_error(
        taxi_dispatcher_access_control,
        blackbox_service,
        mock_fleet_parks_list,
        redis_store,
        park_id,
        group_id,
        ticket,
        uid,
        expected_code,
        expected_result,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'user@yandex.ru',
    )
    response = await taxi_dispatcher_access_control.delete(
        ENDPOINT,
        params=build_params(group_id=group_id),
        headers=build_headers(
            park_id=park_id, user_ticket=ticket, yandex_uid=uid,
        ),
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_result
