import datetime

import pytest

from taxi_corp.api import routes

BASE_PHONELESS_USER_REQUEST = {
    'fullname': 'base_name',
    'external_id': 'base_external_id',
    'is_active': True,
}

EXTENDED_PHONELESS_USER_REQUEST = {
    **BASE_PHONELESS_USER_REQUEST,
    'department_id': 'dep1',
    'limits': [
        {'limit_id': 'limit3_2', 'service': 'taxi'},
        {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
        {'limit_id': 'limit3_2_tanker', 'service': 'tanker'},
    ],
    'cost_centers_id': 'cost_center_1',
    'cost_center': 'default',
    'nickname': 'custom ID',
}

FIELDS_DEFAULT_VALUES = {'limits': [], 'nickname': '', 'is_deleted': False}

NOW = datetime.datetime(2022, 4, 23, 11, 00, 00)


@pytest.mark.parametrize(
    ['passport_mock', 'post_content'],
    [
        pytest.param('client1', BASE_PHONELESS_USER_REQUEST, id='min fields'),
        pytest.param(
            'client3', EXTENDED_PHONELESS_USER_REQUEST, id='max fields',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_success_post_phoneless_user(
        db, taxi_corp_real_auth_client, passport_mock, post_content,
):
    response = await taxi_corp_real_auth_client.post(
        f'{routes.API_PREFIX}/2.0/phoneless-users', json=post_content,
    )
    assert response.status == 200
    response_data = await response.json()
    db_user = await db.corp_users.find_one(
        {'_id': response_data['id']},
        projection={'_id': False, 'created': False, 'updated': False},
    )
    assert db_user.pop('is_draft')
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
            'client1',
            {**BASE_PHONELESS_USER_REQUEST, **{'extra_field': ''}},
            400,
            id='with extra field',
        ),
        pytest.param(
            'client1', {'fullname': 'test'}, 400, id='not enough fields',
        ),
        pytest.param(
            'client1',
            {
                'fullname': 'base_name',
                'external_id': 'external_id_2',
                'is_active': True,
            },
            406,
            id='duplicate external_id',
        ),
        pytest.param(
            'client3',
            {
                **BASE_PHONELESS_USER_REQUEST,
                **{
                    'department_id': 'dep1',
                    'limits': [
                        {'limit_id': 'limit3_2', 'service': 'taxi'},
                        {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                        {'limit_id': 'limit3_2_with_users', 'service': 'taxi'},
                    ],
                    'cost_centers_id': 'cost_center_1',
                },
            },
            400,
            id='two limits for taxi',
        ),
        pytest.param(
            'client3',
            {
                **BASE_PHONELESS_USER_REQUEST,
                **{
                    'department_id': 'dep1',
                    'limits': [{'limit_id': 'limit3_2', 'service': 'eats2'}],
                    'cost_centers_id': 'cost_center_1',
                },
            },
            400,
            id='try to change limit service in user',
        ),
        pytest.param(
            'client3',
            {
                **BASE_PHONELESS_USER_REQUEST,
                **{
                    'department_id': 'dep1',
                    'limits': [
                        {'limit_id': 'deleted_limit', 'service': 'taxi'},
                    ],
                    'cost_centers_id': 'cost_center_1',
                },
            },
            404,
            id='try assign deleted limit',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_fail_post_phoneless_user(
        db,
        taxi_corp_real_auth_client,
        passport_mock,
        post_content,
        status_code,
):
    response = await taxi_corp_real_auth_client.post(
        f'{routes.API_PREFIX}/2.0/phoneless-users', json=post_content,
    )
    assert response.status == status_code


@pytest.mark.parametrize(
    ['passport_mock', 'params', 'expected_code', 'expected_response'],
    [
        pytest.param(
            'client3',
            {'user_id': 'phoneless_user1'},
            200,
            {
                'id': 'phoneless_user1',
                'client_id': 'client3',
                'cost_centers_id': 'cost_center_0',
                'department_id': 'dep1',
                'external_id': 'external_id_1',
                'fullname': 'phoneless user draft',
                'is_active': True,
                'is_deleted': False,
                'is_draft': True,
                'limits': [
                    {'limit_id': 'limit3_2_with_users', 'service': 'taxi'},
                    {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                    {'limit_id': 'drive_limit', 'service': 'drive'},
                    {'limit_id': 'limit3_2_tanker', 'service': 'tanker'},
                ],
            },
            id='phoneless user draft',
        ),
        pytest.param(
            'client1',
            {'user_id': 'phoneless_user2'},
            200,
            {
                'id': 'phoneless_user2',
                'client_id': 'client1',
                'external_id': 'external_id_2',
                'fullname': 'phoneless user not draft',
                'is_active': True,
                'is_deleted': False,
                'is_draft': False,
                'limits': [{'limit_id': 'default_limit', 'service': 'taxi'}],
            },
            id='phoneless user not draft',
        ),
        pytest.param(
            'client1',
            {'external_id': 'external_id_2'},
            200,
            {
                'id': 'phoneless_user2',
                'client_id': 'client1',
                'external_id': 'external_id_2',
                'fullname': 'phoneless user not draft',
                'is_active': True,
                'is_deleted': False,
                'is_draft': False,
                'limits': [{'limit_id': 'default_limit', 'service': 'taxi'}],
            },
            id='phoneless user not draft (search by external_id)',
        ),
        pytest.param(
            'client1',
            {'user_id': 'not_existed_id'},
            404,
            None,
            id='not existed',
        ),
        pytest.param('client1', {}, 400, None, id='empty query'),
        pytest.param(
            'client1',
            {'user_id': 'phoneless_user2', 'external_id': 'external_id_2'},
            400,
            None,
            id='both parameters in query',
        ),
        pytest.param(
            'client3',
            {'external_id': 'external_id_2'},
            403,
            None,
            id='access denied, another client_id',
        ),
        pytest.param('client3', {}, 400, None, id='empty query'),
    ],
    indirect=['passport_mock'],
)
async def test_api_get_phoneless_user(
        taxi_corp_real_auth_client,
        passport_mock,
        params,
        expected_code,
        expected_response,
):
    response = await taxi_corp_real_auth_client.get(
        f'{routes.API_PREFIX}/2.0/phoneless-users', params=params,
    )

    assert response.status == expected_code

    if expected_code == 200:
        response_data = await response.json()
        assert response_data == expected_response


@pytest.mark.parametrize(
    ['passport_mock', 'params', 'post_content'],
    [
        pytest.param(
            'client1',
            {'user_id': 'phoneless_user2'},
            {'fullname': 'update_name', 'is_active': False},
            id='min fields',
        ),
        pytest.param(
            'client1',
            {'external_id': 'external_id_2'},
            {'fullname': 'update_name', 'is_active': False},
            id='min fields (update by external_id)',
        ),
        pytest.param(
            'client3',
            {'user_id': 'phoneless_user1'},
            {
                'fullname': 'base_name',
                'is_active': True,
                'department_id': 'dep1',
                'limits': [
                    {'limit_id': 'limit3_2', 'service': 'taxi'},
                    {'limit_id': 'limit3_2_eats2', 'service': 'eats2'},
                    {'limit_id': 'limit3_2_tanker', 'service': 'tanker'},
                ],
                'cost_centers_id': 'cost_center_1',
                'cost_center': 'default',
                'nickname': 'custom ID',
            },
            id='max_fields',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_success_put_phoneless_user(
        db, taxi_corp_real_auth_client, passport_mock, params, post_content,
):
    response = await taxi_corp_real_auth_client.put(
        f'{routes.API_PREFIX}/2.0/phoneless-users',
        params=params,
        json=post_content,
    )
    assert response.status == 200

    query = {}
    if params.get('user_id'):
        query['_id'] = params['user_id']
    if params.get('external_id'):
        query['external_id'] = params['external_id']

    db_user = await db.corp_users.find_one(
        query,
        projection={
            'created': False,
            'updated': False,
            'services': False,
            'phone': False,
            'phone_id': False,
            'personal_phone_id': False,
            'stat': False,
            'is_draft': False,
        },
    )
    assert db_user.pop('client_id') == passport_mock
    user_id = db_user.pop('_id')
    external_id = db_user.pop('external_id')
    if 'user_id' in params:
        assert params['user_id'] == user_id
    if 'external_id' in params:
        assert params['external_id'] == external_id

    for key, value in db_user.items():
        if key in post_content:
            assert value == post_content[key]
        else:
            if key in FIELDS_DEFAULT_VALUES:
                assert value == FIELDS_DEFAULT_VALUES[key], key
            else:
                assert value is None, key


@pytest.mark.parametrize(
    ['passport_mock', 'params', 'post_content', 'status_code'],
    [
        pytest.param(
            'client1',
            {'user_id': 'not_existed_user'},
            None,
            404,
            id='not existed user',
        ),
        pytest.param(
            'client3',
            {'user_id': 'phoneless_user1'},
            {'fullname': 'update_name', 'is_active': True},
            403,
            id='try change to alien dep',
        ),
        pytest.param(
            'client1',
            {'user_id': 'phoneless_user2'},
            {
                'fullname': 'update_name',
                'is_active': True,
                'department_id': 'dep1',
            },
            403,
            id='user from another dep',
        ),
        pytest.param(
            'client1',
            {'user_id': 'phoneless_user1'},
            None,
            403,
            id='user from another client',
        ),
        pytest.param('client1', {}, None, 400, id='empty query'),
        pytest.param(
            'client3',
            {'external_id': 'external_id_2'},
            None,
            403,
            id='access denied, another client_id',
        ),
        pytest.param(
            'client1',
            {'user_id': 'phoneless_user2'},
            {'fullname': 'update_name', 'is_active': True, 'is_deleted': True},
            400,
            id='cannot mark user as deleted',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_fail_put_phoneless_user(
        taxi_corp_real_auth_client,
        passport_mock,
        params,
        post_content,
        status_code,
):
    response = await taxi_corp_real_auth_client.put(
        f'{routes.API_PREFIX}/2.0/phoneless-users',
        params=params,
        json=post_content,
    )
    assert response.status == status_code


@pytest.mark.now(NOW.isoformat())
@pytest.mark.parametrize(
    ['passport_mock', 'params', 'expected_response', 'is_new'],
    [
        pytest.param(
            'client3',
            {'user_id': 'phoneless_user1'},
            {
                'link': '$mockserver/active_link_id',
                'expiration_date': '2022-04-24T15:20:20+0300',
            },
            False,
            id='existed active link',
        ),
        pytest.param(
            'client3',
            {'external_id': 'external_id_1'},
            {
                'link': '$mockserver/active_link_id',
                'expiration_date': '2022-04-24T15:20:20+0300',
            },
            False,
            id='existed active link (search by external_id)',
        ),
        pytest.param(
            'client1',
            {'user_id': 'client1_user1'},
            None,
            True,
            id='existed link is expired, create new',
        ),
        pytest.param(
            'client3',
            {'user_id': 'test_user_1'},
            None,
            True,
            id='existed link is used, create new',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_post_phoneless_users_link(
        taxi_corp_real_auth_client,
        db,
        passport_mock,
        params,
        expected_response,
        is_new,
):
    response = await taxi_corp_real_auth_client.post(
        f'{routes.API_PREFIX}/2.0/phoneless-users/link', params=params,
    )
    assert response.status == 200

    response_data = await response.json()

    query = {}
    if params.get('user_id'):
        query['_id'] = params['user_id']
    if params.get('external_id'):
        query['external_id'] = params['external_id']

    db_user = await db.corp_users.find_one(query, projection=[])

    if not is_new:
        assert response_data == expected_response
    else:
        link_id = response_data['link'].split('/')[-1]
        db_item = await db.corp_phoneless_user_links.find_one({'_id': link_id})
        assert db_item == {
            '_id': link_id,
            'client_id': passport_mock,
            'user_id': db_user['_id'],
            'is_used': False,
            'created': NOW,
            'updated': NOW,
        }


@pytest.mark.parametrize(
    ['passport_mock', 'params'],
    [
        pytest.param(
            'client3', {'user_id': 'phoneless_user1'}, id='archive-ok',
        ),
        pytest.param(
            'client3',
            {'external_id': 'external_id_1'},
            id='archive-ok (search by external_id)',
        ),
    ],
    indirect=['passport_mock'],
)
async def test_archive_phoneless_user(
        passport_mock, db, taxi_corp_real_auth_client, params,
):
    """
    the rest of the tests are in /integration/2.0/users/{user_id}/archive
    """
    query = {}
    if params.get('user_id'):
        query['_id'] = params['user_id']
    if params.get('external_id'):
        query['external_id'] = params['external_id']

    doc_before = await db.corp_users.find_one(query)
    assert not doc_before.get('is_deleted')

    response = await taxi_corp_real_auth_client.post(
        f'{routes.API_PREFIX}/2.0/phoneless-users/archive',
        json={},
        params=params,
    )

    doc_after = await db.corp_users.find_one(query)
    assert response.status == 200
    assert doc_after['is_deleted'] is True
    assert doc_after['is_active'] is False
