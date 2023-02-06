import pytest

import supportai_calls.models as db_models

pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.pgsql('supportai_calls', files=['sample_project.sql']),
    pytest.mark.config(
        TVM_ENABLED=False,
        SUPPORTAI_CALLS_INTERNAL_USERS={
            'check_ignore_projects': [
                'ivr_framework_no_template_file',
                'ivr_framework_with_template_file',
                'not_existing_slug',
            ],
            'services': '',
        },
    ),
]


@pytest.mark.parametrize('is_internal_api', [True, False])
async def test_get_project_config(
        stq3_context, web_app_client, is_internal_api,
):
    base_url = (
        '/supportai-calls/v1/project-configs'
        if is_internal_api
        else '/v1/project_configs'
    )
    response = await web_app_client.get(
        f'{base_url}?project_slug=ivr_framework_no_template_file&user_id=34',
    )
    assert response.status == 200
    response_json = await response.json()
    assert 'project_slug' in response_json
    assert 'template_file_id' not in response_json
    assert 'dispatcher_params' in response_json
    assert response_json['project_slug'] == 'ivr_framework_no_template_file'
    assert len(response_json['dispatcher_params']) == 1
    assert 'call_service' in response_json['dispatcher_params']
    assert (
        response_json['dispatcher_params']['call_service'] == 'ivr_framework'
    )

    response = await web_app_client.get(
        f'{base_url}?project_slug=ivr_framework_with_template_file&user_id=34',
    )
    assert response.status == 200
    response_json = await response.json()
    assert 'project_slug' in response_json
    assert 'template_file_id' in response_json
    assert 'dispatcher_params' in response_json
    assert response_json['project_slug'] == 'ivr_framework_with_template_file'
    assert response_json['template_file_id'] == '1'
    assert 'call_service' in response_json['dispatcher_params']
    assert (
        response_json['dispatcher_params']['call_service'] == 'ivr_framework'
    )

    response = await web_app_client.get(
        f'{base_url}?project_slug=not_existing_slug&user_id=34',
    )
    assert response.status == 204

    response_not_authorized = await web_app_client.get(
        f'{base_url}?project_slug=ivr_framework_with_template_file',
    )
    assert response_not_authorized.status == (403 if is_internal_api else 400)


async def test_insert_project_config(stq3_context, web_app_client, patch):
    random_secret = '1234567890'

    @patch(
        'supportai_calls.utils.project_config_helpers.generate_random_secret',
    )
    def _():
        return random_secret

    response = await web_app_client.post(
        '/v1/project_configs?project_slug=new_project&user_id=34', json={},
    )
    assert response.status == 200

    response = await web_app_client.post(
        '/v1/project_configs?project_slug=new_project_template&user_id=34',
        json={
            'template_file_id': '1',
            'dispatcher_params': {
                'call_service': 'voximplant',
                'api_key': 'some api_key',
                'account_id': 123,
                'rule_id': 321,
            },
            'auth_token': 'fffffSomeTokenfffff',
            'auth_allowed_ips': ['ip1', 'ip2'],
        },
    )
    assert response.status == 200

    async with stq3_context.pg.slave_pool.acquire() as conn:
        new_project_config = (
            await db_models.ProjectConfig.select_by_project_slug(
                stq3_context, conn, 'new_project',
            )
        )
        new_project_template_config = (
            await db_models.ProjectConfig.select_by_project_slug(
                stq3_context, conn, 'new_project_template',
            )
        )

    assert new_project_config.project_slug == 'new_project'
    assert (
        new_project_config.call_service == db_models.CallService.IVR_FRAMEWORK
    )
    assert new_project_config.template_file_id is None
    assert new_project_config.audio_files_secret == random_secret
    assert new_project_template_config.project_slug == 'new_project_template'
    assert (
        new_project_template_config.call_service
        == db_models.CallService.VOXIMPLANT
    )
    assert new_project_template_config.template_file_id == 1
    assert new_project_template_config.audio_files_secret == random_secret
    assert new_project_template_config.dispatcher_params is not None
    assert (
        new_project_template_config.dispatcher_params['api_key']
        == 'some api_key'
    )
    assert new_project_template_config.dispatcher_params['account_id'] == 123
    assert new_project_template_config.auth_token == 'fffffSomeTokenfffff'
    assert new_project_template_config.auth_allowed_ips == ['ip1', 'ip2']

    response_get_template = await web_app_client.get(
        '/v1/project_configs?project_slug=new_project_template&user_id=34',
    )
    assert response_get_template.status == 200
    response_json = await response_get_template.json()
    assert 'dispatcher_params' in response_json
    assert response_json['dispatcher_params']['api_key'] == 'some api_key'

    response_duplicate_slug = await web_app_client.post(
        'v1/project_configs?project_slug=new_project&user_id=34', json={},
    )
    assert response_duplicate_slug.status == 500

    response_no_such_call_service = await web_app_client.post(
        'v1/project_configs?project_slug=test_ignore&user_id=34',
        json={'dispatcher_params': {'call_service': 'nor ivr nor voximplant'}},
    )
    assert response_no_such_call_service.status == 400

    response_no_such_file = await web_app_client.post(
        'v1/project_configs?project_slug=test_ignore&user_id=34',
        json={'template_file_id': '2'},
    )
    assert response_no_such_file.status == 500


