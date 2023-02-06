# pylint: disable=C0302

import json

import pytest

from tests_dispatcher_access_control import utils

ENDPOINT = 'v1/parks/users/list'

TEST_NO_SUCH_PASSPORT_UID_SEARCH = [
    ('100500', 'park1', 200, {'users': [], 'limit': 100, 'offset': 0}),
    (
        'non_existent_passport_uid',
        'park2',
        200,
        {'users': [], 'limit': 100, 'offset': 0},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': json.dumps({'YandexUid': '1'}),
            'user2': json.dumps({'YandexUid': '2'}),
        },
    ],
    ['hmset', 'User:Items:park2', {'user2': json.dumps({'YandexUid': '1'})}],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, code, expected_response',
    TEST_NO_SUCH_PASSPORT_UID_SEARCH,
)
async def test_no_such_passport_uid_search(
        taxi_dispatcher_access_control,
        passport_uid,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': [passport_uid]},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_NO_SUCH_PARK_ID_SEARCH = [
    (
        '1',
        'non_existent_park_id',
        200,
        {'users': [], 'limit': 100, 'offset': 0},
    ),
    (
        '2',
        'non_existent_park_id',
        200,
        {'users': [], 'limit': 100, 'offset': 0},
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': json.dumps({'YandexUid': '1'}),
            'user2': json.dumps({'YandexUid': '2'}),
        },
    ],
    ['hmset', 'User:Items:park2', {'user2': json.dumps({'YandexUid': '1'})}],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, code, expected_response',
    TEST_NO_SUCH_PARK_ID_SEARCH,
)
async def test_no_such_park_id_search(
        taxi_dispatcher_access_control,
        passport_uid,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': [passport_uid]},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_SINGLE_USER_RETRIEVAL = [
    (
        '1',
        'park1',
        200,
        {'users': [utils.make_user(1)], 'limit': 100, 'offset': 0},
    ),
    (
        '2',
        'park1',
        200,
        {'users': [utils.make_user(2)], 'limit': 100, 'offset': 0},
    ),
    (
        '3',
        'park1',
        200,
        {'users': [utils.make_user(3)], 'limit': 100, 'offset': 0},
    ),
    (
        '1',
        'park2',
        200,
        {
            'users': [utils.make_user(2, 'park2', '1')],
            'limit': 100,
            'offset': 0,
        },
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
    ['hmset', 'User:Items:park2', {'user2': utils.make_redis_user('1')}],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, code, expected_response',
    TEST_SINGLE_USER_RETRIEVAL,
)
async def test_single_user_retrieval(
        taxi_dispatcher_access_control,
        passport_uid,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': [passport_uid]},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_GET_USER_BY_ID = [
    (
        'user1',
        'park1',
        200,
        {'users': [utils.make_user(1)], 'limit': 100, 'offset': 0},
    ),
    (
        'user2',
        'park1',
        200,
        {'users': [utils.make_user(2)], 'limit': 100, 'offset': 0},
    ),
    (
        'user3',
        'park1',
        200,
        {'users': [utils.make_user(3)], 'limit': 100, 'offset': 0},
    ),
    (
        'user2',
        'park2',
        200,
        {
            'users': [utils.make_user(2, 'park2', '1')],
            'limit': 100,
            'offset': 0,
        },
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
    ['hmset', 'User:Items:park2', {'user2': utils.make_redis_user('1')}],
)
@pytest.mark.parametrize(
    'user_id, park_id, code, expected_response', TEST_GET_USER_BY_ID,
)
async def test_get_user_by_id(
        taxi_dispatcher_access_control,
        user_id,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {'park': {'id': park_id}, 'user': {'ids': [user_id]}},
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


@pytest.mark.redis_store(
    ['hmset', 'User:Items:park1', {'user1': json.dumps({'YandexUid': '1'})}],
)
async def test_user_without_extra_fields_retrieval(
        taxi_dispatcher_access_control,
):
    request_body = {
        'query': {'park': {'id': 'park1'}, 'user': {'passport_uid': ['1']}},
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == {
        'limit': 100,
        'offset': 0,
        'users': [
            {
                'id': 'user1',
                'is_confirmed': False,
                'is_enabled': False,
                'is_superuser': False,
                'is_multifactor_authentication_required': False,
                'is_usage_consent_accepted': False,
                'park_id': 'park1',
                'passport_uid': '1',
                'yandex_uid': '1',
            },
        ],
    }


TEST_MANY_USERS = [
    (
        ['0001', '0003', '0100'],
        'park1',
        200,
        {
            'users': utils.make_users(['0001', '0003', '0100']),
            'limit': 100,
            'offset': 0,
        },
    ),
    (
        ['{:04d}'.format(index) for index in range(100, 200)],
        'park1',
        200,
        {
            'users': utils.make_users(
                ['{:04d}'.format(index) for index in range(100, 200)],
            ),
            'limit': 100,
            'offset': 0,
        },
    ),
    (
        [],
        'park1',
        200,
        {
            'users': utils.make_users(
                ['{:04d}'.format(index) for index in range(1, 101)],
            ),
            'limit': 100,
            'offset': 0,
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        dict(
            zip(
                [
                    'user' + str_index
                    for str_index in [
                        '{:04d}'.format(index) for index in range(1, 201)
                    ]
                ],
                [
                    json.dumps(
                        {
                            'YandexUid': str_index,
                            'Group': utils.DEFAULT_GROUP_ID,
                            'Email': utils.DEFAULT_EMAIL,
                            'Enable': utils.DEFAULT_ENABLE,
                        },
                    )
                    for str_index in [
                        '{:04d}'.format(index) for index in range(1, 201)
                    ]
                ],
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'passport_uids, park_id, code, expected_response', TEST_MANY_USERS,
)
async def test_many_users(
        taxi_dispatcher_access_control,
        passport_uids,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': passport_uids},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_EMPTY_PASSPORT_UIDS = [
    (
        'park1',
        200,
        {'users': utils.make_users([1, 2, 3]), 'limit': 100, 'offset': 0},
    ),
    ('non_existent_park_id', 200, {'users': [], 'limit': 100, 'offset': 0}),
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
    'park_id, code, expected_response', TEST_EMPTY_PASSPORT_UIDS,
)
async def test_empty_passport_uids(
        taxi_dispatcher_access_control, park_id, code, expected_response,
):
    request_body = {
        'query': {'park': {'id': park_id}, 'user': {'passport_uid': []}},
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_REQUEST_WITH_NO_USER_FIELD = [
    (
        'park1',
        200,
        {'users': utils.make_users([1, 2, 3]), 'limit': 100, 'offset': 0},
    ),
    ('non_existent_park_id', 200, {'users': [], 'limit': 100, 'offset': 0}),
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
    'park_id, code, expected_response', TEST_REQUEST_WITH_NO_USER_FIELD,
)
async def test_request_with_no_user_field(
        taxi_dispatcher_access_control, park_id, code, expected_response,
):
    request_body = {'query': {'park': {'id': park_id}}, 'limit': 100}
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_ADDITIONAL_USER_FIELDS = [
    (
        ['1', '2', '3'],
        'park1',
        200,
        {
            'users': [
                {
                    'id': 'user3',
                    'park_id': 'park1',
                    'passport_uid': '3',
                    'yandex_uid': '3',
                    'is_enabled': True,
                    'is_superuser': False,
                    'is_confirmed': True,
                    'is_multifactor_authentication_required': False,
                    'is_usage_consent_accepted': True,
                    'usage_consent_acceptance_date': (
                        '2018-12-05T12:59:52.949646+00:00'
                    ),
                },
                {
                    'id': 'user1',
                    'park_id': 'park1',
                    'passport_uid': '1',
                    'yandex_uid': '1',
                    'display_name': 'Alice',
                    'email': 'a@yandex.ru',
                    'phone': '79109042201',
                    'group_id': '21',
                    'group_name': 'Director',
                    'is_enabled': True,
                    'is_superuser': True,
                    'is_confirmed': True,
                    'is_multifactor_authentication_required': True,
                    'is_usage_consent_accepted': False,
                },
                {
                    'id': 'user2',
                    'park_id': 'park1',
                    'passport_uid': '2',
                    'yandex_uid': '2',
                    'display_name': 'Bob Smith',
                    'email': 'bob@yandex.ru',
                    'phone': '79139042204',
                    'is_enabled': False,
                    'is_superuser': False,
                    'is_confirmed': False,
                    'is_multifactor_authentication_required': False,
                    'is_usage_consent_accepted': True,
                },
            ],
            'offset': 0,
            'limit': 100,
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': json.dumps(
                {
                    'YandexUid': '1',
                    'Name': 'Alice',
                    'Email': 'a@yandex.ru',
                    'Phones': '79109042201',
                    'Group': '21',
                    'Enable': True,
                    'IsMultiFactorAuthenticationRequired': True,
                    'IsSuperUser': True,
                    'YandexConfirmed': True,
                },
            ),
            'user2': json.dumps(
                {
                    'YandexUid': '2',
                    'Name': 'Bob Smith',
                    'Email': 'bob@yandex.ru',
                    'Phones': '79139042204',
                    'UsageConsentAcceptance': '2008-INVALID_DATETIME-1:00',
                },
            ),
            'user3': json.dumps(
                {
                    'YandexUid': '3',
                    'Enable': True,
                    'IsSuperUser': False,
                    'YandexConfirmed': True,
                    'UsageConsentAcceptance': '2018-12-05T12:59:52.949646Z',
                },
            ),
        },
    ],
    [
        'hmset',
        'UserGroup:Items:park1',
        {'21': json.dumps({'Name': 'Director', 'IsSuper': True})},
    ],
)
@pytest.mark.parametrize(
    'passport_uids, park_id, code, expected_response',
    TEST_ADDITIONAL_USER_FIELDS,
)
async def test_additional_user_fields(
        taxi_dispatcher_access_control,
        passport_uids,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': passport_uids},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_DEPRECATED_YANDEX_UID_PARAM = [
    (
        ['1', '2', '3'],
        'park1',
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
    'passport_uids, park_id, code, expected_response',
    TEST_DEPRECATED_YANDEX_UID_PARAM,
)
async def test_deprecated_yandex_uid_param(
        taxi_dispatcher_access_control,
        passport_uids,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'yandex_uid': passport_uids},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_DEPRECATED_YANDEX_UID_OVERRIDE = [
    (
        ['1', '2', '3'],
        ['1'],
        'park1',
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
    'passport_uids, yandex_uids, park_id, code, expected_response',
    TEST_DEPRECATED_YANDEX_UID_OVERRIDE,
)
async def test_deprecated_yandex_uid_override(
        taxi_dispatcher_access_control,
        passport_uids,
        yandex_uids,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'yandex_uid': yandex_uids, 'passport_uid': passport_uids},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_USERS_WITH_NO_PASSPORT_UID_FILTERING = [
    (
        ['1', '2'],
        'park1',
        200,
        {'users': utils.make_users([1]), 'limit': 100, 'offset': 0},
    ),
    (
        [],
        'park1',
        200,
        {
            'users': utils.make_users([1]) + [
                {
                    'id': 'user2',
                    'park_id': 'park1',
                    'is_enabled': False,
                    'is_confirmed': False,
                    'is_superuser': False,
                    'is_multifactor_authentication_required': False,
                    'is_usage_consent_accepted': False,
                },
            ],
            'limit': 100,
            'offset': 0,
        },
    ),
    (['3'], 'park1', 200, {'users': [], 'limit': 100, 'offset': 0}),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {'user1': utils.make_redis_user('1'), 'user2': json.dumps({})},
    ],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, code, expected_response',
    TEST_USERS_WITH_NO_PASSPORT_UID_FILTERING,
)
async def test_users_with_no_passport_uid_filtering(
        taxi_dispatcher_access_control,
        passport_uid,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': passport_uid},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_IS_ENABLED_FILTERING = [
    (
        ['1', '2', '3'],
        'park1',
        True,
        200,
        {'users': utils.make_users([1, 3]), 'limit': 100, 'offset': 0},
    ),
    (
        ['1', '2', '3'],
        'park1',
        False,
        200,
        {
            'users': [utils.make_user(2, is_enabled=False)],
            'limit': 100,
            'offset': 0,
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': json.dumps(
                {
                    'YandexUid': '1',
                    'Group': utils.DEFAULT_GROUP_ID,
                    'Enable': True,
                    'Email': utils.DEFAULT_EMAIL,
                },
            ),
            'user2': json.dumps(
                {
                    'YandexUid': '2',
                    'Group': utils.DEFAULT_GROUP_ID,
                    'Enable': False,
                    'Email': utils.DEFAULT_EMAIL,
                },
            ),
            'user3': json.dumps(
                {
                    'YandexUid': '3',
                    'Group': utils.DEFAULT_GROUP_ID,
                    'Email': utils.DEFAULT_EMAIL,
                    'Enable': utils.DEFAULT_ENABLE,
                },
            ),
        },
    ],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, is_enabled, code, expected_response',
    TEST_IS_ENABLED_FILTERING,
)
async def test_is_enabled_filtering(
        taxi_dispatcher_access_control,
        passport_uid,
        park_id,
        is_enabled,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': passport_uid, 'is_enabled': is_enabled},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_ENABLED_NO_PASSPORT_UID_FILTERING = [
    (
        False,
        'park1',
        200,
        {
            'users': [utils.make_user(2, is_enabled=False)],
            'limit': 100,
            'offset': 0,
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': json.dumps(
                {
                    'YandexUid': '1',
                    'Group': utils.DEFAULT_GROUP_ID,
                    'Enable': True,
                    'Email': utils.DEFAULT_EMAIL,
                },
            ),
            'user2': json.dumps(
                {
                    'YandexUid': '2',
                    'Group': utils.DEFAULT_GROUP_ID,
                    'Enable': False,
                    'Email': utils.DEFAULT_EMAIL,
                },
            ),
            'user3': utils.make_redis_user('3'),
        },
    ],
)
@pytest.mark.parametrize(
    'is_enabled, park_id, code, expected_response',
    TEST_ENABLED_NO_PASSPORT_UID_FILTERING,
)
async def test_enabled_no_passport_uid_filtering(
        taxi_dispatcher_access_control,
        is_enabled,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {'park': {'id': park_id}, 'user': {'is_enabled': is_enabled}},
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_MIXED_UP_PASSPORT_UID_FILTERING = [
    (
        ['7', '4', '9', '6', '8', '1'],
        'park1',
        200,
        {
            'users': utils.make_users([1, 4, 6, 7, 8, 9]),
            'limit': 100,
            'offset': 0,
        },
    ),
    (
        ['7', '13', '4', '21', '9', '6', '114', '8', '1'],
        'park1',
        200,
        {
            'users': utils.make_users([1, 4, 6, 7, 8, 9]),
            'limit': 100,
            'offset': 0,
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        dict(
            zip(
                [
                    'user' + str_index
                    for str_index in [str(index) for index in range(10, 0, -1)]
                ],
                [
                    json.dumps(
                        {
                            'YandexUid': str_index,
                            'Group': utils.DEFAULT_GROUP_ID,
                            'Email': utils.DEFAULT_EMAIL,
                            'Enable': utils.DEFAULT_ENABLE,
                        },
                    )
                    for str_index in [str(index) for index in range(10, 0, -1)]
                ],
            ),
        ),
    ],
)
@pytest.mark.parametrize(
    'passport_uid, park_id, code, expected_response',
    TEST_MIXED_UP_PASSPORT_UID_FILTERING,
)
async def test_mixed_up_passport_uid_filtering(
        taxi_dispatcher_access_control,
        passport_uid,
        park_id,
        code,
        expected_response,
):
    request_body = {
        'query': {
            'park': {'id': park_id},
            'user': {'passport_uid': passport_uid},
        },
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == code
    assert response.json() == expected_response


TEST_SEARCH_FILTERING = [
    (
        'liC',
        {
            'limit': 100,
            'offset': 0,
            'users': [
                {
                    'display_name': 'Alice',
                    'email': 'user1@yandex.ru',
                    'group_id': 'gid1',
                    'id': 'user1',
                    'is_confirmed': False,
                    'is_enabled': True,
                    'is_multifactor_authentication_required': False,
                    'is_superuser': False,
                    'is_usage_consent_accepted': False,
                    'park_id': 'park1',
                    'passport_uid': '1',
                    'yandex_uid': '1',
                },
            ],
        },
    ),
    (
        'SeR2@',
        {
            'limit': 100,
            'offset': 0,
            'users': [
                {
                    'display_name': 'Betty',
                    'email': 'user2@yandex.ru',
                    'group_id': 'gid1',
                    'id': 'user2',
                    'is_confirmed': False,
                    'is_enabled': False,
                    'is_multifactor_authentication_required': False,
                    'is_superuser': False,
                    'is_usage_consent_accepted': False,
                    'park_id': 'park1',
                    'passport_uid': '2',
                    'yandex_uid': '2',
                },
            ],
        },
    ),
]


@pytest.mark.redis_store(
    [
        'hmset',
        'User:Items:park1',
        {
            'user1': json.dumps(
                {
                    'Email': 'user1@yandex.ru',
                    'Enable': True,
                    'Group': utils.DEFAULT_GROUP_ID,
                    'Name': 'Alice',
                    'YandexUid': '1',
                },
            ),
            'user2': json.dumps(
                {
                    'Email': 'user2@yandex.ru',
                    'Enable': False,
                    'Group': utils.DEFAULT_GROUP_ID,
                    'Name': 'Betty',
                    'YandexUid': '2',
                },
            ),
            'user3': json.dumps(
                {
                    'Email': 'user3@yandex.ru',
                    'Enable': utils.DEFAULT_ENABLE,
                    'Group': utils.DEFAULT_GROUP_ID,
                    'Name': 'Charlie',
                    'YandexUid': '3',
                },
            ),
        },
    ],
)
@pytest.mark.parametrize('search, expected_response', TEST_SEARCH_FILTERING)
async def test_search_filtering(
        taxi_dispatcher_access_control, search, expected_response,
):
    request_body = {
        'query': {'park': {'id': 'park1'}, 'user': {'search': search}},
        'limit': 100,
    }
    response = await taxi_dispatcher_access_control.post(
        ENDPOINT, json=request_body, headers=utils.SERVICE_TICKET_HEADER,
    )
    assert response.status_code == 200
    assert response.json() == expected_response
