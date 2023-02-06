# pylint: disable=too-many-lines
import json

import pytest

from clownductor.internal import diff
from clownductor.internal.utils import postgres

DIFF_PARAMETERS = [
    {
        'subsystem_name': 'service_info',
        'parameters': ['duty_group_id', 'duty', 'clownductor_project'],
    },
    {
        'subsystem_name': 'abc',
        'parameters': ['service_name', 'description', 'maintainers'],
    },
    {
        'subsystem_name': 'nanny',
        'parameters': [
            'cpu',
            'ram',
            'instances',
            'datacenters_count',
            'root_size',
            'persistent_volumes',
            'work_dir',
            'datacenters_regions',
        ],
    },
]


DIFF_SERVICES = {'services': ['service_exist', 'service_2']}


DIFF_BRANCH_STABLE = [
    {
        'subsystem_name': 'abc',
        'parameters': [
            {
                'name': 'maintainers',
                'value': {
                    'new': ['karachevda', 'meow'],
                    'old': ['kus', 'karachevda'],
                },
            },
            {
                'name': 'service_name',
                'value': {
                    'old': {'ru': 'Крутой Сервис', 'en': 'Cool Service'},
                    'new': {'ru': 'Сервис', 'en': 'Service'},
                },
            },
        ],
    },
    {
        'subsystem_name': 'nanny',
        'parameters': [
            {
                'name': 'persistent_volumes',
                'value': {
                    'new': [
                        {
                            'size': 10240,
                            'path': '/logs',
                            'type': 'hdd',
                            'bandwidth_guarantee_mb_per_sec': 3,
                            'bandwidth_limit_mb_per_sec': 6,
                        },
                    ],
                },
            },
            {'name': 'root_size', 'value': {'new': 10240, 'old': 5120}},
            {'name': 'work_dir', 'value': {'new': 512, 'old': 256}},
        ],
    },
    {
        'parameters': [
            {
                'name': 'clownductor_project',
                'value': {'new': 'taxi', 'old': 'taxi_new'},
            },
            {
                'name': 'duty_group_id',
                'value': {
                    'new': 'SERVICE_ilya_duty_1',
                    'old': 'REMOTE_ilya_duty_22',
                },
            },
        ],
        'subsystem_name': 'service_info',
    },
]
CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS = {
    'components': ['duty'],
    'description_template': {'diff_resolve': 'Параметры диффа:\n{params}'},
    'summary_template': {
        'diff_resolve': (
            'New diff RTC-service {project_name}-{service_name} '
            'environment:{env}'
        ),
    },
}


