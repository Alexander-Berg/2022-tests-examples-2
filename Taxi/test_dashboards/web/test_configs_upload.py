import copy
from typing import List

import pytest

from dashboards.internal import types
from dashboards.internal.models import configs as configs_models


LAYOUTS_REQUIRING_HOSTS = [
    {'name': 'http'},
    {'name': 'http_basic'},
    {'name': 'rps_share'},
]
COMMON_HANDLER = {
    'endpoint': '/get_stuff',
    'method': 'GET',
    'has_path_params': False,
    'custom_responses': [{'status': 403}, {'status': 405}, {'status': 410}],
}
DASHBOARD_SIMPLE_CONFIG_MOCK = {'layouts': [{'name': 'system'}]}
DASHBOARD_SAME_CONFIG_MOCK = {
    'layouts': [{'name': 'http'}, {'name': 'system'}, {'name': 'rps_share'}],
    'hostnames': ['test_service.taxi.yandex.net'],
    'handlers': [COMMON_HANDLER],
}
DASHBOARD_DIFF_LAYOUTS_CONFIG_MOCK = {
    'layouts': [{'name': 'http'}],
    'hostnames': ['test_service.taxi.yandex.net'],
    'handlers': [COMMON_HANDLER],
}
DASHBOARD_DIFF_HOSTNAMES_CONFIG_MOCK = {
    'layouts': [{'name': 'http'}, {'name': 'system'}, {'name': 'rps_share'}],
    'hostnames': [
        'test_service.taxi.yandex.net',
        'test_service.taxi.test.yandex.net',
    ],
    'handlers': [COMMON_HANDLER],
}
DASHBOARD_DIFF_HANDLERS_CONFIG_MOCK = {
    'layouts': [{'name': 'http'}, {'name': 'system'}, {'name': 'rps_share'}],
    'hostnames': ['test_service.taxi.yandex.net'],
    'handlers': [
        COMMON_HANDLER,
        {
            'endpoint': '/stuff/update',
            'method': 'POST',
            'has_path_params': False,
            'custom_responses': [],
        },
    ],
}
DASHBOARD_DIFF_HANDLER_DESCRIPTION_CONFIG_MOCK = {
    'layouts': [{'name': 'http'}, {'name': 'system'}, {'name': 'rps_share'}],
    'hostnames': ['test_service.taxi.yandex.net'],
    'handlers': [
        {
            'endpoint': '/get_stuff',
            'method': 'GET',
            'description': 'test_changed_description',
            'has_path_params': False,
            'custom_responses': [
                {'status': 403},
                {'status': 405},
                {'status': 410},
            ],
        },
    ],
}
DASHBOARD_DIFF_EMPTY_HANDLERS_CONFIG_MOCK = {
    'layouts': [{'name': 'http'}, {'name': 'system'}, {'name': 'rps_share'}],
    'hostnames': ['test_service.taxi.yandex.net'],
}
UPLOAD_CONFIG_PARAMS_MOCK = {
    'project_name': 'taxi-devops',
    'service_name': 'test_service',
    'branch_name': 'stable',
    'service_type': 'nanny',
}
DASHBOARD_NAME_MOCK = 'nanny_taxi_test_service_stable'


@pytest.mark.parametrize(
    'dashboard_config, should_have_diff',
    [
        pytest.param(DASHBOARD_SAME_CONFIG_MOCK, False, id='config_no_diff'),
        pytest.param(
            DASHBOARD_DIFF_HANDLERS_CONFIG_MOCK,
            True,
            id='config_diff_handlers',
        ),
        pytest.param(
            DASHBOARD_DIFF_HANDLER_DESCRIPTION_CONFIG_MOCK,
            True,
            id='config_diff_handler_additional_data',
        ),
        pytest.param(
            DASHBOARD_DIFF_EMPTY_HANDLERS_CONFIG_MOCK,
            True,
            id='config_diff_empty_handlers',
        ),
        pytest.param(
            DASHBOARD_DIFF_LAYOUTS_CONFIG_MOCK, True, id='config_diff_layouts',
        ),
        pytest.param(
            DASHBOARD_DIFF_HOSTNAMES_CONFIG_MOCK,
            True,
            id='config_diff_hostnames',
        ),
    ],
)
@pytest.mark.parametrize(
    'should_overwrite_waiting',
    [
        pytest.param(
            False,
            id='only_applied_config',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_data.sql',
                        'add_applied_config_with_common_handler.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            True,
            id='only_waiting_config',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_data.sql',
                        'add_waiting_config_with_common_handler.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            True,
            id='applied_and_waiting_config',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_data.sql',
                        'add_applied_config_with_uniq_handler.sql',
                        'add_waiting_config_with_common_handler.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            True,
            id='applied_and_waiting_with_common_handler',
            marks=[
                pytest.mark.pgsql(
                    'dashboards',
                    files=[
                        'init_data.sql',
                        'add_configs_with_common_handler.sql',
                    ],
                ),
            ],
        ),
    ],
)
async def test_upload_config(
        web_app_client,
        web_context,
        dashboard_config,
        should_have_diff,
        should_overwrite_waiting,
):
    expected_config = copy.deepcopy(dashboard_config)

    async def _get_configs_count():
        query, args = web_context.sqlt.service_branches_fetch_all_configs(
            service_branch_id=1,
            dashboard_name=DASHBOARD_NAME_MOCK,
            status=None,
        )
        configs = await web_context.pg.primary.fetch(query, *args)
        return len(configs)

    configs_count_before_upload = await _get_configs_count()

    response = await web_app_client.post(
        '/v1/configs/upload',
        params=UPLOAD_CONFIG_PARAMS_MOCK,
        json=expected_config,
    )
    content = await response.json()
    assert response.status == 200, content

    assert content['is_created'] == should_have_diff
    assert content['config'] == expected_config, str(content)

    configs_count_after_upload = await _get_configs_count()

    expected_config_count = (
        configs_count_before_upload + 1
        if should_have_diff and not should_overwrite_waiting
        else configs_count_before_upload
    )
    assert (
        configs_count_after_upload == expected_config_count
    ), f'service should have {expected_config_count} configs'


