# pylint: disable=too-many-lines
# TODO(TAXIPLATFORM-4213): extract tests for service.yaml
import json

from aiohttp import web
import pytest

from clownductor.internal.tasks import cubes
from clownductor.internal.utils import postgres


GITHUB_ORG_URL = 'https://github.yandex-team.ru/taxi'


def task_data(name):
    return {
        'id': 123,
        'job_id': 1,
        'name': name,
        'sleep_until': 0,
        'input_mapping': {},
        'output_mapping': {},
        'payload': {},
        'retries': 0,
        'status': 'in_progress',
        'error_message': None,
        'created_at': 0,
        'updated_at': 0,
    }


DIFF_PARAMETERS = [
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
            'root_storage_class',
        ],
    },
]


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'disk_profiles': True})
@pytest.mark.features_on(
    'enable_io_limits_params_remote', 'enable_io_limits_params_yaml',
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.parametrize(
    'service_yaml', ['clownductor_py3.yaml', 'clownductor_py3_2.yaml'],
)
@pytest.mark.parametrize(
    'service_id, expected_config',
    [
        (
            1,
            {
                'abc': {
                    'stable': {
                        'maintainers': ['deoevgen', 'karachevda'],
                        'service_name': {
                            'en': 'clownductor',
                            'ru': 'clownductor',
                        },
                        'description': {
                            'en': 'The cool one',
                            'ru': 'Крутой сервис',
                        },
                    },
                },
                'nanny': {
                    'general': {
                        'reallocation_settings': {
                            'max_unavailable_pods_percent': 30,
                            'min_update_delay_seconds': 330,
                        },
                    },
                    'stable': {
                        'cpu': 1000,
                        'instances': 1,
                        'ram': 2048,
                        'datacenters_count': 2,
                        'datacenters_regions': ['vla', 'man', 'sas'],
                        'persistent_volumes': [
                            {
                                'path': '/cores',
                                'size': 10240,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                            {
                                'path': '/logs',
                                'size': 50000,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                            {
                                'path': '/var/cache/yandex',
                                'size': 2048,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                        ],
                        'root_size': 4096,
                        'work_dir': 256,
                        'root_storage_class': 'hdd',
                        'root_bandwidth_guarantee_mb_per_sec': 1,
                        'root_bandwidth_limit_mb_per_sec': 2,
                    },
                    'testing': {
                        'cpu': 1000,
                        'instances': 1,
                        'ram': 4096,
                        'datacenters_count': 2,
                        'datacenters_regions': ['vla', 'man', 'sas'],
                        'persistent_volumes': [
                            {
                                'path': '/cores',
                                'size': 10240,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                            {
                                'path': '/logs',
                                'size': 50000,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                            {
                                'path': '/var/cache/yandex',
                                'size': 2048,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                        ],
                        'root_size': 10240,
                        'work_dir': 256,
                        'root_storage_class': 'hdd',
                        'root_bandwidth_guarantee_mb_per_sec': 1,
                        'root_bandwidth_limit_mb_per_sec': 2,
                    },
                    'unstable': {
                        'cpu': 1000,
                        'instances': 1,
                        'ram': 4096,
                        'datacenters_count': 1,
                        'datacenters_regions': ['vla', 'man', 'sas'],
                        'persistent_volumes': [
                            {
                                'path': '/cores',
                                'size': 10240,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                            {
                                'path': '/logs',
                                'size': 50000,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                            {
                                'path': '/var/cache/yandex',
                                'size': 2048,
                                'type': 'hdd',
                                'bandwidth_guarantee_mb_per_sec': 1,
                                'bandwidth_limit_mb_per_sec': 2,
                            },
                        ],
                        'root_size': 10240,
                        'work_dir': 256,
                        'root_storage_class': 'hdd',
                        'root_bandwidth_guarantee_mb_per_sec': 1,
                        'root_bandwidth_limit_mb_per_sec': 2,
                    },
                },
                'service_info': {
                    'general': {
                        'hostnames': {
                            'production': ['clownductor.taxi.yandex.net'],
                            'testing': ['clownductor.taxi.tst.yandex.net'],
                        },
                        'clownductor_project': 'taxi',
                        'service_name': 'clownductor',
                        'service_type': 'backendpy3',
                        'description': None,
                        'service_yaml_url': (
                            'https://github.yandex-team.ru/'
                            'taxi/backend-py3/blob/develop/'
                            'clownductor/service.yaml'
                        ),
                        'wiki_path': 'https://wiki.yandex-team.ru',
                        'design_review': 'https://st.yandex-team.ru',
                        'critical_class': None,
                        'deploy_callback_url': None,
                        'duty_group_id': 'duty_id',
                        'duty': None,
                        'responsible_managers': None,
                        'release_flow': {'single_approve': True},
                        'tvm_name': 'clownductor',
                        'yt_log_replications': [
                            {
                                'table': 'table_name',
                                'url': 'https://yt.yandex-team.ru',
                            },
                        ],
                    },
                    'stable': {
                        'grafana': (
                            'https://grafana.yandex-team.ru/d/Ygx9WhhZk'
                            '/nanny_taxi_clownductor_stable'
                        ),
                        'clownductor_project': 'taxi',
                        'duty_group_id': 'duty_id',
                        'duty': None,
                    },
                    'testing': {
                        'grafana': (
                            'https://grafana.yandex-team.ru/d/GvwEwKhWk'
                            '/nanny_taxi_clownductor_testing'
                        ),
                    },
                },
            },
        ),
        (3, {'service_info': {'stable': {'service_type': 'python3'}}}),
    ],
)
async def test_update_service_yaml_params(
        web_context,
        service_yaml,
        service_id,
        expected_config,
        patch_github_single_file,
):
    get_single_file = patch_github_single_file(
        'clownductor/service.yaml', service_yaml,
    )
    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['UpdateServiceYamlParams'](
            web_context,
            task_data('UpdateServiceYamlParams'),
            {'service_id': service_id},
            [],
            conn,
        )
        await cube.update()
    assert cube.success
    calls = 1 if service_id == 1 else 0
    assert len(get_single_file.calls) == calls
    config = await _get_parameters(web_context, service_id)
    assert config == expected_config


@pytest.mark.config(
    CLOWNDUCTOR_DIFF_PARAMETERS=[
        {'subsystem_name': 'abc', 'parameters': ['maintainers']},
        {'subsystem_name': 'nanny', 'parameters': ['cpu']},
    ],
)
@pytest.mark.parametrize('cube_call_count', [1, 2])
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_sync_remote_params(web_context, get_job, cube_call_count):
    async with postgres.primary_connect(web_context) as conn:
        for _ in range(cube_call_count):
            cube = cubes.CUBES['StartSyncRemoteParams'](
                web_context,
                task_data('StartSyncRemoteParams'),
                {
                    'service_id': 1,
                    'branch_id': 1,
                    'aliases': [{'service_id': 2, 'branch_id': 5}],
                },
                [],
                conn,
            )
            await cube.update()
    assert cube.success
    assert cube.payload == {'job_ids': [2]}
    job = (await get_job(2))[0]['job']
    assert job['name'] == 'SyncServiceRemoteParameters'
    assert job['service_id'] == 2
    assert job['branch_id'] == 5


@pytest.mark.features_on('use_remote_clownductor_project')
@pytest.mark.parametrize(
    'old, new, result, status',
    [
        ('taxi', 'taxi_infra', 'taxi_infra', 'success'),
        ('taxi', 'taxi', None, 'success'),
        ('taxi', None, None, 'success'),
        ('taxi', 'Not_real_project', None, 'failed'),
    ],
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_cube_check_change_project(
        web_context, get_job, old, new, result, status, mock_task_processor,
):
    @mock_task_processor('/v1/jobs/start/')
    async def tp_handler(request):
        assert request.json.get('external_entities')
        assert request.json['external_entities'] == {
            'service': '1',
            'branch': '1',
        }
        job_vars = request.json['job_vars']
        assert list(job_vars.keys()) == [
            'new_project_id',
            'new_project_name',
            'old_project_name',
            'service_name',
            'service_id',
            'st_task',
        ]
        return web.json_response({'job_id': 2})

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaStartChangingProject'](
            web_context,
            task_data('MetaStartChangingProject'),
            {
                'service_id': 2,
                'subsystems_info': {
                    'service_info': {
                        'clownductor_project': {'old': old, 'new': new},
                    },
                },
                'st_task': 'st_task',
            },
            [],
            conn,
        )
        await cube.update()
        assert cube.status == status
        assert tp_handler.times_called == (
            1
            if cube.status == 'success'
            and cube.payload['change_project_job_id'] == 2
            else 0
        )


@pytest.mark.features_on('feat_duty_group_id')
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.parametrize(
    'duty_group',
    [
        pytest.param(
            {
                'old': '{"duty_group_id": "SERVICE_ilya_duty_1"}',
                'new': '{"duty_group_id": "Great"}',
                'change_old': 'SERVICE_ilya_duty_1',
                'change_new': 'Great',
                'result': 'Great',
            },
        ),
        pytest.param(
            {
                'old': '{"duty_group_id": "SERVICE_ilya_duty_1"}',
                'new': '{"duty_group_id": null}',
                'change_old': 'SERVICE_ilya_duty_1',
                'change_new': None,
                'result': None,
            },
            id='remove duty group',
        ),
    ],
)
async def test_cube_change_system_info(web_context, duty_group):
    async with postgres.primary_connect(web_context) as conn:
        await conn.fetch(
            f"""
            insert into clownductor.parameters
            (
                subsystem_name,
                service_id,
                branch_id,
                service_values,
                remote_values
              )
            values
                (
                    'service_info',
                    1,
                    1,
                    '{duty_group['old']}'::jsonb,
                    '{duty_group['new']}'::jsonb
                );
            """,
        )

        cube = cubes.CUBES['ChangeSystemInfo'](
            web_context,
            task_data('ChangeSystemInfo'),
            {
                'service_id': 1,
                'branch_id': 1,
                'environment': 'stable',
                'subsystems_info': {
                    'service_info': {
                        'duty_group_id': {
                            'old': duty_group['change_old'],
                            'new': duty_group['change_new'],
                        },
                    },
                },
            },
            [],
            conn,
        )
        await cube.update()

        params = await _get_remote_value(web_context, 1, 1, 'service_info')
        remote_values = json.loads(params.get('remote_values', {}))
        assert remote_values.get('duty_group_id') == duty_group['result']


async def _get_remote_value(
        web_context, service_id, branch_id, subsystem_name,
):
    async with postgres.primary_connect(web_context) as conn:
        row = await conn.fetchrow(
            """
            select
                subsystem_name,
                service_id,
                branch_id,
                remote_values
            from
                clownductor.parameters
            where
                service_id = $1 and
                branch_id = $2 and
                subsystem_name = $3;
            """,
            service_id,
            branch_id,
            subsystem_name,
        )
        return row


async def _get_parameters(web_context, service_id):
    async with postgres.primary_connect(web_context) as conn:
        rows = await conn.fetch(
            """
            select
                p.subsystem_name,
                p.service_id,
                p.branch_id,
                p.service_values,
                b.env
            from
                clownductor.parameters p
                left join clownductor.branches b
                    on p.branch_id = b.id
            where
                p.service_id = $1;
            """,
            service_id,
        )

        config = {}
        for row in rows:
            row = dict(row)
            subsystem = config.setdefault(row['subsystem_name'], {})
            env = 'general' if not row['env'] else row['env']
            subsystem[env] = json.loads(row['service_values'])
    return config


@pytest.mark.features_on('use_remote_clownductor_project')
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.parametrize(
    'service_id, branch_id, project_exp',
    [(1, 1, 'taxi'), (3, 9, 'taxi'), (1, 2, None)],
)
async def test_update_project_for_remote_values(
        web_context, service_id, branch_id, project_exp,
):
    async with postgres.get_connection(web_context) as conn:
        cube = cubes.CUBES['UpdateProjectInRemoteValues'](
            web_context,
            task_data('UpdateProjectInRemoteValues'),
            {'service_id': service_id, 'branch_id': branch_id},
            [],
            conn,
        )
        await cube.update()
        assert cube.success

        remote_config = (
            await web_context.service_manager.parameters.get_service_config(
                service_id, branch_id, conn=conn, is_remote=True,
            )
        )
    service_info = remote_config.service_info
    project_name = service_info.stable.clownductor_project
    assert project_name.value == project_exp
    assert project_name


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_start_change_abc_subsystem(
        web_context,
        get_job,
        abc_mockserver,
        get_job_variables,
        mock_task_processor,
):
    @mock_task_processor('/v1/jobs/start/')
    async def _handler(_):
        return web.json_response({'job_id': 1})

    abc_mockserver()
    meta_task_data = task_data('StartChangeAbcSubsystem')
    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['StartChangeAbcSubsystem'](
            web_context,
            meta_task_data,
            {
                'service_id': 1,
                'branch_id': 1,
                'environment': 'stable',
                'subsystems_info': {
                    'abc': {
                        'maintainers': {
                            'old': ['karachevda', 'test1'],
                            'new': ['test2', 'karachevda'],
                        },
                        'service_name': {
                            'old': {'ru': 'test', 'en': 'test'},
                            'new': {'ru': 'ok', 'en': 'ok'},
                        },
                        'description': {
                            'old': {'ru': '', 'en': ''},
                            'new': {'ru': '', 'en': ''},
                        },
                    },
                },
                'abc_slug': 'abc_service',
            },
            [],
            conn,
        )
        await cube.update()
    assert cube.success
    assert cube.data['payload'] == {
        'abc_job_id': 2,
        'tp_change_doc_id': 'ChangeAbcSubsystem_stable_clownductor',
        'st_comment': (
            'Starting job '
            '((/services/1/edit/1/jobs?jobId=2&isClownJob=true'
            ' ChangeAbcSubsystem))'
        ),
    }

    job = (await get_job(2))[0]['job']
    assert job.pop('created_at')
    assert job.pop('status')
    job.pop('finished_at', None)
    assert job == {
        'service_id': 1,
        'id': 2,
        'initiator': 'change-parameters',
        'name': 'ChangeAbcSubsystem',
        'change_doc_id': 'ChangeAbcSubsystem_stable_clownductor',
        'remote_job_id': 1,
        'idempotency_token': 'ChangeAbcSubsystem_stable_clownductor_123',
    }
    row = await get_job_variables(2)
    assert json.loads(row['variables']) == {
        'environment': 'stable',
        'branch_id': 1,
        'service_id': 1,
        'subsystem_name': 'abc',
        'new_parameters': {
            'maintainers': ['test2', 'karachevda'],
            'service_name': {'ru': 'ok', 'en': 'ok'},
            'description': {'ru': '', 'en': ''},
        },
        'team_members_to_delete': ['test1'],
        'new_team_members': ['test2'],
        'name': {'ru': 'ok', 'en': 'ok'},
        'service_slug': 'abc_service',
        'description': {'ru': '', 'en': ''},
    }


@pytest.mark.parametrize(
    'input_data, expected_variables',
    [
        (
            {
                'branch_id': 1,
                'initiator': 'deoevgen',
                'nanny_parameters': [{'name': 'cpu', 'value': 500}],
                'ticket': 'TICKET-1',
                'skip_closing_ticket': True,
            },
            {
                'branch_id': 1,
                'new_service_ticket': 'TICKET-1',
                'service_id': 1,
                'skip_closing_ticket': True,
                'subsystems_info': {
                    'nanny': {'cpu': {'new': 500, 'old': 1000}},
                },
            },
        ),
        (
            {
                'branch_id': 2,
                'initiator': 'deoevgen',
                'nanny_parameters': [
                    {'name': 'cpu', 'value': 222},
                    {'name': 'ram', 'value': 50},
                    {'name': 'root_size', 'value': 250},
                    {'name': 'work_dir', 'value': 4},
                    {'name': 'instances', 'value': 5},
                    {'name': 'datacenters_count', 'value': 50},
                ],
                'ticket': 'TICKET-1',
            },
            {
                'branch_id': 2,
                'new_service_ticket': 'TICKET-1',
                'service_id': 1,
                'skip_closing_ticket': False,
                'subsystems_info': {
                    'nanny': {
                        'cpu': {'new': 222, 'old': 14000},
                        'datacenters_count': {'new': 50, 'old': 2},
                        'ram': {'new': 50, 'old': 163840},
                        'instances': {'new': 5, 'old': 3},
                        'root_size': {'new': 250, 'old': 10240},
                        'work_dir': {'new': 4, 'old': 256},
                    },
                },
            },
        ),
    ],
)
@pytest.mark.pgsql('clownductor', files=['test_start_resolve_diff.sql'])
@pytest.mark.config(CLOWNDUCTOR_DIFF_PARAMETERS=DIFF_PARAMETERS)
async def test_start_resolve_diff(
        web_context,
        input_data,
        expected_variables,
        get_job,
        get_job_variables,
):
    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['StartResolveDiff'](
            web_context, task_data('StartResolveDiff'), input_data, [], conn,
        )
        await cube.update()
    assert cube.success
    assert cube.data['payload'] == {'resolve_job_id': 2}
    job = (await get_job(cube.data['payload']['resolve_job_id']))[0]['job']
    assert job.pop('created_at')
    job.pop('finished_at', None)
    assert job.pop('status')
    assert job == {
        'branch_id': input_data['branch_id'],
        'id': 2,
        'change_doc_id': f'1_{input_data["branch_id"]}_ResolveServiceDiff',
        'initiator': 'deoevgen',
        'name': 'ResolveServiceDiff',
        'service_id': 1,
        'idempotency_token': (
            f'1_{input_data["branch_id"]}_ResolveServiceDiff_123'
        ),
    }
    job_variables = await get_job_variables(
        cube.data['payload']['resolve_job_id'],
    )
    variables = json.loads(job_variables['variables'])
    assert variables == expected_variables


@pytest.mark.parametrize(
    (
        'service_yaml, expected_yaml, nanny_params, '
        'service_yaml_in_arcadia, success'
    ),
    [
        pytest.param(
            'full_preset_form_service.yaml',
            'expected_change_testing_in_full_preset_form_service.yaml',
            {
                'branch_id': 2,
                'nanny_parameters': [{'name': 'cpu', 'value': 1000}],
            },
            False,
            True,
        ),
        pytest.param(
            'full_preset_form_service_empty_dc.yaml',
            'expected_preset_from_with_empty_dc.yaml',
            {
                'branch_id': 2,
                'nanny_parameters': [{'name': 'cpu', 'value': 1000}],
            },
            False,
            True,
        ),
        pytest.param(
            'custom_preset_service.yaml',
            None,
            {
                'branch_id': 1,
                'nanny_parameters': [{'name': 'cpu', 'value': 1000}],
            },
            False,
            True,
            id='zero_diff_in_resources',
        ),
        pytest.param(
            'contracted_preset_form_service.yaml',
            'expected_change_prod_in_contracted_preset_form_service.yaml',
            {
                'branch_id': 1,
                'nanny_parameters': [{'name': 'cpu', 'value': 500}],
            },
            False,
            True,
        ),
        pytest.param(
            'contracted_preset_form_service.yaml',
            'expected_change_testing_in_contracted_preset_form_service.yaml',
            {
                'branch_id': 2,
                'nanny_parameters': [{'name': 'cpu', 'value': 500}],
            },
            False,
            True,
        ),
        pytest.param(
            'contracted_non_default_preset_service.yaml',
            'expected_default_preset_for_testing_service.yaml',
            {
                'branch_id': 10,
                'nanny_parameters': [{'name': 'cpu', 'value': 4000}],
            },
            False,
            True,
            id='unpack_full_form_with_correct_default_preset',
        ),
        pytest.param(
            'contracted_non_default_preset_service.yaml',
            'expected_default_preset_for_testing_without_unstable.yaml',
            {
                'branch_id': 11,
                'nanny_parameters': [{'name': 'cpu', 'value': 4000}],
            },
            True,
            True,
            id='unpack_full_form_testing_preset_without_unstable',
        ),
        pytest.param(
            'contracted_non_default_preset_service.yaml',
            (
                'expected_default_preset_for_testing_without_'
                'overrides_from_remote.yaml'
            ),
            {
                'branch_id': 2,
                'nanny_parameters': [{'name': 'cpu', 'value': 4000}],
            },
            False,
            True,
            id=(
                'unpack_full_form_with_default_preset_and_'
                'no_overrides_from_remote'
            ),
        ),
        pytest.param(
            'contracted_preset_form_service.yaml',
            '',
            {
                'branch_id': 2,
                'nanny_parameters': [{'name': 'instances', 'value': 15}],
            },
            False,
            False,
            id='fail_with_restricted-param-instances',
        ),
        pytest.param(
            'contracted_preset_form_service.yaml',
            '',
            {
                'branch_id': 2,
                'nanny_parameters': [
                    {'name': 'datacenters_count', 'value': 15},
                ],
            },
            False,
            False,
            id='fail_with_restricted-param-datacenters_count',
        ),
        pytest.param(
            'contracted_preset_form_service.yaml',
            'default_preset_form_service_taxi.yaml',
            {
                'branch_id': 1,
                'service_info_parameters': [
                    {'name': 'clownductor_project', 'value': 'taxi-devops'},
                ],
            },
            False,
            True,
            id='change_project',
        ),
        pytest.param(
            'full_preset_form_service.yaml',
            'expected_change_testing_in_full_preset_form_service.yaml',
            {
                'branch_id': 12,
                'nanny_parameters': [{'name': 'cpu', 'value': 1000}],
            },
            True,
            True,
            id='service_yaml_in_arcadia',
        ),
        pytest.param(
            'preset_service_with_aliases.yaml',
            'expected_preset_service_with_aliases.yaml',
            {
                'branch_id': 12,
                'nanny_parameters': [{'name': 'cpu', 'value': 1000}],
            },
            True,
            True,
            id='preset_service_with_aliases',
        ),
    ],
)
@pytest.mark.features_on('enable_ignore_datacenter_regions_null')
@pytest.mark.features_off('only_custom_envs_change_resources')
@pytest.mark.config(
    CLOWNDUCTOR_DIFF_CONFIGURATION={
        'services': ['clownductor', 'service_without_unstable'],
    },
    CLOWNDUCTOR_AVAILABLE_DATACENTERS={
        'all_datacenters': ['vla', 'man', 'sas', 'iva', 'myt'],
        'projects': [{'datacenters': ['vla', 'sas'], 'name': '__default__'}],
    },
)
@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
async def test_prepare_service_yaml(
        web_context,
        load,
        patch_arc_read_file,
        patch_github_single_file,
        service_yaml,
        expected_yaml,
        nanny_params,
        service_yaml_in_arcadia,
        success,
):
    if service_yaml_in_arcadia:
        read_file_mock = patch_arc_read_file(
            'taxi/backend-py3/services/clownductor/service.yaml', service_yaml,
        )
    else:
        read_file_mock = patch_github_single_file(
            'clownductor/service.yaml', service_yaml,
        )

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['PrepareServiceYaml'](
            web_context,
            task_data('PrepareServiceYaml'),
            nanny_params,
            [],
            conn,
        )
        await cube.update()

    assert cube.success == success, cube.error
    assert len(read_file_mock.calls) == (1 if success else 0)

    if success:
        expected_yaml_content = load(expected_yaml) if expected_yaml else None
        assert (
            expected_yaml_content
            == cube.data['payload']['content_service_yaml']
        )
