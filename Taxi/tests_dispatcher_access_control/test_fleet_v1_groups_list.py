import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'fleet/dac/v1/parks/groups/list'

HEADERS = {
    'X-Park-ID': 'park1',
    'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
}


def build_headers(accept_language=None):
    headers = {
        'X-Park-ID': 'park1',
        'X-Ya-Service-Ticket': utils.MOCK_SERVICE_TICKET,
    }
    if accept_language is not None:
        headers['Accept-Language'] = accept_language
    return headers


async def test_no_groups(taxi_dispatcher_access_control):
    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {'groups': []}


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': utils.make_redis_user(uid='1', group='1'),
            'user2': utils.make_redis_user(uid='2', group='1'),
            'user3': utils.make_redis_user(uid='3', group='1'),
            'user4': utils.make_redis_user(uid='4', group='1'),
            'user5': utils.make_redis_user(uid='5', group='1'),
        },
    ],
)
@pytest.mark.redis_store(
    ['hmset', 'UserGroup:Items:park1', {'1': json.dumps({'Name': 'Group1'})}],
    ['hmset', 'UserGroup:Items:park2', {'2': json.dumps({'Name': 'Group2'})}],
)
async def test_single_group_retrieval(taxi_dispatcher_access_control):
    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'groups': [
            {'id': '1', 'is_super': False, 'name': 'Group1', 'size': 5},
        ],
    }


LOCALIZED_PARAMS = [
    (
        'ru',
        {
            'groups': [
                {'id': '1', 'is_super': True, 'name': 'Директор', 'size': 1},
                {
                    'id': '2',
                    'is_super': False,
                    'name': 'Администратор',
                    'size': 1,
                },
                {'id': '3', 'is_super': False, 'name': 'Диспетчер', 'size': 1},
            ],
        },
    ),
    (
        'en',
        {
            'groups': [
                {'id': '1', 'is_super': True, 'name': 'Director', 'size': 1},
                {
                    'id': '2',
                    'is_super': False,
                    'name': 'Administrator',
                    'size': 1,
                },
                {
                    'id': '3',
                    'is_super': False,
                    'name': 'Dispatcher',
                    'size': 1,
                },
            ],
        },
    ),
    (
        None,
        {
            'groups': [
                {'id': '1', 'is_super': True, 'name': 'Директор', 'size': 1},
                {
                    'id': '2',
                    'is_super': False,
                    'name': 'Администратор',
                    'size': 1,
                },
                {'id': '3', 'is_super': False, 'name': 'Диспетчер', 'size': 1},
            ],
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': utils.make_redis_user(uid='1', group='1'),
            'user2': utils.make_redis_user(uid='2', group='2'),
            'user3': utils.make_redis_user(uid='3', group='3'),
        },
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park1',
        {'1': json.dumps({'Name': 'Директор', 'IsSuper': True})},
    ],
    [
        'hmset',
        'UserGroup:Items:park1',
        {'2': json.dumps({'Name': 'Администратор'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park1',
        {'3': json.dumps({'Name': 'Диспетчер'})},
    ],
)
@pytest.mark.parametrize(
    'accept_language, expected_response', LOCALIZED_PARAMS,
)
async def test_localized_groups(
        taxi_dispatcher_access_control, accept_language, expected_response,
):
    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, headers=build_headers(accept_language=accept_language),
    )
    assert response.status_code == 200, response.text
    assert response.json() == expected_response


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': utils.make_redis_user(uid='1', group='3'),
            'user2': utils.make_redis_user(uid='2', group='3'),
            'user3': utils.make_redis_user(uid='3', group='3'),
            'user4': utils.make_redis_user(uid='4', group='4'),
            'user5': utils.make_redis_user(uid='5', group='4'),
        },
    ],
)
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
    response = await taxi_dispatcher_access_control.get(
        ENDPOINT, headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    assert response.json() == {
        'groups': [
            {'id': '3', 'is_super': True, 'name': 'Group3', 'size': 3},
            {'id': '4', 'is_super': False, 'name': 'Group4', 'size': 2},
            {'id': '5', 'is_super': False, 'name': 'Group5', 'size': 0},
        ],
    }