async def test_links_between_configs_and_handlers_after_upload(
        web_app_client,
        web_context,
        load_json,
        service_branch_mock,
        add_service_branch,
        add_config,
):
    service_branch_id = await add_service_branch(
        web_context, service_branch_mock,
    )
    handlers = [
        {**handler_data, 'service_branch_id': service_branch_id}
        for handler_data in load_json('handlers.json')
    ]
    raw_cofig = {
        'dashboard_name': DASHBOARD_NAME_MOCK,
        'layouts': LAYOUTS_REQUIRING_HOSTS,
        'dorblu_custom': None,
    }

    applied_config = await add_config(
        web_context,
        service_branch_id,
        configs_models.BareConfig.from_dict(
            {**raw_cofig, 'handlers': handlers[0:2]},
        ),
        status='applied',
    )
    waiting_config = await add_config(
        web_context,
        service_branch_id,
        configs_models.BareConfig.from_dict(
            {**raw_cofig, 'handlers': handlers[1:4]},
        ),
        status='waiting',
    )
    expected_handler_id_to_delete = 3

    response = await web_app_client.post(
        '/v1/configs/upload',
        params={
            'project_name': service_branch_mock.project_name,
            'service_name': service_branch_mock.service_name,
            'branch_name': service_branch_mock.branch_name,
            'service_type': service_branch_mock.group_info.type.value,
        },
        json={
            **raw_cofig,
            'hostnames': ['test_service.taxi.yandex.net'],
            'handlers': handlers[3:],
        },
    )
    content = await response.json()
    assert response.status == 200, content

    assert content['is_created']

    assert await check_deleted_configs(web_context, [waiting_config.id])
    assert not await check_deleted_configs(web_context, [applied_config.id, 3])

    assert await check_deleted_handlers(
        web_context, [expected_handler_id_to_delete],
    )
    assert not await check_deleted_handlers(
        web_context, [handler.id for handler in applied_config.handlers],
    )


async def check_deleted_configs(
        context: types.AnyContext, config_ids: List[int],
) -> bool:
    query = f"""
        SELECT id FROM dashboards.configs
        WHERE id = ANY(ARRAY{config_ids}::INT[])
          AND is_deleted
        """
    rows = await context.pg.primary.fetch(query)
    deleted_ids = sorted(row['id'] for row in rows)
    return sorted(config_ids) == deleted_ids


async def check_deleted_handlers(
        context: types.AnyContext, handler_ids: List[int],
) -> bool:
    query = f"""
        SELECT id FROM dashboards.handlers
        WHERE id = ANY(ARRAY{handler_ids}::INT[])
          AND is_deleted
        """
    rows = await context.pg.primary.fetch(query)
    deleted_ids = sorted(row['id'] for row in rows)
    return sorted(handler_ids) == deleted_ids


@pytest.mark.parametrize(
    '',
    [
        pytest.param(id='create_new_service_and_config'),
        pytest.param(
            id='create_only_config',
            marks=[pytest.mark.pgsql('dashboards', files=['init_data.sql'])],
        ),
    ],
)
@pytest.mark.usefixtures('clownductor_mock', 'clowny_balancer_mock')
@pytest.mark.config(
    DASHBOARDS_GRAFANA_ACTIVE_LAYOUTS={'http': {'is_active': True}},
)
async def test_upload_config_with_service_upsert(web_app_client):
    expected_config = copy.deepcopy(DASHBOARD_DIFF_HANDLERS_CONFIG_MOCK)
    response = await web_app_client.post(
        '/v1/configs/upload',
        params=UPLOAD_CONFIG_PARAMS_MOCK,
        json=expected_config,
    )
    content = await response.json()
    assert response.status == 200, content
    assert content['is_created']
    assert content['config'] == expected_config


