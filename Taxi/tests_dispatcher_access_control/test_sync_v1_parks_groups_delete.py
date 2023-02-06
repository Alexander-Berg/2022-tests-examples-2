import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'sync/v1/parks/groups'


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park_valid1',
        {'group_valid1': json.dumps({'Name': 'Group1', 'IsSuper': True})},
    ],
)
async def test_delete_group_ok(
        taxi_dispatcher_access_control, mock_fleet_parks_list, redis_store,
):
    response = await taxi_dispatcher_access_control.delete(
        ENDPOINT,
        params={'park_id': 'park_valid1', 'group_id': 'group_valid1'},
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200, response.text

    assert (
        redis_store.hget('UserGroup:Items:park_valid1', 'group_valid1') is None
    )


BAD_PARAMS = [
    (
        'park_invalid',
        'group_valid1',
        404,
        {'code': '404', 'message': 'Park not found'},
    ),
    (
        'park_valid1',
        'group_invalid',
        404,
        {'code': '404', 'message': 'Group not found'},
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
async def test_delete_group_error(
        taxi_dispatcher_access_control,
        mock_fleet_parks_list,
        redis_store,
        park_id,
        group_id,
        expected_code,
        expected_result,
):
    response = await taxi_dispatcher_access_control.delete(
        ENDPOINT,
        params={'park_id': park_id, 'group_id': group_id},
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == expected_code, response.text
    assert response.json() == expected_result
