# pylint: disable=C1801
import pytest

from supportai_tasks.models import role


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_projects(web_app_client):
    response = await web_app_client.get('/v1/projects?user_id=34')
    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['projects']) == 2

    response = await web_app_client.get('/v1/projects?user_id=35')
    assert response.status == 200

    response_json = await response.json()
    projects = response_json['projects']

    assert len(projects) == 3

    assert len(projects[0]['capabilities']) == 3
    assert 'topics' in projects[1]['capabilities']
    assert 'user_based' in projects[1]['capabilities']
    assert 'topics' in projects[2]['capabilities']
    assert 'user_based' in projects[2]['capabilities']
    assert 'features' in projects[2]['capabilities']

    response = await web_app_client.get('/v1/projects?user_id=007')
    assert response.status == 200

    response_json = await response.json()
    projects = response_json['projects']

    assert 'su_user_based' in projects[0]['capabilities']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_create_project(web_app_client):
    test_slug = 'test_slug'
    test_title = 'test_title'
    test_is_chatterbox_value = True
    default_capabilities = {'su_user_based', 'topics', 'features'}
    default_permissions = {
        role.ROLE_PERMISSION_READ,
        role.ROLE_PERMISSION_WRITE,
        role.ROLE_PERMISSION_MODIFY,
    }

    response = await web_app_client.get('/v1/projects?user_id=007')
    admin_initial_amount = len((await response.json())['projects'])

    response = await web_app_client.get('/v1/projects?user_id=34')
    user_initial_amount = len((await response.json())['projects'])

    response = await web_app_client.post(
        '/v1/projects?user_id=34',
        json={
            'slug': test_slug,
            'title': test_title,
            'is_chatterbox': test_is_chatterbox_value,
        },
    )
    assert response.status == 403

    response = await web_app_client.post(
        '/v1/projects?user_id=007',
        json={
            'slug': '',
            'title': test_title,
            'is_chatterbox': test_is_chatterbox_value,
        },
    )
    assert response.status == 500

    response = await web_app_client.post(
        '/v1/projects?user_id=007',
        json={
            'slug': test_slug,
            'title': '',
            'is_chatterbox': test_is_chatterbox_value,
        },
    )
    assert response.status == 500

    response = await web_app_client.post(
        '/v1/projects?user_id=007',
        json={
            'slug': test_slug,
            'title': test_title,
            'is_chatterbox': test_is_chatterbox_value,
        },
    )
    assert response.status == 200
    project_info = await response.json()

    response = await web_app_client.post(
        '/v1/projects?user_id=007',
        json={
            'slug': test_slug,
            'title': test_title,
            'is_chatterbox': test_is_chatterbox_value,
        },
    )
    assert response.status == 500

    response = await web_app_client.get('/v1/projects?user_id=007')
    admin_final_amount = len((await response.json())['projects'])

    response = await web_app_client.get('/v1/projects?user_id=34')
    user_final_amount = len((await response.json())['projects'])

    assert admin_final_amount == admin_initial_amount + 1
    assert user_final_amount == user_initial_amount
    assert project_info['slug'] == test_slug
    assert project_info['title'] == test_title
    assert project_info['is_chatterbox'] == test_is_chatterbox_value
    assert set(project_info['capabilities']) == default_capabilities
    assert set(project_info['permissions']) == default_permissions


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_get_projects_all_access_user(web_app_client):
    response = await web_app_client.get('/v1/projects?user_id=35')
    assert response.status == 200
    assert len((await response.json())['projects']) == 3


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_invalid_user(web_app_client):
    response = await web_app_client.get('/v1/projects?user_id=32')
    assert response.status == 403


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_project_users(web_app_client):
    response = await web_app_client.get(
        '/v1/projects/users?user_id=34&project_slug=ya_market',
    )
    assert response.status == 200

    responose_json = await response.json()
    assert len(responose_json['users']) == 2

    for user in responose_json['users']:
        assert 'login' in user


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_user_approve(web_app_client):
    response = await web_app_client.get(
        '/v1/projects/users?user_id=34&project_slug=ya_market',
    )
    assert response.status == 200

    not_active_user_ids = [
        user['provider_id']
        for user in (await response.json())['users']
        if not user['is_active']
    ]

    for _id in not_active_user_ids:
        _response = await web_app_client.get(
            '/v1/projects?user_id={}&project_slug=ya_market'.format(_id),
        )
        assert _response.status == 200

    response = await web_app_client.get(
        '/v1/projects/users?user_id=34&project_slug=ya_market',
    )
    assert response.status == 200

    for user in (await response.json())['users']:
        if user['provider_id'] in not_active_user_ids:
            assert user['is_active']


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_project_users_add(web_app_client):
    response = await web_app_client.get(
        '/v1/projects/users?user_id=35&project_slug=ya_lavka',
    )
    assert response.status == 200
    assert len((await response.json())['users']) == 3

    response = await web_app_client.post(
        '/v1/projects/users?user_id=35&project_slug=ya_lavka',
        json={'provider_id': '333', 'login': '333'},
    )
    assert response.status == 200

    response = await web_app_client.get(
        '/v1/projects/users?user_id=35&project_slug=ya_lavka',
    )
    assert response.status == 200
    assert len((await response.json())['users']) == 4

    response = await web_app_client.get(
        '/v1/projects/users?user_id=333&project_slug=ya_lavka',
    )
    assert response.status == 200
    assert len((await response.json())['users']) == 4

    response = await web_app_client.post(
        '/v1/projects/users?user_id=35&project_slug=ya_lavka',
        json={'login': 'ya_user_3'},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/projects/users?user_id=35&project_slug=ya_lavka',
        json={'login': 'other_user'},
    )
    assert response.status == 400


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_projects_super_admin(web_app_client):
    response = await web_app_client.get('/v1/projects?user_id=007')
    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['projects']) == 3

    response = await web_app_client.post(
        '/v1/projects/users?user_id=007&project_slug=ya_useless',
        json={'provider_id': '000', 'login': 'ya_useless_user'},
    )
    assert response.status == 200


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_projects_add_user_denied(web_app_client):
    response = await web_app_client.get('/v1/projects?user_id=34')
    assert response.status == 200

    response_json = await response.json()

    assert len(response_json['projects']) == 2

    response = await web_app_client.post(
        '/v1/projects/users?user_id=34&project_slug=ya_useless',
        json={'provider_id': '000', 'login': 'ya_useless_user'},
    )
    assert response.status == 403


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_update_project_by_slug(web_app_client):
    response_get_projects = await web_app_client.get('/v1/projects?user_id=34')
    assert response_get_projects.status == 200
    response_projects_json = await response_get_projects.json()
    project = response_projects_json['projects'][0]
    assert project['id'] == '1'
    assert project['slug'] == 'ya_market'
    assert project['title'] == 'Маркет'
    assert not project['is_chatterbox']
    assert not project['new_config_schema']
    assert 'validation_instance_id' not in project

    response_update_project = await web_app_client.put(
        'v1/projects/ya_market?user_id=34',
        json={
            'title': 'some title',
            'is_chatterbox': True,
            'new_config_schema': True,
        },
    )
    assert response_update_project.status == 200

    response_get_projects = await web_app_client.get('/v1/projects?user_id=34')
    assert response_get_projects.status == 200
    response_projects_json = await response_get_projects.json()
    project = response_projects_json['projects'][0]
    assert project['id'] == '1'
    assert project['slug'] == 'ya_market'
    assert project['title'] == 'some title'
    assert project['is_chatterbox']
    assert project['new_config_schema']
    assert 'validation_instance_id' not in project

    response_update_project_clear = await web_app_client.put(
        'v1/projects/ya_market?user_id=34',
        json={'title': 'other title', 'is_chatterbox': False},
    )
    assert response_update_project_clear.status == 200

    response_get_projects = await web_app_client.get('/v1/projects?user_id=34')
    assert response_get_projects.status == 200
    response_projects_json = await response_get_projects.json()
    project = response_projects_json['projects'][0]
    assert project['id'] == '1'
    assert project['slug'] == 'ya_market'
    assert project['title'] == 'other title'
    assert not project['is_chatterbox']
    assert 'new_config_schema' not in project
    assert 'validation_instance_id' not in project


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_add_capabilities_from_preset(web_app_client):
    response = await web_app_client.get('/v1/capabilities/project?user_id=007')
    assert response.status == 200
    response_json = await response.json()
    ya_useless_init_capabilities = [
        capabilities
        for capabilities in response_json['capabilities']
        if (
            'project_slug' in capabilities
            and capabilities['project_slug'] == 'ya_useless'
        )
    ]
    assert len(ya_useless_init_capabilities) == 0

    response = await web_app_client.post(
        '/v1/projects/ya_useless/from-preset/add-capabilities',
        params={'user_id': '007', 'preset_slug': 'pretty_awesome_preset'},
    )
    assert response.status == 204

    response = await web_app_client.get('/v1/capabilities/project?user_id=007')
    assert response.status == 200
    response_json = await response.json()

    ya_useless_capabilities = [
        capability['capability_slug']
        for capability in response_json['capabilities']
        if (
            'project_slug' in capability
            and capability['project_slug'] == 'ya_useless'
        )
    ]

    assert len(ya_useless_capabilities) == 3
    assert 'topics' in ya_useless_capabilities
    assert 'user_based' in ya_useless_capabilities
    assert 'demo' in ya_useless_capabilities


@pytest.mark.pgsql('supportai_tasks', files=['sample_projects.sql'])
async def test_internal_get_project(web_app_client):
    response = await web_app_client.get('/supportai-tasks/v1/projects/1')
    assert response.status == 200

    response_json = await response.json()

    assert response_json['slug'] == 'ya_market'
