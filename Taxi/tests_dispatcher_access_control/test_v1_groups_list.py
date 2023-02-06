import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/groups/list'

OK_REQUEST = {'query': {'park': {'id': 'park1'}}}


async def test_no_groups(taxi_dispatcher_access_control):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=OK_REQUEST,
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == {'groups': []}


@pytest.mark.redis_store(
    ['hmset', 'UserGroup:Items:park1', {'1': json.dumps({'Name': 'Group1'})}],
    ['hmset', 'UserGroup:Items:park2', {'2': json.dumps({'Name': 'Group2'})}],
)
async def test_single_group_retrieval(taxi_dispatcher_access_control):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=OK_REQUEST,
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == {
        'groups': [
            {'id': '1', 'name': 'Group1', 'is_super': False, 'size': 0},
        ],
    }


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park1',
        {'3': json.dumps({'Name': 'Group3', 'IsSuper': True})},
    ],
    ['hmset', 'UserGroup:Items:park1', {'4': json.dumps({'Name': 'Group4'})}],
    ['hmset', 'UserGroup:Items:park1', {'5': json.dumps({'Name': 'Group5'})}],
)
async def test_multiple_group_retrieval(taxi_dispatcher_access_control):
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT,
        json=OK_REQUEST,
        headers={'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET},
    )
    assert response.status_code == 200
    assert response.json() == {
        'groups': [
            {'id': '3', 'name': 'Group3', 'is_super': True, 'size': 0},
            {'id': '4', 'name': 'Group4', 'is_super': False, 'size': 0},
            {'id': '5', 'name': 'Group5', 'is_super': False, 'size': 0},
        ],
    }