@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS,
    CLOWNDUCTOR_DIFF_CONFIGURATION=DIFF_SERVICES,
)
@pytest.mark.parametrize(
    'branch_id, expected_config',
    [
        pytest.param(
            1,
            {
                'abc': {
                    'stable': {
                        'maintainers': {
                            'old': ['kus', 'karachevda'],
                            'new': ['karachevda', 'meow'],
                        },
                        'service_name': {
                            'new': {'en': 'Service', 'ru': 'Сервис'},
                            'old': {
                                'en': 'Cool Service',
                                'ru': 'Крутой Сервис',
                            },
                        },
                    },
                },
                'nanny': {
                    'stable': {
                        'persistent_volumes': {
                            'new': [
                                {
                                    'size': 10240,
                                    'path': '/logs',
                                    'type': 'hdd',
                                    'bandwidth_guarantee_mb_per_sec': 3,
                                    'bandwidth_limit_mb_per_sec': 6,
                                },
                            ],
                            'old': None,
                        },
                        'root_size': {'new': 10240, 'old': 5120},
                        'work_dir': {'new': 512, 'old': 256},
                    },
                },
                'service_info': {
                    'stable': {
                        'clownductor_project': {
                            'new': 'taxi',
                            'old': 'taxi_new',
                        },
                        'duty_group_id': {
                            'new': 'SERVICE_ilya_duty_1',
                            'old': 'REMOTE_ilya_duty_22',
                        },
                    },
                },
            },
        ),
        pytest.param(
            2,
            {
                'nanny': {
                    'testing': {
                        'instances': {'old': 1, 'new': 2},
                        'datacenters_count': {'old': 1, 'new': 2},
                        'persistent_volumes': {
                            'new': [
                                {
                                    'bandwidth_guarantee_mb_per_sec': 3,
                                    'bandwidth_limit_mb_per_sec': 6,
                                    'path': '/logs',
                                    'size': 10240,
                                    'type': 'hdd',
                                },
                            ],
                            'old': [
                                {
                                    'bandwidth_guarantee_mb_per_sec': 9,
                                    'bandwidth_limit_mb_per_sec': 12,
                                    'path': '/logs',
                                    'size': 10240,
                                    'type': 'hdd',
                                },
                            ],
                        },
                    },
                },
            },
        ),
        pytest.param(
            3,
            {
                'nanny': {
                    'unstable': {
                        'cpu': {'new': 1000, 'old': 500},
                        'ram': {'new': 1000, 'old': 500},
                    },
                },
            },
        ),
        pytest.param(5, {}),
        pytest.param(
            12,
            {},
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES={'diff_validation': True},
                ),
            ],
        ),
        pytest.param(
            13,
            {},
            id='no diff for datacenter_regions null',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES={
                        'diff_validation': True,
                        'enable_ignore_datacenter_regions_null': True,
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_calculate_diff(web_context, branch_id, expected_config):
    branch = await web_context.service_manager.branches.get_by_id(branch_id)
    service = await web_context.service_manager.services.get_by_id(
        branch['service_id'],
    )
    diff_config = await diff.get_diff_config(
        web_context, service, branch, conn=None,
    )
    dumped = {}
    for diff_value in diff_config.calculate_diff():
        sub_dump = dumped.setdefault(diff_value.subsystem_name, {})
        env_dump = sub_dump.setdefault(diff_value.env, {})
        env_dump[diff_value.param_name] = {
            'old': diff_value.remote.value,
            'new': diff_value.current.value,
        }

    assert dumped == expected_config


@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS,
    CLOWNDUCTOR_DIFF_CONFIGURATION=DIFF_SERVICES,
    CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS=(
        CLOWNDUCTOR_NEW_SERVICE_TICKET_SETTINGS
    ),
    CLOWNDUCTOR_FEATURES={
        'diff_validation': True,
        'diff_resolve_draft_ticket': True,
    },
)
@pytest.mark.parametrize(
    'body,status,error_code,expected_response',
    [
        ({'branch_id': 1}, 200, None, 'expected_response_diff_check_1.json'),
        ({'branch_id': 6}, 400, 'DIFF_VALIDATION_ERROR', None),
        ({'branch_id': -1}, 404, 'NOT_FOUND', None),
        ({'branch_id': 5}, 400, 'DIFF_EMPTY', None),
        ({'branch_id': 1}, 409, 'DIFF_ALREADY_PROCESSING', None),
        ({'branch_id': 10}, 400, 'DIFF_CALCULATE_ERROR', None),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_resolve_diff_check_handle(
        mockserver,
        web_app_client,
        body,
        status,
        error_code,
        expected_response,
        load_json,
):
    @mockserver.json_handler('/client-abc/v4/duty/schedules-cursor/')
    def _schedules_cursor_handler(request):
        return {
            'results': [
                {
                    'id': 1,
                    'name': 'существующее расписание',
                    'slug': 'existing-schedule',
                },
            ],
            'next': None,
            'previous': None,
        }

    url = '/v1/parameters/diff/resolve/check/'
    if status == 409:
        await web_app_client.post(
            '/v1/parameters/diff/resolve/',
            json={'branch_id': 1, 'diff': DIFF_BRANCH_STABLE},
            headers={'X-Yandex-Login': 'karachevda'},
        )
    response = await web_app_client.post(
        url, json=body, headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()
    assert response.status == status, f'{response_body}'
    if status == 200:
        assert response_body == load_json(expected_response)
    else:
        assert response_body['code'] == error_code


@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS,
    CLOWNDUCTOR_DIFF_CONFIGURATION=DIFF_SERVICES,
    CLOWNDUCTOR_FEATURES={
        'diff_validation': True,
        'use_remote_clownductor_project': True,
        'check_diff_conflict': True,
        'diff_check_active_deploys': True,
    },
)
@pytest.mark.parametrize(
    'body,status,error_code',
    [
        pytest.param({'branch_id': 1, 'diff': DIFF_BRANCH_STABLE}, 200, None),
        pytest.param(
            {
                'branch_id': 6,
                'diff': [
                    {
                        'parameters': [
                            {
                                'name': 'persistent_volumes',
                                'value': {'new': None, 'old': []},
                            },
                            {
                                'name': 'datacenters_count',
                                'value': {'new': 4, 'old': 1},
                            },
                            {
                                'name': 'cpu',
                                'value': {'new': 100, 'old': 1000},
                            },
                            {
                                'name': 'ram',
                                'value': {'new': 500, 'old': 1000},
                            },
                            {
                                'name': 'root_size',
                                'value': {'new': 10, 'old': 5120},
                            },
                        ],
                        'subsystem_name': 'nanny',
                    },
                ],
            },
            400,
            'DIFF_VALIDATION_ERROR',
        ),
        pytest.param(
            {
                'branch_id': 1,
                'diff': [
                    {
                        'subsystem_name': 'abc',
                        'parameters': [
                            {
                                'name': 'maintainers',
                                'value': {
                                    'new': ['karachevda', 'meow'],
                                    'old': ['kus', 'karachevda'],
                                },
                            },
                        ],
                    },
                ],
            },
            409,
            'DIFF_CONFLICT',
        ),
        pytest.param({'branch_id': -1}, 404, 'NOT_FOUND'),
        pytest.param({'branch_id': 5, 'diff': []}, 400, 'DIFF_EMPTY'),
        pytest.param({'branch_id': 2, 'diff': []}, 400, 'DEPLOY_RUNNING'),
        pytest.param({'branch_id': 11, 'diff': []}, 200, None),
        pytest.param(
            {'branch_id': 13, 'diff': []},
            400,
            'DIFF_EMPTY',
            id='no diff for datacenter_regions:null',
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'check_diff_conflict': True,
                    'diff_validation': True,
                    'enable_ignore_datacenter_regions_null': True,
                },
            ),
        ),
        pytest.param(
            {
                'branch_id': 14,
                'diff': [
                    {
                        'parameters': [
                            {
                                'name': 'datacenters_count',
                                'value': {'new': 2, 'old': 3},
                            },
                            {
                                'name': 'datacenters_regions',
                                'value': {
                                    'new': ['vla', 'sas'],
                                    'old': ['vla', 'sas', 'man'],
                                },
                            },
                        ],
                        'subsystem_name': 'nanny',
                    },
                ],
            },
            200,
            None,
            id='diff for datacenter_regions not null',
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'check_diff_conflict': True,
                    'diff_check_active_deploys': True,
                    'diff_validation': True,
                    'use_remote_clownductor_project': True,
                    'enable_ignore_datacenter_regions_null': True,
                },
            ),
        ),
        pytest.param(
            {
                'branch_id': 15,
                'diff': [
                    {
                        'parameters': [
                            {
                                'name': 'datacenters_regions',
                                'value': {
                                    'new': ['man', 'sas'],
                                    'old': ['vla', 'sas'],
                                },
                            },
                        ],
                        'subsystem_name': 'nanny',
                    },
                ],
            },
            400,
            'DIFF_VALIDATION_ERROR',
            marks=pytest.mark.features_on(
                'diff_validation',
                'use_remote_clownductor_project',
                'enable_ignore_datacenter_regions_null',
                'enable_datacenter_regions_validator',
                'check_diff_conflict',
                'diff_check_active_deploys',
            ),
        ),
        pytest.param(
            {
                'branch_id': 16,
                'diff': [
                    {
                        'parameters': [
                            {
                                'name': 'datacenters_count',
                                'value': {'new': 2, 'old': 3},
                            },
                            {
                                'name': 'datacenters_regions',
                                'value': {
                                    'new': ['vla', 'sas'],
                                    'old': ['vla', 'sas', 'man'],
                                },
                            },
                        ],
                        'subsystem_name': 'nanny',
                    },
                ],
            },
            200,
            None,
            id='test subset',
            marks=pytest.mark.features_on(
                'diff_validation',
                'use_remote_clownductor_project',
                'enable_ignore_datacenter_regions_null',
                'enable_datacenter_regions_validator',
                'check_diff_conflict',
                'diff_check_active_deploys',
            ),
        ),
    ],
)
@pytest.mark.pgsql('clownductor', ['init_service.sql', 'add_deploy_jobs.sql'])
async def test_resolve_diff_handle(
        mockserver, web_app_client, body, status, error_code,
):
    @mockserver.json_handler('/client-abc/v4/duty/schedules-cursor/')
    def _schedules_cursor_handler(request):
        return {
            'results': [
                {
                    'id': 1,
                    'name': 'существующее расписание',
                    'slug': 'existing-schedule',
                },
            ],
            'next': None,
            'previous': None,
        }

    url = '/v1/parameters/diff/resolve/'

    response = await web_app_client.post(
        url, json=body, headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()
    assert response.status == status, f'{response_body}'
    if status == 200:
        assert response_body == {'job_id': 4}
    else:
        assert response_body['code'] == error_code


@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS,
    CLOWNDUCTOR_DIFF_CONFIGURATION=DIFF_SERVICES,
)
@pytest.mark.pgsql(
    'clownductor', files=['init_service.sql', 'add_deploy_jobs.sql'],
)
async def test_resolve_diff_handle_idempotency(web_app_client, patch):
    body = {'branch_id': 1}
    response = await web_app_client.post(
        '/v1/parameters/diff/resolve/',
        json=body,
        headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()
    assert response.status == 200
    assert response_body == {'job_id': 4}

    @patch('clownductor.internal.jobs.Jobs.get_active_by_change_doc_id')
    async def _get_active_by_change_doc_id(*args, **kwargs):
        return None

    __get_active_by_change_doc_id_mock = _get_active_by_change_doc_id

    response = await web_app_client.post(
        '/v1/parameters/diff/resolve/',
        json=body,
        headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()

    assert response.status == 409
    assert response_body == {
        'code': 'DIFF_ALREADY_PROCESSING',
        'message': 'Diff already resolving',
    }
    assert len(__get_active_by_change_doc_id_mock.calls) == 1


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.parametrize(
    'service_id,branch_id,has_url,expected_params,error_code,status',
    [
        pytest.param(
            1,
            1,
            False,
            [
                {
                    'service_values': {
                        'clownductor_project': 'taxi',
                        'duty_group_id': 'Hola Amigos',
                        'duty': None,
                        'network': '__HOLA_AMIGOS_STABLE_NETWORK_',
                    },
                    'subsystem_name': 'service_info',
                },
                {'service_values': {}, 'subsystem_name': 'awacs'},
                {
                    'service_values': {
                        'cpu': 1000,
                        'instances': 1,
                        'datacenters_count': 2,
                        'datacenters_regions': ['vla', 'man', 'sas'],
                        'persistent_volumes': [],
                        'ram': 2048,
                        'root_size': 10240,
                        'work_dir': 256,
                        'root_storage_class': 'hdd',
                        'root_bandwidth_guarantee_mb_per_sec': 1,
                        'root_bandwidth_limit_mb_per_sec': 2,
                        'network_bandwidth_guarantee_mb_per_sec': 8,
                    },
                    'subsystem_name': 'nanny',
                },
                {
                    'service_values': {
                        'description': {
                            'en': 'The cool one',
                            'ru': 'Крутой сервис',
                        },
                        'maintainers': ['deoevgen', 'karachevda'],
                        'service_name': {
                            'en': 'clownductor',
                            'ru': 'clownductor',
                        },
                    },
                    'subsystem_name': 'abc',
                },
            ],
            None,
            200,
        ),
        pytest.param(1, 1, True, None, 'SERVICE_YAML_OVERRIDE_ERROR', 400),
        pytest.param(1, 5, True, None, 'WRONG_SERVICE', 400),
        pytest.param(
            1,
            3,
            True,
            [
                {
                    'service_values': {
                        'cpu': 1000,
                        'instances': 1,
                        'datacenters_count': 1,
                        'datacenters_regions': ['vla', 'man', 'sas'],
                        'persistent_volumes': [],
                        'ram': 4096,
                        'root_size': 10240,
                        'work_dir': 256,
                        'root_storage_class': 'hdd',
                        'root_bandwidth_guarantee_mb_per_sec': 1,
                        'root_bandwidth_limit_mb_per_sec': 2,
                        'network_bandwidth_guarantee_mb_per_sec': 8,
                    },
                    'subsystem_name': 'nanny',
                },
            ],
            None,
            200,
        ),
        pytest.param(
            1,
            1,
            False,
            [
                {
                    'service_values': {
                        'clownductor_project': 'taxi',
                        'duty_group_id': 'Hola Amigos',
                        'duty': None,
                        'network': '__HOLA_AMIGOS_STABLE_NETWORK_',
                    },
                    'subsystem_name': 'service_info',
                },
                {'service_values': {}, 'subsystem_name': 'awacs'},
                {
                    'service_values': {
                        'cpu': 1000,
                        'instances': 1,
                        'datacenters_count': 2,
                        'datacenters_regions': None,
                        'persistent_volumes': [],
                        'ram': 2048,
                        'root_size': 10240,
                        'work_dir': 256,
                        'root_storage_class': 'hdd',
                        'root_bandwidth_guarantee_mb_per_sec': 1,
                        'root_bandwidth_limit_mb_per_sec': 2,
                        'network_bandwidth_guarantee_mb_per_sec': 8,
                    },
                    'subsystem_name': 'nanny',
                },
                {
                    'service_values': {
                        'description': {
                            'en': 'The cool one',
                            'ru': 'Крутой сервис',
                        },
                        'maintainers': ['deoevgen', 'karachevda'],
                        'service_name': {
                            'en': 'clownductor',
                            'ru': 'clownductor',
                        },
                    },
                    'subsystem_name': 'abc',
                },
            ],
            None,
            200,
            id='test nullable datacenter_regions',
            marks=[
                pytest.mark.config(
                    CLOWNDUCTOR_FEATURES_PER_SERVICE={
                        '__default__': {},
                        'taxi': {
                            '__default__': {},
                            'service_exist': {
                                'feat_duty_group_id': True,
                                'use_remote_clownductor_project': True,
                                'enable_ignore_datacenter_regions_null': True,
                            },
                        },
                    },
                ),
            ],
        ),
    ],
)
@pytest.mark.features_on('use_network_guarantee_config')
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'feat_duty_group_id': True,
        'use_remote_clownductor_project': True,
    },
)
async def test_service_values_sync(
        patch_github_single_file,
        web_context,
        service_id,
        web_app_client,
        has_url,
        branch_id,
        expected_params,
        error_code,
        status,
):
    body = {'branch_id': branch_id, 'service_id': service_id}
    if has_url:
        url = (
            'https://github.yandex-team.ru/taxi/backend-py3/blob/develop/'
            'clownductor/service.yaml'
        )
        body['service_yaml_url'] = url

    get_single_file = patch_github_single_file(
        'clownductor/service.yaml', 'clownductor_py3.yaml',
    )

    response = await web_app_client.post(
        '/v1/parameters/service_values/sync/',
        json=body,
        headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()
    assert response.status == status
    if status != 200:
        assert response_body['code'] == error_code
        return
    assert response_body == {}

    assert len(get_single_file.calls) == 1

    rows = await _get_parameters(web_context, service_id, branch_id, None)
    expected = []
    for row in rows:
        expected.append(
            {
                'subsystem_name': row['subsystem_name'],
                'service_values': row['service_values'],
            },
        )

    assert expected_params == expected


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'feat_duty_group_id': True,
        'use_remote_clownductor_project': True,
    },
)
async def test_conductor_service_values_sync(
        patch_github_single_file, web_context, web_app_client,
):
    body = {'branch_id': 9, 'service_id': 3}

    patch_github_single_file(
        'admin-users-info/service.yaml', 'admin-users-info_py3.yaml',
    )

    response = await web_app_client.post(
        '/v1/parameters/service_values/sync/',
        json=body,
        headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()
    assert response_body == {}

    rows = await _get_parameters(web_context, 3, 9, 'service_info')
    assert len(rows) == 1
    row = rows[0]
    service_values = row['service_values']
    assert service_values['duty_group_id'] == '5f724de38ef826475c624741'
    assert service_values['duty'] is None
    assert len(service_values) == 2


# TODO: see TAXIPLATFORM-4701
@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS,
    CLOWNDUCTOR_DIFF_CONFIGURATION=DIFF_SERVICES,
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_change_abc_subsystem(
        task_processor,
        run_job_common,
        web_context,
        abc_mockserver,
        abc_nonofficial_mockserver,
        load_yaml,
):
    abc_mockserver(services=['abc_service'])
    abc_nonofficial_mockserver()

    recipe = task_processor.load_recipe(
        load_yaml('recipes/ChangeAbcSubsystem.yaml')['data'],
    )
    job = await recipe.start_job(
        job_vars={
            'environment': 'stable',
            'branch_id': 1,
            'service_id': 1,
            'subsystem_name': 'abc',
            'new_parameters': {'maintainers': ['test2', 'karachevda']},
            'team_members_to_delete': ['test1'],
            'new_team_members': ['test2'],
            'service_slug': 'abc_service',
        },
        initiator='clownductor',
    )
    await run_job_common(job)

    parameters = await _get_parameters(web_context, 1, 1, 'abc')
    assert parameters[0]['remote_values'] == {
        'maintainers': ['test2', 'karachevda'],
        'service_name': {'en': 'Cool Service', 'ru': 'Крутой Сервис'},
        'description': {'en': 'Service', 'ru': 'Сервис'},
    }


@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.features_on('feat_duty_group_id')
@pytest.mark.features_on('use_remote_clownductor_project')
@pytest.mark.features_on(
    'enable_io_limits_params_remote',
    'enable_io_limits_params_yaml',
    'enable_io_limits_params_apply',
)
@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS,
    CLOWNDUCTOR_DIFF_CONFIGURATION=DIFF_SERVICES,
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_resolve_diff_execution(
        mockserver,
        task_processor,
        run_job_with_meta,
        patch,
        web_app_client,
        get_job,
        abc_mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
        staff_mockserver,
        awacs_mockserver,
        load_yaml,
        load_json,
        nanny_yp_list_pods_groups,
        nanny_yp_pod_reallocation_spec,
        nanny_yp_start_pod_reallocation,
        yp_mockserver,
):
    abc_mockserver(services=['abc_service'])
    nanny_yp_mockserver()
    staff_mockserver()
    awacs_mockserver()
    yp_mockserver()

    @patch(
        'clownductor.generated.service.conductor_api.'
        'plugin.ConductorClient.get_approvers',
    )
    async def _get_approvers(*args, **kwargs):  # pylint: disable=W0612
        return ['mvpetrov', 'karachevda', 'd1mbas']

    @mockserver.json_handler(
        '/client-nanny/v2/services/test_nanny_service/current_state/',
        prefix=True,
    )
    async def _handler(request):
        return load_json('nanny_service_current_state.json')

    body = {'branch_id': 1}
    response = await web_app_client.post(
        '/v1/parameters/diff/resolve/',
        json=body,
        headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()
    assert response.status == 200
    assert response_body == {'job_id': 1}

    task_processor.load_recipe(
        load_yaml('recipes/ChangeAbcSubsystem.yaml')['data'],
    )
    recipes_path = '../../../cubes_handles/recipes/static/default/recipes'
    task_processor.load_recipe(
        load_yaml(f'{recipes_path}/ChangeServiceResources.yaml')['data'],
    )
    task_processor.load_recipe(
        load_yaml(f'{recipes_path}/ReallocateOneNannyService.yaml')['data'],
    )

    job = (await get_job(1))[0]['job']
    assert job.pop('created_at')
    assert job == {
        'id': 1,
        'branch_id': 1,
        'service_id': 1,
        'name': 'ResolveServiceDiff',
        'initiator': 'karachevda',
        'status': 'inited',
        'remote_job_id': 1,
        'change_doc_id': '1_1_ResolveServiceDiff',
    }
    job = task_processor.find_job(1)
    await run_job_with_meta(job)


@pytest.mark.usefixtures('mock_internal_tp')
@pytest.mark.features_on(
    'enable_io_limits_params_remote', 'enable_io_limits_params_yaml',
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_sync_service_remote_parameters(
        task_processor,
        run_job_common,
        web_context,
        web_app_client,
        get_job,
        abc_mockserver,
        abc_nonofficial_mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
):
    abc_mockserver(services=['abc_service'])
    abc_nonofficial_mockserver()
    nanny_yp_mockserver()

    body = {'branch_id': 1, 'service_id': 1}
    response = await web_app_client.post(
        '/v1/parameters/remote_values/sync/',
        json=body,
        headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()
    assert response.status == 200, f'{response_body}'
    assert response_body == {'job_id': 1}

    job = (await get_job(1))[0]['job']
    assert job.pop('created_at')
    assert job == {
        'id': 1,
        'branch_id': 1,
        'service_id': 1,
        'name': 'SyncServiceRemoteParameters',
        'initiator': 'karachevda',
        'status': 'inited',
        'change_doc_id': '1_1_SyncServiceRemoteParameters',
        'remote_job_id': 1,
    }

    job = task_processor.find_job(job['id'])
    await run_job_common(job)

    parameter_ids = []
    for task in job.tasks:
        if task.cube.name in ('SaveRemoteNannyConfig', 'SaveRemoteAbcConfig'):
            parameter_ids.extend(task.payload['parameters_ids'])

    nanny_parameter = (await _get_parameters(web_context, 1, 1, 'nanny'))[0]
    abc_parameter = (await _get_parameters(web_context, 1, 1, 'abc'))[0]
    real_ids = [nanny_parameter['id'], abc_parameter['id']]
    assert set(parameter_ids) == set(real_ids)

    # careful this mock from library nanny-yp
    assert nanny_parameter['remote_values'] == {
        'cpu': 1000,
        'instances': 2,
        'datacenters_count': 1,
        'datacenters_regions': ['vla'],
        'ram': 2048,
        'root_size': 512,
        'work_dir': 512,
        'root_storage_class': 'hdd',
        'root_bandwidth_guarantee_mb_per_sec': 10,
        'root_bandwidth_limit_mb_per_sec': 20,
        'network_bandwidth_guarantee_mb_per_sec': 0,
        'persistent_volumes': [
            {
                'size': 10240,
                'path': '/logs',
                'type': 'hdd',
                'bandwidth_guarantee_mb_per_sec': 10,
                'bandwidth_limit_mb_per_sec': 20,
            },
        ],
    }
    assert abc_parameter['remote_values'] == {
        'description': {'en': '', 'ru': ''},
        'maintainers': ['isharov', 'nikslim'],
        'service_name': {
            'en': 'TVM for billing_orders service (TAXIADMIN-6231) - testing',
            'ru': 'TVM для сервиса billing_orders (TAXIADMIN-6231) - testing',
        },
    }


@pytest.mark.parametrize(
    'service_id,branch_id,expected_parameters,is_remote,updating_job_id',
    [
        pytest.param(
            1,
            1,
            {
                'nanny': [
                    'cpu',
                    'ram',
                    'instances',
                    'datacenters_count',
                    'persistent_volumes',
                    'root_size',
                    'work_dir',
                ],
                'abc': ['description', 'maintainers', 'service_name'],
                'service_info': [
                    'clownductor_project',
                    'grafana',
                    'duty_group_id',
                ],
            },
            False,
            None,
            id='search_for_service_n_branch-stable',
        ),
        pytest.param(
            1,
            None,
            {
                'service_info': [
                    'clownductor_project',
                    'duty_group_id',
                    'service_type',
                    'critical_class',
                ],
            },
            False,
            None,
            id='search_for_service',
        ),
        pytest.param(
            1,
            2,
            {
                'nanny': [
                    'cpu',
                    'ram',
                    'root_size',
                    'datacenters_count',
                    'instances',
                    'work_dir',
                    'persistent_volumes',
                ],
            },
            False,
            None,
            id='search_for_service_n_branch-testing',
        ),
        pytest.param(
            1,
            1,
            {
                'nanny': [
                    'cpu',
                    'ram',
                    'root_size',
                    'datacenters_count',
                    'instances',
                    'work_dir',
                ],
                'abc': ['description', 'maintainers', 'service_name'],
                'service_info': [
                    'clownductor_project',
                    'grafana',
                    'duty_group_id',
                ],
            },
            True,
            2,
            id='search_for_service_n_branch-stable-remote',
        ),
        pytest.param(
            1,
            2,
            {
                'nanny': [
                    'cpu',
                    'ram',
                    'root_size',
                    'datacenters_count',
                    'instances',
                    'work_dir',
                    'persistent_volumes',
                ],
            },
            True,
            1,
            id='search_for_service_n_branch-testing-remote',
        ),
        pytest.param(
            1,
            2,
            {
                'nanny': [
                    'cpu',
                    'ram',
                    'root_size',
                    'datacenters_count',
                    'instances',
                    'work_dir',
                    'persistent_volumes',
                ],
            },
            True,
            None,
        ),
        pytest.param(
            5,
            13,
            {
                'awacs': [
                    'cpu',
                    'ram',
                    'datacenters_instances',
                    'persistent_volumes',
                    'root_volume',
                ],
                'nanny': [
                    'cpu',
                    'ram',
                    'root_size',
                    'datacenters_count',
                    'instances',
                    'work_dir',
                ],
            },
            False,
            None,
            id='test awacs preset in response',
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_get_service_parameters(
        web_app_client,
        service_id,
        branch_id,
        expected_parameters,
        is_remote,
        updating_job_id,
        patch,
):
    @patch('clownductor.internal.jobs.Jobs.get_active_by_change_doc_id')
    async def _get_active_by_change_doc_id(*args, **kwargs):
        return {'id': updating_job_id}

    params = {'service_id': service_id}
    if branch_id:
        params['branch_id'] = branch_id
    url = '/v1/parameters/service_values/'
    if is_remote:
        url = '/v1/parameters/remote_values/'
    response = await web_app_client.get(
        url, params=params, headers={'X-Yandex-Login': 'karachevda'},
    )

    response_body = await response.json()

    for subsystem in response_body['subsystems']:
        assert subsystem['updated_at']

    await _check_get_parameters_response(
        response,
        response_body,
        expected_parameters,
        updating_job_id,
        'updating_job_id',
    )


@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS,
    CLOWNDUCTOR_DIFF_CONFIGURATION=DIFF_SERVICES,
)
@pytest.mark.parametrize(
    'service_id,branch_id,expected_parameters,applying_job_id,draft_id',
    [
        (
            1,
            1,
            {
                'abc': ['maintainers', 'service_name'],
                'nanny': ['persistent_volumes', 'root_size', 'work_dir'],
                'service_info': ['clownductor_project', 'duty_group_id'],
            },
            None,
            None,
        ),
        (
            1,
            2,
            {
                'nanny': [
                    'instances',
                    'datacenters_count',
                    'persistent_volumes',
                ],
            },
            None,
            None,
        ),
        (
            1,
            2,
            {
                'nanny': [
                    'instances',
                    'datacenters_count',
                    'persistent_volumes',
                ],
            },
            2,
            1,
        ),
        (2, 5, {}, 2, None),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_get_diff(
        web_app_client,
        service_id,
        branch_id,
        expected_parameters,
        applying_job_id,
        draft_id,
        patch,
):
    @patch('clownductor.internal.jobs.Jobs.get_active_by_change_doc_id')
    async def _get_active_by_change_doc_id(*args, **kwargs):
        return {'id': applying_job_id}

    @patch('taxi.clients.approvals.ApprovalsApiClient.get_drafts')
    async def _get_drafts(*args, **kwargrs):
        return [] if not draft_id else [{'id': draft_id}]

    params = {'branch_id': branch_id, 'service_id': service_id}
    response = await web_app_client.get(
        '/v1/parameters/diff/',
        params=params,
        headers={'X-Yandex-Login': 'karachevda'},
    )
    response_body = await response.json()
    if draft_id:
        assert response_body.pop('active_draft_id') == draft_id
    await _check_get_parameters_response(
        response,
        response_body,
        expected_parameters,
        applying_job_id,
        'applying_job_id',
    )


async def _check_get_parameters_response(
        response, response_body, expected_parameters, job_id, job_id_name,
):
    assert response.status == 200, f'{response_body}'
    subsystems = response_body.pop('subsystems')

    assert len(subsystems) == len(
        expected_parameters,
    ), f'{subsystems} != {expected_parameters}'

    for subsystem in subsystems:
        expected_params = set(
            expected_parameters.pop(subsystem['subsystem_name']),
        )
        for param in subsystem['parameters']:
            assert param['value'] is not None
            expected_params.remove(param['name'])
        assert not expected_params
    assert not expected_parameters

    if job_id:
        assert response_body == {job_id_name: job_id}
    else:
        assert response_body == {}


def _dump_config(config):
    dumped = {}
    for name, value in config.parameters:
        dumped[name] = {'old': value.old, 'new': value.new}
    return dumped


async def _get_parameters(web_context, service_id, branch_id, subsystem_name):
    new_rows = []
    async with postgres.primary_connect(web_context) as conn:
        rows = await conn.fetch(
            """
            select
                p.id,
                p.subsystem_name,
                p.service_id,
                p.branch_id,
                p.remote_values,
                p.service_values
            from
                clownductor.parameters p
            where
                p.service_id = $1
                and p.branch_id = $2
            """,
            service_id,
            branch_id,
        )
    for row in rows:
        if (
                subsystem_name is not None
                and row['subsystem_name'] != subsystem_name
        ):
            continue
        row = dict(row)
        row['remote_values'] = json.loads(row['remote_values'])
        row['service_values'] = json.loads(row['service_values'])
        new_rows.append(row)
    return new_rows
