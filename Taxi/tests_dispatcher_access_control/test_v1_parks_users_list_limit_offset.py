import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/users/list'

TEST_LIMIT_OFFSET = [
    (
        ['1', '2', '3', '4', '5'],
        'park1',
        1,
        0,
        200,
        {'users': utils.make_users([1]), 'limit': 1, 'offset': 0},
    ),
    (
        ['1', '2', '3', '4', '5'],
        'park1',
        1,
        1,
        200,
        {'users': utils.make_users([2]), 'limit': 1, 'offset': 1},
    ),
    (
        ['1', '2', '3', '4', '5'],
        'park1',
        100,
        0,
        200,
        {
            'users': utils.make_users([1, 2, 3, 4, 5]),
            'limit': 100,
            'offset': 0,
        },
    ),
    (
        ['1', '2', '3', '4', '5'],
        'park1',
        100,
        500,
        200,
        {'users': [], 'limit': 100, 'offset': 500},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': utils.make_redis_user('1'),
            'user2': utils.make_redis_user('2'),
            'user3': utils.make_redis_user('3'),
            'user4': utils.make_redis_user('4'),
            'user5': utils.make_redis_user('5'),
        },
    ],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, limit, offset, code, expected_response',
    TEST_LIMIT_OFFSET,
)
async def test_limit_offset(
        taxi_dispatcher_access_control,
        passport_uid,
        limit,
        offset,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': passport_uid},
        },
        'limit': limit,
        'offset': offset,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_LIMIT_NO_OFFSET = [
    (
        ['1', '2', '3'],
        'park1',
        1,
        200,
        {'users': utils.make_users([1]), 'limit': 1, 'offset': 0},
    ),
    (
        ['1', '2', '3', '4', '5'],
        'park1',
        2,
        200,
        {'users': utils.make_users([1, 2]), 'limit': 2, 'offset': 0},
    ),
    (
        ['1', '2', '3'],
        'park1',
        100,
        200,
        {'users': utils.make_users([1, 2, 3]), 'limit': 100, 'offset': 0},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': utils.make_redis_user('1'),
            'user2': utils.make_redis_user('2'),
            'user3': utils.make_redis_user('3'),
        },
    ],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, limit, code, expected_response',
    TEST_LIMIT_NO_OFFSET,
)
async def test_limit_no_offset(
        taxi_dispatcher_access_control,
        passport_uid,
        limit,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': passport_uid},
        },
        'limit': limit,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_USER_SORT_PARAMS = [
    (
        None,
        [
            utils.make_user(
                id_='1',
                display_name='Ann',
                group_id='group1',
                group_name='Women',
            ),
            utils.make_user(
                id_='3',
                display_name='Bob',
                group_id='group2',
                group_name='Men',
            ),
            utils.make_user(
                id_='2',
                display_name='Mike',
                group_id='group2',
                group_name='Men',
            ),
        ],
    ),
    (
        [{'field': 'group_name', 'order': 'asc'}],
        [
            utils.make_user(
                id_='2',
                display_name='Mike',
                group_id='group2',
                group_name='Men',
            ),
            utils.make_user(
                id_='3',
                display_name='Bob',
                group_id='group2',
                group_name='Men',
            ),
            utils.make_user(
                id_='1',
                display_name='Ann',
                group_id='group1',
                group_name='Women',
            ),
        ],
    ),
    (
        [
            {'field': 'group_name', 'order': 'asc'},
            {'field': 'display_name', 'order': 'asc'},
        ],
        [
            utils.make_user(
                id_='3',
                display_name='Bob',
                group_id='group2',
                group_name='Men',
            ),
            utils.make_user(
                id_='2',
                display_name='Mike',
                group_id='group2',
                group_name='Men',
            ),
            utils.make_user(
                id_='1',
                display_name='Ann',
                group_id='group1',
                group_name='Women',
            ),
        ],
    ),
    (
        [
            {'field': 'group_name', 'order': 'desc'},
            {'field': 'display_name', 'order': 'desc'},
        ],
        [
            utils.make_user(
                id_='1',
                display_name='Ann',
                group_id='group1',
                group_name='Women',
            ),
            utils.make_user(
                id_='2',
                display_name='Mike',
                group_id='group2',
                group_name='Men',
            ),
            utils.make_user(
                id_='3',
                display_name='Bob',
                group_id='group2',
                group_name='Men',
            ),
        ],
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'UserGroup:Items:park1',
        {'group1': json.dumps({'Name': 'Women'})},
    ],
    [
        'hmset',
        'UserGroup:Items:park1',
        {'group2': json.dumps({'Name': 'Men'})},
    ],
)
@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': json.dumps(
                {
                    'Name': 'Ann',
                    'Group': 'group1',
                    'Email': utils.DEFAULT_EMAIL,
                    'Enable': utils.DEFAULT_ENABLE,
                    'YandexUid': '1',
                },
            ),
            'user2': json.dumps(
                {
                    'Name': 'Mike',
                    'Group': 'group2',
                    'Email': utils.DEFAULT_EMAIL,
                    'Enable': utils.DEFAULT_ENABLE,
                    'YandexUid': '2',
                },
            ),
            'user3': json.dumps(
                {
                    'Name': 'Bob',
                    'Group': 'group2',
                    'Email': utils.DEFAULT_EMAIL,
                    'Enable': utils.DEFAULT_ENABLE,
                    'YandexUid': '3',
                },
            ),
        },
    ],
)
@pytest.mark.parametrize('sort_modes, expected_users', TEST_USER_SORT_PARAMS)
async def test_user_sort(
        taxi_dispatcher_access_control, sort_modes, expected_users,
):
    request_body = {'query': {'park': {'id': 'park1'}}, 'limit': 100}
    if sort_modes:
        request_body['sort_by'] = sort_modes

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )

    assert response.status_code == 200, response.text()
    assert response.json()['users'] == expected_users


BAD_USER_SORT_PARAMS = [
    ([{'field': 'invalid', 'order': 'desc'}],),
    ([{'field': 'group_name', 'order': 'invalid'}],),
    ([],),
]


@pytest.mark.parametrize('sort_modes', BAD_USER_SORT_PARAMS)
async def test_user_sort_fail(taxi_dispatcher_access_control, sort_modes):
    request_body = {'query': {'park': {'id': 'park1'}}, 'limit': 100}
    request_body['sort_by'] = sort_modes

    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )

    assert response.status_code == 400, response.text
    assert response.json()['code'] == '400'
