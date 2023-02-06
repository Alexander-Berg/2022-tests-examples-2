import pytest


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_all_users(web_app_client):
    permitted_user_ids = [34, 35, '000000', '007']

    for user_id in permitted_user_ids:
        response = await web_app_client.get(f'/v1/users' f'?user_id={user_id}')
        assert response.status == 200
        response_json = await response.json()
        assert len(response_json['users']) == 5
        assert {'id': 1, 'login': 'ya_user_1'} in response_json['users']
        assert {'id': 2, 'login': 'ya_user_2'} in response_json['users']
        assert {'id': 3, 'login': 'ya_user_3'} in response_json['users']
        assert {'id': 4, 'login': 'ya_user_4'} in response_json['users']
        assert {'id': 5, 'login': 'ya_user_5'} in response_json['users']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_users_by_id(web_app_client):
    response = await web_app_client.get('/v1/users/34?user_id=007')
    assert response.status == 200
    response_json = await response.json()
    assert response_json['provider_id'] == '34'
    assert response_json['is_active'] is True
    assert response_json['permissions'] == []


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_delete_users_by_id(web_app_client):
    response = await web_app_client.delete(
        '/v1/users/34?user_id=007&project_slug=ya_market',
    )
    assert response.status == 200


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_permissions_for_user_by_id(web_app_client):
    response = await web_app_client.get(
        '/v1/users/34/permissions?user_id=007&project_slug=ya_market',
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['permissions'] == ['read', 'write']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_put_permissions_for_user_by_id(web_app_client):
    response = await web_app_client.put(
        '/v1/users/34/permissions?user_id=007&project_slug=ya_market',
        json={'permissions': ['read']},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/users/34/permissions?user_id=007&project_slug=ya_market',
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['permissions'] == ['read']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_put_multiple_permissions_for_user_by_id(web_app_client):
    response = await web_app_client.put(
        '/v1/users/34/permissions?user_id=007&project_slug=ya_market',
        json={'permissions': ['read', 'write']},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/users/34/permissions?user_id=007&project_slug=ya_market',
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['permissions'] == ['read', 'write']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_put_permissions_for_user_admin(web_app_client):
    response = await web_app_client.put(
        '/v1/users/007/permissions?user_id=007&project_slug=ya_market',
        json={'permissions': ['read']},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/users/007/permissions?user_id=007&project_slug=ya_market',
    )
    assert response.status == 200

    response_json = await response.json()
    assert response_json['permissions'] == ['read']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_project_roles_by_user(web_app_client):
    response = await web_app_client.get(
        '/v1/users/34/roles?user_id=007&project_slug=ya_market',
    )
    assert response.status == 200

    response_json = await response.json()
    assert len(response_json['project_roles']) == 1
    assert response_json['project_roles'][0]['project_slug'] == 'ya_market'


TEST_SERVICE_TICKET = (
    '3:serv:CBAQ__________'
    '9_IgUI3gEQbw:QzaViIq2'
    'Q2PT4eOSAA5KckfGWfiAY'
    'AWCzsgxsCPLjmbtr0ajCW'
    'WiSbow3A26IJPGAlHokU_'
    'UUvPQHj4VWteK0I-BD-Om'
    'lKNAUiG0NyN5klfDpNxlW'
    'zF3rIUklChCGsG2YNBMeh'
    'GNvFmqbfocwNB9JLhHpB2'
    'I_9P847VfM9nihhA'
)


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'sample_client', 'dst': 'supportai-tasks'}],
    TVM_SERVICES={'supportai-tasks': 111, 'sample_client': 222},
    TVM_API_URL='$mockserver/tvm',
)
@pytest.mark.usefixtures('mocked_tvm')
async def test_project_info_internal(web_app_client):
    def check(res_json: dict):
        assert res_json['slug'] == 'ya_lavka'
        assert res_json['is_chatterbox'] is False
        assert 'read' in res_json['permissions']
        assert 'write' in res_json['permissions']

    response = await web_app_client.get(
        '/supportai-tasks/v1/users/34/projects/ya_lavka',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )

    assert response.status == 200
    response_json = await response.json()

    check(response_json)

    response = await web_app_client.get(
        '/supportai-tasks/v1/users/007/projects/ya_lavka',
        headers={'X-Ya-Service-Ticket': TEST_SERVICE_TICKET},
    )

    assert response.status == 200
    response_json = await response.json()

    check(response_json)


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_users_by_ids(web_app_client):
    expected_users = {
        1: {
            'provider_id': '34',
            'login': 'ya_user_1',
            'is_active': True,
            'permissions': {
                'ya_market': ['read', 'write'],
                'ya_lavka': ['read', 'write'],
            },
        },
        2: {
            'provider_id': '35',
            'login': 'ya_user_2',
            'is_active': True,
            'permissions': {
                'ya_market': ['read', 'write'],
                'ya_lavka': ['read', 'write', 'modify'],
            },
        },
        3: {'provider_id': '000000'},
        4: {'provider_id': '007'},
        5: {
            'provider_id': '12321',
            'login': 'ya_user_5',
            'is_active': False,
            'permissions': {'ya_lavka': ['read']},
        },
    }

    def kick_users_without_permissions(res_json):
        res_json['users'] = [
            user for user in res_json['users'] if user['permissions']
        ]

    def check_user_ids(res_json, expected_user_ids):
        provider_ids = {user['provider_id'] for user in res_json['users']}
        expected_provider_ids = {
            expected_users[user_id]['provider_id']
            for user_id in expected_user_ids
        }
        assert provider_ids == expected_provider_ids

    def check_users(res_json, project_slug):
        for user in res_json['users']:
            expected_user = expected_users_by_provider_id[user['provider_id']]
            assert user['login'] == expected_user['login']
            assert user['is_active'] == expected_user['is_active']
            assert (
                user['permissions']
                == expected_user['permissions'][project_slug]
            )

    expected_users_by_provider_id = {
        user['provider_id']: user for user in expected_users.values()
    }
    response_empty = await web_app_client.post(
        '/supportai-tasks/v1/users/by_provider_ids?project_slug=ya_lavka',
        json={'user_provider_ids': []},
    )
    assert response_empty.status == 200
    json_empty = await response_empty.json()
    check_user_ids(json_empty, [])
    kick_users_without_permissions(json_empty)
    assert json_empty['users'] == []

    response_no_users = await web_app_client.post(
        '/supportai-tasks/v1/users/by_provider_ids?project_slug=ya_market',
        json={
            'user_provider_ids': [
                expected_users[i]['provider_id'] for i in (3, 4, 5)
            ] + ['not_existing_user', 'one_more_just_in_case'],
        },
    )
    assert response_no_users.status == 200
    json_no_users = await response_no_users.json()
    check_user_ids(json_no_users, [3, 4, 5])
    kick_users_without_permissions(json_no_users)
    assert json_no_users['users'] == []

    response_all_users = await web_app_client.post(
        '/supportai-tasks/v1/users/by_provider_ids?project_slug=ya_lavka',
        json={
            'user_provider_ids': [
                expected_users[i]['provider_id'] for i in (1, 2, 5)
            ],
        },
    )
    assert response_all_users.status == 200
    json_all_users = await response_all_users.json()
    check_user_ids(json_all_users, [1, 2, 5])
    kick_users_without_permissions(json_all_users)
    check_user_ids(json_all_users, [1, 2, 5])
    check_users(json_all_users, 'ya_lavka')

    response_some_users = await web_app_client.post(
        '/supportai-tasks/v1/users/by_provider_ids?project_slug=ya_market',
        json={
            'user_provider_ids': [
                expected_users[i]['provider_id'] for i in (1, 2, 3, 4, 5)
            ],
        },
    )
    assert response_some_users.status == 200
    json_some_users = await response_some_users.json()
    check_user_ids(json_some_users, [1, 2, 3, 4, 5])
    kick_users_without_permissions(json_some_users)
    check_user_ids(json_some_users, [1, 2])
    check_users(json_some_users, 'ya_market')


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_superuser_handlers(web_app_client):
    response_superusers = await web_app_client.get(
        '/v1/superusers?user_id=007',
    )
    assert response_superusers.status == 200

    json_superusers = await response_superusers.json()
    assert len(json_superusers['users']) == 1

    response_post_superuser = await web_app_client.post(
        '/v1/users/34/make-superuser?user_id=007',
    )
    assert response_post_superuser.status == 200

    response_superusers = await web_app_client.get(
        '/v1/superusers?user_id=007',
    )
    assert response_superusers.status == 200

    json_superusers = await response_superusers.json()
    assert len(json_superusers['users']) == 2

    response_post_superuser = await web_app_client.post(
        '/v1/users/34/make-superuser?user_id=007',
    )
    assert response_post_superuser.status == 400

    response_post_superuser = await web_app_client.post(
        '/v1/users/35/make-superuser?user_id=000000',
    )
    assert response_post_superuser.status == 403
