import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'sync/v1/parks/groups'


def build_request(name='GroupNew', is_super=None):
    request = {'name': name}
    if is_super is not None:
        request['is_super'] = is_super
    return request


def build_response(group_id, payload):
    return {
        'id': group_id,
        'is_super': payload.get('is_super', False),
        'name': payload.get('name', ''),
    }


OK_PARAMS = [
    (
        'group_valid1',
        None,
        {
            b'group_valid1': b'{"Name":"GroupNew"}',
            b'group_valid2': b'{"Name": "Group2"}',
        },
    ),
    (
        'group_valid1',
        True,
        {
            b'group_valid1': b'{"Name":"GroupNew","IsSuper":true}',
            b'group_valid2': b'{"Name": "Group2"}',
        },
    ),
    (
        'group_valid3',
        None,
        {
            b'group_valid1': b'{"Name": "Group1", "IsSuper": true}',
            b'group_valid2': b'{"Name": "Group2"}',
            b'group_valid3': b'{"Name":"GroupNew"}',
        },
    ),
    (
        'group_valid3',
        False,
        {
            b'group_valid1': b'{"Name": "Group1", "IsSuper": true}',
            b'group_valid2': b'{"Name": "Group2"}',
            b'group_valid3': b'{"Name":"GroupNew"}',
        },
    ),
    (
        'group_valid3',
        True,
        {
            b'group_valid2': b'{"Name": "Group2"}',
            b'group_valid3': b'{"Name":"GroupNew","IsSuper":true}',
        },
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
        {
            'group_valid1': json.dumps({'Name': 'Group1', 'IsSuper': True}),
            'group_valid2': json.dumps({'Name': 'Group2'}),
        },
    ],
)
@pytest.mark.parametrize('group_id, is_super, redis_result', OK_PARAMS)
async def test_put_group(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        redis_store,
        group_id,
        is_super,
        redis_result,
):
    request = build_request(is_super=is_super)
    response = await taxi_dispatcher_access_control.put(
        ENDPOINT,
        params={'park_id': 'park_valid1', 'group_id': group_id},
        json=request,
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200, response.text
    assert response.json() == build_response(group_id, request)

    assert redis_store.hgetall('UserGroup:Items:park_valid1') == redis_result


BAD_PARAMS = [
    (
        'park_invalid',
        'group_valid1',
        404,
        {'code': '404', 'message': 'Park not found'},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Group1', 'IsSuper': True})},
    ],
)
@pytest.mark.parametrize(
    'park_id, group_id, expected_code, expected_result', BAD_PARAMS,
)
async def test_put_group_error(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        redis_store,
        park_id,
        group_id,
        expected_code,
        expected_result,
):
    response = await taxi_dispatcher_access_control.put(
        ENDPOINT,
        params={'park_id': park_id, 'group_id': group_id},
        json=build_request(is_super=True),
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_result
