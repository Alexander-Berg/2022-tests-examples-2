import json

import pytest


async def test_get_idm_info_basic(web_app_client):
    response = await web_app_client.get('/idm-integration/info')
    assert response.status == 200

    content = await response.json()
    assert content['code'] == 0


@pytest.mark.config(
    ATLAS_METRICS_RESTRICTION_GROUPS={
        'view_groups': [
            {'en_name': 'CI+KD', 'id': 'ci_kd', 'ru_name': 'CI+KD'},
            {
                'en_name': 'Call center',
                'id': 'callcenter',
                'ru_name': 'Колл-центер',
            },
        ],
    },
)
async def test_get_idm_info_metrics(web_app_client):
    response = await web_app_client.get('/idm-integration/info')
    assert response.status == 200
    content = await response.json()
    assert content['code'] == 0

    assert 'metrics' in content['roles']['values']
    metrics_proj = content['roles']['values']['metrics']['roles']['values']
    assert 'admin' in metrics_proj
    assert 'edit_protected_metrics' in metrics_proj
    assert (
        'z_edit_protected_metric'
        in metrics_proj['edit_protected_metrics']['roles']['values']
    )
    assert 'view_protected_metric_groups' in metrics_proj
    groups = metrics_proj['view_protected_metric_groups']['roles']['values']
    assert 'ci_kd' in groups
    assert 'callcenter' in groups


async def test_get_idm_info_restricted_preset_cities(web_app_client):
    response = await web_app_client.get('/idm-integration/info')
    assert response.status == 200
    content = await response.json()
    assert content['code'] == 0

    assert 'restricted_preset_cities' in content['roles']['values']
    preset_proj = content['roles']['values']['restricted_preset_cities']

    assert 'RTT Experiment' not in preset_proj['roles']['values']
    assert 'All Cities' in preset_proj['roles']['values']


async def test_get_idm_info_restricted_cities(web_app_client):
    response = await web_app_client.get('/idm-integration/info')
    assert response.status == 200
    content = await response.json()
    assert content['code'] == 0

    assert 'restricted_cities' in content['roles']['values']
    cities_proj = content['roles']['values']['restricted_cities']

    assert 'kazan' in cities_proj['roles']['values']
    assert 'vladivostok' in cities_proj['roles']['values']


async def test_add_idm_role(web_app_client, db):
    role = {
        'login': 'restricted_user',
        'role': {
            'metric': 'z_edit_protected_metric',
            'project': 'metrics',
            'role': 'edit_protected_metrics',
        },
    }
    mongo_filter = {
        'login': role['login'],
        'role.project': role['role']['project'],
        'role.role': role['role']['role'],
        'role.metric': role['role']['metric'],
    }
    before_count = await db.atlas_idm_roles.find(mongo_filter).count()
    assert before_count == 0

    response = await web_app_client.post(
        '/idm-integration/add-role',
        data={'login': role['login'], 'role': json.dumps(role['role'])},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'code': 0}

    after_count = await db.atlas_idm_roles.find(mongo_filter).count()
    assert after_count == 1

    second_response = await web_app_client.post(
        '/idm-integration/add-role',
        data={'login': role['login'], 'role': json.dumps(role['role'])},
    )
    assert second_response.status == 200
    content = await second_response.json()
    assert content == {'code': 0}

    second_after_count = await db.atlas_idm_roles.find(mongo_filter).count()
    assert second_after_count == 1


async def test_remove_idm_role(web_app_client, db):
    role = {
        'login': 'city_user',
        'role': {'project': 'restricted_cities', 'role': 'kazan'},
    }
    mongo_filter = {
        'login': role['login'],
        'role.project': role['role']['project'],
        'role.role': role['role']['role'],
    }
    before_count = await db.atlas_idm_roles.find(mongo_filter).count()
    assert before_count == 1

    response = await web_app_client.post(
        '/idm-integration/remove-role',
        data={'login': role['login'], 'role': json.dumps(role['role'])},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {'code': 0}

    after_count = await db.atlas_idm_roles.find(mongo_filter).count()
    assert after_count == 0


async def test_get_idm_user_roles(web_app_client):
    response = await web_app_client.get('/idm-integration/get-all-roles')
    assert response.status == 200
    content = await response.json()
    assert content['code'] == 0

    users = content['users']
    many_role_users = {
        user['login'] for user in users if len(user['roles']) > 1
    }
    assert many_role_users == {
        'omnipotent_user',
        'city_user',
        'metrics_view_protected_group_user',
        'jupyter_viewer_2_3',
    }

    def _check_single_role_user(login, role):
        user_roles = [
            user['roles'] for user in users if user['login'] == login
        ]
        assert len(user_roles) == 1
        assert len(user_roles[0]) == 1
        assert role == user_roles[0][0]

    _check_single_role_user(
        'preset_user',
        {'project': 'restricted_preset_cities', 'role': 'RTT Experiment 2'},
    )