@pytest.mark.parametrize(
    'service_branch_id, project_name, service_name, expected_dashboard_name',
    [
        pytest.param(
            1, 'taxi', 'test-service-1', 'nanny_taxi_test-service-1_stable',
        ),
        pytest.param(
            2,
            'taxi-devops',
            'test-service-2',
            'nanny_taxi_test-service-2_stable',
            id='use_overridden_project_name',
        ),
        pytest.param(
            3, 'eda', 'test-service-3', 'nanny_eda_test-service-3_stable',
        ),
        pytest.param(
            4, 'lavka', 'test-service-4', 'nanny_lavka_test-service-4_stable',
        ),
    ],
)
@pytest.mark.pgsql('dashboards', files=['init_services.sql'])
async def test_upload_config_dashboard_name(
        web_app_client,
        get_dashboard_configs_count,
        service_branch_id,
        project_name,
        service_name,
        expected_dashboard_name,
):
    expected_config = copy.deepcopy(DASHBOARD_SIMPLE_CONFIG_MOCK)
    params = {
        **UPLOAD_CONFIG_PARAMS_MOCK,
        'project_name': project_name,
        'service_name': service_name,
    }
    response = await web_app_client.post(
        '/v1/configs/upload', params=params, json=expected_config,
    )
    assert response.status == 200

    content = await response.json()
    assert content['is_created']
    assert content['config'] == expected_config, str(content)

    configs_count_after_upload = await get_dashboard_configs_count(
        service_branch_id=service_branch_id,
        dashboard_name=expected_dashboard_name,
    )
    assert configs_count_after_upload == 1


@pytest.mark.parametrize(
    'suffix',
    [
        pytest.param({'suffix': 'cool_web_unit'}, id='with_suffix'),
        pytest.param({}, id='without_suffix'),
    ],
)
@pytest.mark.pgsql(
    'dashboards',
    files=[
        'init_data.sql',
        'add_applied_config_with_uniq_handler.sql',
        'add_waiting_config_with_common_handler.sql',
    ],
)
async def test_upload_config_with_suffix(web_app_client, suffix):
    expected_config = copy.deepcopy(DASHBOARD_SAME_CONFIG_MOCK)
    upload_params = copy.deepcopy(UPLOAD_CONFIG_PARAMS_MOCK)
    upload_params.update(suffix)

    response = await web_app_client.post(
        '/v1/configs/upload', params=upload_params, json=expected_config,
    )
    assert response.status == 200
    content = await response.json()
    if suffix:
        assert content['is_created']
    else:
        assert not content['is_created']

    assert content['config'] == expected_config, str(content)


@pytest.mark.parametrize(
    'project_name, service_name, is_api_flow_enabled',
    [
        pytest.param(
            'taxi',
            'test-service-1',
            True,
            id='api_flow_enabled_with_service_override',
        ),
        pytest.param(
            'taxi-devops',
            'test-service-2',
            False,
            id='api_flow_disabled_with_service_override',
        ),
        pytest.param(
            'eda', 'test-service-3', True, id='api_flow_as_project_default',
        ),
        pytest.param(
            'lavka', 'test-service-4', False, id='api_flow_as_global_default',
        ),
    ],
)
@pytest.mark.config(
    DASHBOARDS_CONFIGS_SERVICE_SETTINGS={
        '__default__': {'use_api_flow': False},
        'taxi': {
            '__default__': {'use_api_flow': False},
            'test-service-1': {'use_api_flow': True},
        },
        'taxi-devops': {
            '__default__': {'use_api_flow': True},
            'test-service-2': {'use_api_flow': False},
        },
        'eda': {'__default__': {'use_api_flow': True}},
    },
)
@pytest.mark.pgsql('dashboards', files=['init_services.sql'])
async def test_upload_config_for_api_flow_enabled(
        web_app_client, project_name, service_name, is_api_flow_enabled,
):
    expected_config = copy.deepcopy(DASHBOARD_SIMPLE_CONFIG_MOCK)
    params = {
        **UPLOAD_CONFIG_PARAMS_MOCK,
        'project_name': project_name,
        'service_name': service_name,
    }
    response = await web_app_client.post(
        '/v1/configs/upload', params=params, json=expected_config,
    )

    if is_api_flow_enabled:
        assert response.status == 200
        content = await response.json()
        assert content['is_created']
        assert content['config'] == expected_config, str(content)
    else:
        assert response.status == 400
        content = await response.json()
        assert content['code'] == 'UPLOAD_DISABLED'
