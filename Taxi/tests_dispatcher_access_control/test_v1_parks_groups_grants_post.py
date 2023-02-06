import copy
import json

import pytest

from tests_dispatcher_access_control import utils

PARK_ID = 'park_valid1'
GROUP_ID = 'group_valid1'

ENDPOINT = '/v1/parks/groups/grants'
SYNC_ENDPOINT = '/sync/v1/parks/groups/grants'
FLEET_ENDPOINT = '/fleet/dac/v1/parks/groups/grants'

ENDPOINTS = [ENDPOINT, SYNC_ENDPOINT, FLEET_ENDPOINT]


def build_grant(grant_id, state):
    return {'id': grant_id, 'state': state}


def build_params(endpoint, park_id=PARK_ID, group_id=GROUP_ID):
    params = {'group_id': group_id}
    if endpoint in [ENDPOINT, SYNC_ENDPOINT]:
        params['park_id'] = park_id
    return params


def build_headers(endpoint, park_id=PARK_ID, provider='yandex', uid='100'):
    headers = {'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET}
    if endpoint != SYNC_ENDPOINT:
        headers['X-Ya-User-Ticket'] = 'ticket_valid1'
        headers['X-Ya-User-Ticket-Provider'] = provider
        headers['X-Yandex-UID'] = uid
        headers['X-Remote-IP'] = '127.0.0.1'
    if endpoint == FLEET_ENDPOINT:
        headers['X-Park-ID'] = park_id
    return headers


def build_response(endpoint, response):
    return response if endpoint != SYNC_ENDPOINT else {}


def parse_redis_grants(grants_to_parse):
    parsed_grants = copy.deepcopy(grants_to_parse)
    if b'Menu' in parsed_grants:
        parsed_grants[b'Menu'] = json.loads(parsed_grants[b'Menu'])
        if 'hideMenu' in parsed_grants[b'Menu']:
            parsed_grants[b'Menu']['hideMenu'].sort()
    return parsed_grants


def check_logs(pgsql, log_info, values):
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
        assert json.loads(pg_group['values']) == values
        assert pg_group['user_name'] == log_info['user_name']
        assert pg_group['counts'] == log_info['counts']
        assert pg_group['ip'] == log_info['ip']


OK_PARAMS = [
    (
        'group_valid1',
        {'grants': [build_grant('orders', False)]},
        {
            b'Driver': b'{"tabgps": true}',
            b'Menu': b'{"hideMenu":["55","21","52"]}',
        },
        {b'orders': b'false'},
        {
            'Grants': {
                'current': '{"orders":"False"}',
                'old': '{"orders":"True"}',
            },
        },
    ),
    (
        'group_valid1',
        {'grants': [build_grant('orders', True)]},
        {b'Driver': b'{"tabgps": true}', b'Menu': b'{"hideMenu":["55","52"]}'},
        {b'orders': b'true'},
        {},
    ),
    (
        'group_valid2',
        {'grants': [build_grant('orders', False)]},
        {b'Menu': b'{"hideMenu":["21"]}'},
        {b'orders': b'false'},
        {
            'Grants': {
                'current': '{"orders":"False"}',
                'old': '{"orders":"True"}',
            },
        },
    ),
    (
        'group_valid2',
        {'grants': [build_grant('orders', True)]},
        {b'Menu': b'{"hideMenu":[]}'},
        {b'orders': b'true'},
        {},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {'Name': 'Name1', 'Group': 'group_valid1', 'YandexUid': '100'},
            ),
            'user2': json.dumps(
                {'Name': 'Name2', 'Group': 'group_valid2', 'YandexUid': '100'},
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {
            'group_valid1': json.dumps({'Name': 'group_valid1'}),
            'group_valid2': json.dumps({'Name': 'group_valid2'}),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'Access:park_valid1:group_valid1',
        {
            'Menu': json.dumps({'hideMenu': ['52', '55']}),
            'Driver': json.dumps({'tabgps': True}),
        },
    ],
)
@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize(
    'group_id, payload, redis_access_grants, redis_grants, log_values',
    OK_PARAMS,
)
async def test_edit_grants_ok(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        fleet_parks_shard,
        mock_fleet_synchronizer,
        redis_store,
        blackbox_service,
        pgsql,
        endpoint,
        group_id,
        payload,
        redis_access_grants,
        redis_grants,
        log_values,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'user@yandex.ru',
    )
    response = await taxi_dispatcher_access_control.post(
        endpoint,
        params=build_params(endpoint=endpoint, group_id=group_id),
        json=payload,
        headers=build_headers(endpoint=endpoint),
    )
    assert response.status_code == 200, response.text
    assert response.json() == build_response(endpoint, payload)

    access_grants_from_redis = redis_store.hgetall(
        'Access:park_valid1:' + group_id,
    )
    assert parse_redis_grants(access_grants_from_redis) == parse_redis_grants(
        redis_access_grants,
    )
    grants_from_redis = redis_store.hgetall('Grants:park_valid1:' + group_id)
    assert grants_from_redis == redis_grants
    assert mock_fleet_synchronizer.times_called == (
        0 if endpoint == SYNC_ENDPOINT else 1
    )

    log_info = {
        'user_id': ('user1' if endpoint is not SYNC_ENDPOINT else ''),
        'user_name': (
            'Name1' if endpoint is not SYNC_ENDPOINT else 'Tech support'
        ),
        'counts': 1,
        'ip': '127.0.0.1' if endpoint is not SYNC_ENDPOINT else '',
    }
    check_logs(pgsql, log_info, log_values)


BAD_PARAMS = [
    (
        'park_valid1',
        'group_valid1',
        {'grants': [build_grant('grant_invalid', False)]},
        400,
        {'code': 'invalid_grants', 'message': 'Invalid grants'},
    ),
    (
        'park_valid1',
        'group_invalid',
        {'grants': [build_grant('orders', False)]},
        404,
        {'code': 'group_not_found', 'message': 'Group not found'},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park_valid1',
        {
            'user1': json.dumps(
                {'Name': 'Name1', 'Group': 'group_valid1', 'YandexUid': '100'},
            ),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'group_valid1'})},
    ],
)
@pytest.mark.parametrize('endpoint', ENDPOINTS)
@pytest.mark.parametrize(
    'park_id, group_id, payload, expected_code, expected_response', BAD_PARAMS,
)
async def test_edit_grants_bad(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        blackbox_service,
        endpoint,
        park_id,
        group_id,
        payload,
        expected_code,
        expected_response,
):
    blackbox_service.set_user_ticket_info(
        'ticket_valid1', '100', 'user@yandex.ru',
    )
    response = await taxi_dispatcher_access_control.post(
        endpoint,
        params=build_params(
            endpoint=endpoint, park_id=park_id, group_id=group_id,
        ),
        json=payload,
        headers=build_headers(endpoint=endpoint, park_id=park_id),
    )
    assert response.status_code == expected_code
    if expected_code == 400:
        assert response.json()['code'] == expected_response['code']
    else:
        assert response.json() == expected_response
