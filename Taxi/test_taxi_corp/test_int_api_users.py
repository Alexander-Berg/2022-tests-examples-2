import pytest

from taxi_corp.api import routes
from taxi_corp.api.common import codes
from test_taxi_corp import corp_users_util

FIELDS_DEFAULT_VALUES = {'limits': [], 'nickname': '', 'is_deleted': False}
USER_PHONES_CONFIG = dict(
    CORP_USER_PHONES_SUPPORTED=corp_users_util.CORP_USER_PHONES_SUPPORTED,
)


@pytest.mark.parametrize(
    [
        'passport_mock',
        'corp_users_response',
        'expected_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client3',
            corp_users_util.CORP_USERS_RESPONSE,
            200,
            corp_users_util.api_user_doc(corp_users_util.BASE_USER_RESPONSE),
            id='user-ok',
        ),
        pytest.param(
            'client3',
            corp_users_util.CORP_USERS_RESPONSE_ERROR,
            404,
            corp_users_util.CORP_USERS_RESPONSE_ERROR,
            id='user-error',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_api_get_user(
        taxi_corp_real_auth_client,
        mock_corp_users,
        passport_mock,
        corp_users_response,
        expected_code,
        expected_response,
):
    mock_corp_users.data.get_user_response = corp_users_response
    mock_corp_users.data.get_user_code = expected_code

    response = await taxi_corp_real_auth_client.get(
        f'{routes.API_PREFIX}/2.0/users/test_user_1',
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_response


@pytest.mark.parametrize(
    [
        'passport_mock',
        'corp_users_search_response',
        'expected_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client3',
            {
                'items': [corp_users_util.CORP_USERS_RESPONSE],
                'limit': 1,
                'offset': 0,
                'total_amount': 1,
            },
            200,
            {
                'items': [
                    corp_users_util.api_user_doc(
                        corp_users_util.BASE_USER_RESPONSE,
                    ),
                ],
                'limit': 1,
                'offset': 0,
                'total_amount': 1,
            },
        ),
    ],
    indirect=['passport_mock'],
)
async def test_api_search_users(
        taxi_corp_real_auth_client,
        mock_corp_users,
        passport_mock,
        corp_users_search_response,
        expected_code,
        expected_response,
):
    mock_corp_users.data.search_users_response = corp_users_search_response
    mock_corp_users.data.search_users_code = expected_code

    params = {'limit': '1', 'offset': '0'}
    response = await taxi_corp_real_auth_client.get(
        f'{routes.API_PREFIX}/2.0/users/search', params=params,
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_response

    assert mock_corp_users.search_users.next_call()['request'].query == dict(
        params, client_id='client3', performer_department_id='dep1',
    )


@pytest.mark.parametrize(
    [
        'passport_mock',
        'cursor',
        'corp_users_list_response',
        'expected_code',
        'expected_response',
    ],
    [
        pytest.param(
            'client3',
            None,
            {
                'items': [corp_users_util.CORP_USERS_RESPONSE],
                'limit': 1,
                'next_cursor': corp_users_util.CORP_USERS_NEXT_CURSOR,
                'total_amount': 1,
            },
            200,
            {
                'items': [
                    corp_users_util.api_user_doc(
                        corp_users_util.BASE_USER_RESPONSE,
                    ),
                ],
                'limit': 1,
                'next_cursor': corp_users_util.CORP_USERS_NEXT_CURSOR,
                'total_amount': 1,
            },
            id='users list with next cursor',
        ),
        pytest.param(
            'client3',
            corp_users_util.CORP_USERS_NEXT_CURSOR,
            {
                'items': [],
                'limit': 1,
                'cursor': corp_users_util.CORP_USERS_NEXT_CURSOR,
                'total_amount': 1,
            },
            200,
            {
                'items': [],
                'limit': 1,
                'cursor': corp_users_util.CORP_USERS_NEXT_CURSOR,
                'total_amount': 1,
            },
            id='empty users list',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_api_list_users(
        taxi_corp_real_auth_client,
        mock_corp_users,
        passport_mock,
        cursor,
        corp_users_list_response,
        expected_code,
        expected_response,
):
    mock_corp_users.data.list_users_response = corp_users_list_response
    mock_corp_users.data.list_users_code = expected_code

    params = {'limit': '1'}
    if cursor is not None:
        params['cursor'] = cursor
    response = await taxi_corp_real_auth_client.get(
        f'{routes.API_PREFIX}/2.0/users', params=params,
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_response

    assert mock_corp_users.list_users.next_call()['request'].query == dict(
        params, client_id='client3',
    )


@pytest.mark.parametrize(
    ['passport_mock', 'post_content'],
    [
        pytest.param(
            'client1', corp_users_util.BASE_USER_REQUEST, id='min fields',
        ),
        pytest.param(
            'client3', corp_users_util.EXTENDED_USER_REQUEST, id='max fields',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(**USER_PHONES_CONFIG)
async def test_success_post_user(
        pd_patch, db, taxi_corp_real_auth_client, passport_mock, post_content,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()
    response = await taxi_corp_real_auth_client.post(
        f'{routes.API_PREFIX}/2.0/users', json=post_content,
    )
    assert response.status == 200
    response_data = await response.json()
    db_user = await db.corp_users.find_one(
        {'_id': response_data['id']},
        projection={
            '_id': False,
            'created': False,
            'updated': False,
            'phone_id': False,
            'email_id': False,
            'personal_phone_id': False,
            'services': False,
        },
    )
    assert db_user.pop('client_id') == passport_mock
    for key, value in db_user.items():
        if key in post_content:
            assert value == post_content[key]
        else:
            if key in FIELDS_DEFAULT_VALUES:
                assert value == FIELDS_DEFAULT_VALUES[key], key
            else:
                assert value is None, key


@pytest.mark.parametrize(
    ['passport_mock', 'post_content', 'status_code'],
    [
        pytest.param(
            'client3', corp_users_util.BASE_USER_REQUEST, 403, id='alien dep',
        ),
        pytest.param(
            'client1',
            {**corp_users_util.BASE_USER_REQUEST, **{'extra_field': ''}},
            400,
            id='with extra field',
        ),
        pytest.param(
            'client1', {'fullname': 'test'}, 400, id='not enough fields',
        ),
        pytest.param(
            'client3',
            corp_users_util.TWO_LIMITS_USER_REQUEST,
            400,
            id='two limits for taxi',
        ),
        pytest.param(
            'client3',
            corp_users_util.ANOTHER_SERVICE_USER_REQUEST,
            400,
            id='try to change limit service in user',
        ),
        pytest.param(
            'client3',
            corp_users_util.DELETED_LIMIT_USER_REQUEST,
            404,
            id='try assign deleted limit',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(**USER_PHONES_CONFIG)
async def test_fail_post_user(
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        post_content,
        status_code,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()
    response = await taxi_corp_real_auth_client.post(
        f'{routes.API_PREFIX}/2.0/users', json=post_content,
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'user_id', 'post_content'],
    [
        pytest.param(
            'client1',
            'client1_user1',
            corp_users_util.BASE_USER_REQUEST,
            id='min fields',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            corp_users_util.EXTENDED_USER_REQUEST,
            id='max_fields',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(**USER_PHONES_CONFIG)
async def test_success_put_user(
        pd_patch,
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        user_id,
        post_content,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()
    response = await taxi_corp_real_auth_client.put(
        f'{routes.API_PREFIX}/2.0/users/{user_id}', json=post_content,
    )
    assert response.status == 200
    db_user = await db.corp_users.find_one(
        {'_id': user_id},
        projection={
            'created': False,
            'updated': False,
            'phone_id': False,
            'email_id': False,
            'personal_phone_id': False,
            'services': False,
            'stat': False,
        },
    )
    assert db_user.pop('_id') == user_id
    assert db_user.pop('client_id') == passport_mock
    for key, value in db_user.items():
        if key in post_content:
            assert value == post_content[key]
        else:
            if key in FIELDS_DEFAULT_VALUES:
                assert value == FIELDS_DEFAULT_VALUES[key], key
            else:
                assert value is None, key


@pytest.mark.parametrize(
    ['passport_mock', 'user_id', 'post_content', 'status_code'],
    [
        pytest.param(
            'client1',
            'not_existed_user',
            corp_users_util.BASE_USER_REQUEST,
            404,
            id='not existed user',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            corp_users_util.BASE_USER_REQUEST,
            403,
            id='try change to alien dep',
        ),
        pytest.param(
            'client3',
            'test_user_2',
            {**corp_users_util.BASE_USER_REQUEST, **{'department_id': 'dep1'}},
            403,
            id='user from another dep',
        ),
        pytest.param(
            'client1',
            'test_user_1',
            corp_users_util.BASE_USER_REQUEST,
            403,
            id='user from another client',
        ),
        pytest.param(
            'client1',
            'client1_user1',
            dict(
                corp_users_util.BASE_USER_REQUEST,
                is_deleted=True,
                is_active=False,
            ),
            400,
            id='cannot mark user as deleted',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            {
                **corp_users_util.BASE_USER_REQUEST,
                'is_deleted': True,
                'department_id': 'dep1',
            },
            400,
            id='is_deleted and is_active',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(**USER_PHONES_CONFIG)
async def test_fail_put_user(
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        user_id,
        post_content,
        status_code,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()
    response = await taxi_corp_real_auth_client.put(
        f'{routes.API_PREFIX}/2.0/users/{user_id}', json=post_content,
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'user_id', 'post_content'],
    [
        pytest.param(
            'client1',
            'client1_user1',
            corp_users_util.BASE_USER_REQUEST,
            id='min fields',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            corp_users_util.EXTENDED_USER_REQUEST,
            id='max_fields',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(CORP_COUNTERS_ENABLED=True, **USER_PHONES_CONFIG)
async def test_user_counters_in_limits(
        pd_patch,
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        user_id,
        post_content,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()

    old_user = await db.corp_users.find_one(
        {'_id': user_id}, projection=['limits', 'counters'],
    )

    old_limit_ids = {limit['limit_id'] for limit in old_user.get('limits', [])}
    new_limit_ids = {
        limit['limit_id'] for limit in post_content.get('limits', [])
    }
    limits_before_updating = await db.corp_limits.find(
        {'_id': {'$in': list(old_limit_ids | new_limit_ids)}},
    ).to_list(None)
    limits_before_updating_by_ids = {
        limit['_id']: limit for limit in limits_before_updating
    }

    response = await taxi_corp_real_auth_client.put(
        f'{routes.API_PREFIX}/2.0/users/{user_id}', json=post_content,
    )
    assert response.status == 200

    limits_after_updating = await db.corp_limits.find(
        {'_id': {'$in': list(old_limit_ids | new_limit_ids)}},
    ).to_list(None)
    limits_after_updating_by_ids = {
        limit['_id']: limit for limit in limits_after_updating
    }

    for limit_id, limit in limits_after_updating_by_ids.items():
        limit_after_updating_counters = limit['counters']['users']
        limit_before_updating_counters = limits_before_updating_by_ids[
            limit_id
        ]['counters']['users']
        if limit_id in old_limit_ids and limit_id in new_limit_ids:
            assert (
                limit_before_updating_counters == limit_after_updating_counters
            )
        elif limit_id in old_limit_ids:
            assert (
                limit_before_updating_counters - 1
                == limit_after_updating_counters
            )
        else:
            assert (
                limit_before_updating_counters + 1
                == limit_after_updating_counters
            )


@pytest.mark.parametrize(
    ['passport_mock', 'user_id', 'expected_code', 'expected_content'],
    [
        pytest.param('client3', 'test_user_1', 200, {}, id='archive-ok'),
        pytest.param(
            'client3',
            'test_user_x',
            404,
            {
                'errors': [{'text': 'User not found', 'code': 'GENERAL'}],
                'message': 'User not found',
                'code': 'GENERAL',
            },
            id='archive-error-404',
        ),
        pytest.param(
            'client3',
            'test_user_6',
            400,
            {
                'errors': [
                    {
                        'text': codes.DRIVE_LIMIT_IN_PROGRESS.text,
                        'code': codes.DRIVE_LIMIT_IN_PROGRESS.error_code,
                    },
                ],
                'message': codes.DRIVE_LIMIT_IN_PROGRESS.text,
                'code': codes.DRIVE_LIMIT_IN_PROGRESS.error_code,
            },
            id='user-with-active-drive-stq',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_archive_user(
        passport_mock,
        db,
        taxi_corp_real_auth_client,
        user_id,
        expected_code,
        expected_content,
):
    if expected_code != 404:
        doc_before = await db.corp_users.find_one({'_id': user_id})
        assert not doc_before.get('is_deleted')

    response = await taxi_corp_real_auth_client.post(
        f'{routes.API_PREFIX}/2.0/users/{user_id}/archive', json={},
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_content

    doc_after = await db.corp_users.find_one({'_id': user_id})
    if expected_code == 404:
        assert doc_after is None
    elif expected_code == 200:
        assert doc_after['is_deleted'] is True
        assert doc_after['is_active'] is False
        if 'drive' in doc_before['services']:
            assert 'task_id' not in doc_before['services']['drive']
            assert doc_after['services']['drive']['task_id']
    else:
        assert doc_after.get('is_deleted') == doc_before.get('is_deleted')
