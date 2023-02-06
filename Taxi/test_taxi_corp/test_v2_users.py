import pytest

from test_taxi_corp import corp_users_util

FIELDS_DEFAULT_VALUES = {'limits': [], 'nickname': ''}
USER_PHONES_CONFIG = dict(
    CORP_USER_PHONES_SUPPORTED=corp_users_util.CORP_USER_PHONES_SUPPORTED,
)
LONG_DEFAULT_CC = 'cc' * 256 + '_'  # 513 symbols
_v2 = corp_users_util.v2_user_doc  # pylint: disable=invalid-name


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
            corp_users_util.BASE_USER_RESPONSE,
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
async def test_get_user_proxy(
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
        '/2.0/users/{}'.format('test_user_1'),
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
                'items': [corp_users_util.BASE_USER_RESPONSE],
                'limit': 1,
                'offset': 0,
                'total_amount': 1,
            },
            id='common-flow',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_search_users_proxy(
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
        '/2.0/users', params=params,
    )
    assert response.status == expected_code
    response_data = await response.json()
    assert response_data == expected_response

    assert mock_corp_users.search_users.next_call()['request'].query == dict(
        params, client_id='client3', performer_department_id='dep1',
    )


@pytest.mark.parametrize(
    ['passport_mock', 'user_id', 'status_code'],
    [
        pytest.param('client3', 'not_existed_user', 404, id='not found'),
        pytest.param('client3', 'test_user_2', 403, id='another dep'),
    ],
    indirect=['passport_mock'],
)
async def test_get_user_fail(
        taxi_corp_real_auth_client, passport_mock, user_id, status_code,
):
    response = await taxi_corp_real_auth_client.get(
        '/2.0/users/{}'.format(user_id),
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'post_content'],
    [
        pytest.param(
            'client1', _v2(corp_users_util.BASE_USER_REQUEST), id='min fields',
        ),
        pytest.param(
            'client3',
            _v2(corp_users_util.EXTENDED_USER_REQUEST),
            id='max fields',
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
        '/2.0/users', json=post_content,
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
            'client3',
            _v2(corp_users_util.BASE_USER_REQUEST),
            403,
            id='alien dep',
        ),
        pytest.param(
            'client1',
            dict(_v2(corp_users_util.BASE_USER_REQUEST), extra_field=''),
            400,
            id='with extra field',
        ),
        pytest.param(
            'client1', {'fullname': 'test'}, 400, id='not enough fields',
        ),
        pytest.param(
            'client3',
            _v2(corp_users_util.TWO_LIMITS_USER_REQUEST),
            400,
            id='two limits for taxi',
        ),
        pytest.param(
            'client3',
            _v2(corp_users_util.ANOTHER_SERVICE_USER_REQUEST),
            400,
            id='try to change limit service in user',
        ),
        pytest.param(
            'client1',
            dict(
                _v2(corp_users_util.BASE_USER_REQUEST),
                cost_center=LONG_DEFAULT_CC,
            ),
            400,
            id='too long default cost center',
        ),
        pytest.param(
            'client3',
            _v2(corp_users_util.DELETED_LIMIT_USER_REQUEST),
            404,
            id='try assign deleted limit',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(**USER_PHONES_CONFIG)
async def test_fail_post_user(
        pd_patch,
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        post_content,
        status_code,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()
    response = await taxi_corp_real_auth_client.post(
        '/2.0/users', json=post_content,
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'user_id', 'post_content'],
    [
        pytest.param(
            'client1',
            'client1_user1',
            _v2(corp_users_util.BASE_USER_REQUEST),
            id='min fields',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            _v2(corp_users_util.EXTENDED_USER_REQUEST),
            id='max_fields',
        ),
        pytest.param(
            'client1',
            'client1_user1',
            dict(
                _v2(corp_users_util.BASE_USER_REQUEST),
                is_deleted=True,
                is_active=False,
            ),
            id='mark user as deleted',
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
        '/2.0/users/{}'.format(user_id), json=post_content,
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
            _v2(corp_users_util.BASE_USER_REQUEST),
            404,
            id='not existed user',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            _v2(corp_users_util.BASE_USER_REQUEST),
            403,
            id='try change to alien dep',
        ),
        pytest.param(
            'client3',
            'test_user_2',
            dict(_v2(corp_users_util.BASE_USER_REQUEST), department_id='dep1'),
            403,
            id='user from another dep',
        ),
        pytest.param(
            'client1',
            'test_user_1',
            _v2(corp_users_util.BASE_USER_REQUEST),
            403,
            id='user from another client',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            dict(
                _v2(corp_users_util.BASE_USER_REQUEST),
                is_deleted=True,
                department_id='dep1',
            ),
            400,
            id='is_deleted and is_active',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            dict(
                _v2(corp_users_util.EXTENDED_USER_REQUEST),
                cost_center=LONG_DEFAULT_CC,
            ),
            400,
            id='too long default cost center',
        ),
    ],
    indirect=['passport_mock'],
)
@pytest.mark.config(**USER_PHONES_CONFIG)
async def test_fail_put_user(
        pd_patch,
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        user_id,
        post_content,
        status_code,
):
    await taxi_corp_real_auth_client.server.app.phones.refresh_cache()
    response = await taxi_corp_real_auth_client.put(
        '/2.0/users/{}'.format(user_id), json=post_content,
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'user_id', 'post_content'],
    [
        pytest.param(
            'client1',
            'client1_user1',
            _v2(corp_users_util.BASE_USER_REQUEST),
            id='min fields',
        ),
        pytest.param(
            'client3',
            'test_user_1',
            _v2(corp_users_util.EXTENDED_USER_REQUEST),
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
        '/2.0/users/{}'.format(user_id), json=post_content,
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