async def test_update_project_config(stq3_context, web_app_client):
    response = await web_app_client.put(
        'v1/project_configs'
        '?project_slug=ivr_framework_no_template_file&user_id=34',
        json={'template_file_id': '1'},
    )
    assert response.status == 200

    response = await web_app_client.put(
        'v1/project_configs'
        '?project_slug=ivr_framework_with_template_file&user_id=34',
        json={},
    )
    assert response.status == 200

    response = await web_app_client.put(
        'v1/project_configs?project_slug=vox_no_template_file&user_id=34',
        json={'call_service': 'ivr_framework'},
    )
    assert response.status == 200

    async with stq3_context.pg.slave_pool.acquire() as conn:
        now_with_template = (
            await db_models.ProjectConfig.select_by_project_slug(
                stq3_context, conn, 'ivr_framework_no_template_file',
            )
        )
        now_without_template = (
            await db_models.ProjectConfig.select_by_project_slug(
                stq3_context, conn, 'ivr_framework_with_template_file',
            )
        )
        now_ivr_framework = (
            await db_models.ProjectConfig.select_by_project_slug(
                stq3_context, conn, 'vox_no_template_file',
            )
        )

    assert now_with_template.template_file_id == 1
    assert now_without_template.template_file_id is None
    assert (
        now_ivr_framework.call_service == db_models.CallService.IVR_FRAMEWORK
    )

    assert now_with_template.project_slug == 'ivr_framework_no_template_file'
    assert (
        now_with_template.call_service == db_models.CallService.IVR_FRAMEWORK
    )
    assert (
        now_without_template.project_slug == 'ivr_framework_with_template_file'
    )
    assert (
        now_without_template.call_service
        == db_models.CallService.IVR_FRAMEWORK
    )
    assert now_ivr_framework.project_slug == 'vox_no_template_file'
    assert now_ivr_framework.template_file_id is None


async def test_update_project_config_various_json(
        stq3_context, web_app_client,
):
    default_project_config = {
        'dispatcher_params': {'call_service': 'ivr_framework'},
    }

    async def _update_project_config(new_project_config):
        if new_project_config is None:
            response = await web_app_client.put(
                'v1/project_configs?'
                'project_slug=vox_no_template_file&user_id=34',
            )
        else:
            response = await web_app_client.put(
                'v1/project_configs?'
                'project_slug=vox_no_template_file&user_id=34',
                json=new_project_config,
            )
        assert response.status == 200

        response = await web_app_client.get(
            'v1/project_configs?project_slug=vox_no_template_file&user_id=34',
        )
        assert response.status == 200
        updated_project_config = await response.json()
        if not new_project_config:
            expected_project_config = default_project_config
        else:
            expected_project_config = new_project_config
        assert updated_project_config == {
            **expected_project_config,
            **{'project_slug': 'vox_no_template_file'},
        }

    voximplant_project_config = {
        'dispatcher_params': {
            'call_service': 'voximplant',
            'account_id': 123,
            'api_key': 'some api_key',
            'rule_id': 321,
        },
    }

    project_configs = [
        None,
        {},
        {'dispatcher_params': {'call_service': 'ivr_framework'}},
        voximplant_project_config,
    ]

    for _from in project_configs:
        for _to in project_configs:
            await _update_project_config(_from)
            await _update_project_config(_to)
