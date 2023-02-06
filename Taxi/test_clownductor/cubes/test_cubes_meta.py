import json
from typing import List

import pytest

from clownductor.internal import parameters
from clownductor.internal import service_parameters
from clownductor.internal.service_yaml import models
from clownductor.internal.tasks import cubes
from clownductor.internal.utils import postgres

REPO_PY3 = 'https://github.yandex-team.ru/taxi/backend-py3'


def task_data(name='name'):
    return {
        'id': 123,
        'job_id': 456,
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


async def test_create_nanny(
        patch,
        web_context,
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert 'CreateNannyService'

    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    project = await add_project('taxi')
    project_id = project['id']
    service = await add_service('taxi', 'some-service')
    service_info = models.ServiceInfo()
    service_info.network_stable = '__STABLE__'
    service_info.network_testing = '_TESTING_'
    deploy_unit = models.ClownAlias(
        service_type='backendpy3',
        service_yaml_url=None,
        service_name='some-service',
        wiki_path=None,
        maintainers=[],
        service_info=service_info,
        tvm_name='aaa',
    )
    service_config = await parameters.parametrize_clown_alias(
        web_context, deploy_unit,
    )
    service_config_raw = service_parameters.service_config_serialize(
        service_config,
    )
    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateNannyService'](
            web_context,
            task_data(),
            {
                'project_id': project_id,
                'service_id': service['id'],
                'preset_name': 'x2nano',
                'new_service_ticket': 'TAXIADMIN-1',
                'user': 'ilyasov',
                'service_config': service_config_raw,
            },
            [],
            conn,
        )

        await cube.update()
        assert cube.success
    assert len(create_comment.calls) == 1


@pytest.mark.parametrize(
    'service_config_name, drive_types',
    [
        pytest.param('ssd_service_config', ['ssd'], id='sdd only'),
        pytest.param('hdd_service_config', ['hdd'], id='hdd only'),
        pytest.param(
            'hdd_ssd_service_config', ['ssd', 'hdd'], id='sdd and hdd',
        ),
    ],
)
async def test_create_nanny_drive_types(
        patch,
        web_context,
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_project,
        add_service,
        get_job_variables,
        load_json,
        service_config_name,
        drive_types,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(**kwargs):
        return {}

    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    project = await add_project('taxi')
    project_id = project['id']
    service = await add_service('taxi', 'some_service')
    service_config_raw = load_json(f'{service_config_name}.json')

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeCreateNannyService'](
            web_context,
            task_data(),
            {
                'project_id': project_id,
                'service_id': service['id'],
                'preset_name': 'x2nano',
                'new_service_ticket': 'TAXIADMIN-1',
                'user': 'ilyasov',
                'service_config': service_config_raw,
            },
            [],
            conn,
        )

        await cube.update()
        assert cube.success
    job = await get_job_variables(2)
    job_drive_types = json.loads(job['variables'])['drive_types']
    assert len(create_comment.calls) == 1
    assert set(job_drive_types) == set(drive_types)


def _balancers_access_config(**kwargs):
    return pytest.mark.config(
        CLOWNDUCTOR_BALANCERS_ACCESS_SETTINGS={
            '__default__': {
                'stable': [
                    '@srv_svc_vopstaxi@',
                    '@srv_svc_taxiinformationsecurity@',
                ],
                'testing': [
                    '@srv_svc_taxi_development@',
                    '@srv_svc_taxi_testing@',
                ],
            },
            **kwargs,
        },
    )


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'punch_network': True,
        'fqdn_from_service': True,
        'puncher_check_requests': True,
    },
    CLOWNDUCTOR_BALANCERS_ACCESS_SETTINGS={
        '__default__': {'stable': [], 'testing': ['_C_TAXI_DEV_USER_YP_']},
    },
)
@pytest.mark.parametrize(
    'env, expected_groups, puncher_entities, expected_puncher_called',
    [
        pytest.param(
            'stable',
            [
                '@srv_svc_vopstaxi@',
                '@srv_svc_taxiinformationsecurity@',
                '_STABLE_NET_',
            ],
            {},
            2,
            marks=_balancers_access_config(),
            id='stable-only_default_config',
        ),
        pytest.param(
            'testing',
            [
                '@srv_svc_vopstaxi@',
                '@srv_svc_taxiinformationsecurity@',
                '@srv_svc_taxi_development@',
                '@srv_svc_taxi_testing@',
                '_C_TAXI_DEV_USER_YP_',
                '_TEST_NET_',
            ],
            {},
            2,
            marks=_balancers_access_config(),
            id='testing-only_default_config',
        ),
        pytest.param(
            'testing',
            [
                'group1',
                'group2',
                '@srv_svc_taxi_development@',
                '@srv_svc_taxi_testing@',
                '_C_TAXI_DEV_USER_YP_',
                '_TEST_NET_',
            ],
            {},
            2,
            marks=_balancers_access_config(
                taxi={'stable': ['group1', 'group2']},
            ),
            id='testing-projects_settings_no_testing_specs',
        ),
        pytest.param(
            'testing',
            [
                'group1',
                'group2',
                't_group1',
                't_group2',
                '_C_TAXI_DEV_USER_YP_',
                '_TEST_NET_',
            ],
            {},
            2,
            marks=_balancers_access_config(
                taxi={
                    'stable': ['group1', 'group2'],
                    'testing': ['t_group1', 't_group2'],
                },
            ),
            id='testing-projects_settings_with_testing_specs',
        ),
        pytest.param(
            'testing',
            ['group1', 'group2', '_C_TAXI_DEV_USER_YP_', '_TEST_NET_'],
            {},
            2,
            marks=_balancers_access_config(
                __default__={'stable': ['group1', 'group2']},
            ),
            id='testing-default_with_no_testing_settings',
        ),
        pytest.param(
            'testing',
            ['t_group1', 't_group2', '_C_TAXI_DEV_USER_YP_', '_TEST_NET_'],
            {},
            2,
            marks=_balancers_access_config(
                __default__={'stable': ['group1', 'group2']},
                taxi={'stable': ['t_group1', 't_group2']},
            ),
            id='testing-default_and_exact_with_no_testing_settings',
        ),
        pytest.param(
            'stable',
            ['@srv_svc_vopstaxi@', '@srv_svc_taxiinformationsecurity@'],
            {'rules': {'_STABLE_NET_': 'response_rules.json'}},
            1,
            marks=_balancers_access_config(),
            id='stable-rule_exists',
        ),
        pytest.param(
            'stable',
            [
                '@srv_svc_vopstaxi@',
                '@srv_svc_taxiinformationsecurity@',
                '_STABLE_NET_',
            ],
            {'rules': {'@srv_svc_vopstaxi@': 'response_rules_mismatch.json'}},
            2,
            marks=_balancers_access_config(),
            id='stable-rule_exists_mismatch',
        ),
    ],
)
async def test_puncher(
        patch,
        web_context,
        l3mgr_mockserver,
        login_mockserver,
        puncher_mockserver,
        staff_mockserver,
        mock_clowny_balancer,
        add_service,
        add_project,
        add_branch,
        env,
        expected_groups,
        puncher_entities,
        puncher_context,
        expected_puncher_called,
        load_json,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert 'puncher.yandex-team.ru' in text

    @mock_clowny_balancer('/v1/entry-points/fqdn/search/')
    def _handler(request):
        return {'fqdns': ['aa']}

    puncher_mockserver()
    puncher_data = {
        type: {
            source: load_json(filename) for source, filename in values.items()
        }
        for type, values in puncher_entities.items()
    }
    puncher_context.set_data(puncher_data)
    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    await add_project('taxi')
    service = await add_service('taxi', 'some-service')
    await add_branch(
        {
            'service_id': service['id'],
            'env': env,
            'direct_link': 'some-service-link',
            'name': env,
        },
    )

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubePunchBalancers'](
            web_context,
            task_data(),
            {
                'service_id': service['id'],
                'needs_balancers': True,
                'new_service_ticket': 'TAXIADMIN-1',
                'environment': env,
            },
            [],
            conn,
        )

        await cube.update()
        assert cube.success

    assert len(create_comment.calls) == 1

    puncher_calls = puncher_context.requests_post_calls
    assert len(puncher_calls) == expected_puncher_called
    sources = set()
    for puncher_request in puncher_calls:
        request_sources = puncher_request.json['request']['sources']
        sources.update(request_sources)
    assert sources == set(expected_groups)


async def test_deploy_placeholders(
        patch,
        web_context,
        l3mgr_mockserver,
        login_mockserver,
        staff_mockserver,
        add_service,
        add_project,
        add_nanny_branch,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def create_comment(ticket, text):
        assert ticket == 'TAXIADMIN-1'
        assert 'MetaCubeDeployPlaceholders' in text

    l3mgr_mockserver()
    login_mockserver()
    staff_mockserver()
    await add_project('taxi')
    service = await add_service('taxi', 'some-service')
    await add_nanny_branch(
        service['id'], 'testing', direct_link='taxi-service-testing',
    )
    await add_nanny_branch(
        service['id'], 'stable', direct_link='taxi-service-stable',
    )

    async with postgres.primary_connect(web_context) as conn:
        cube = cubes.CUBES['MetaCubeDeployPlaceholders'](
            web_context,
            task_data(),
            {
                'project_id': 123,
                'service_id': service['id'],
                'new_service_ticket': 'TAXIADMIN-1',
            },
            [],
            conn,
        )

        await cube.update()
        assert cube.success
        assert len(cube.data['payload']['job_ids']) == 3

    assert len(create_comment.calls) == 1


@pytest.mark.pgsql('clownductor', files=['init_jobs.sql'])
@pytest.mark.parametrize('job_id, cube_is_success', [(1, True), (2, False)])
async def test_wait_for_job_common(
        mock_task_processor, mockserver, web_context, job_id, cube_is_success,
):
    @mock_task_processor('/v1/jobs/retrieve/')
    def _handler(request):
        if request.json['job_id'] == 1:
            return {
                'job_info': {
                    'id': 1,
                    'job_vars': {},
                    'name': 'aaa',
                    'recipe_id': 1,
                    'status': 'success',
                    'created_at': 1234,
                },
                'tasks': [],
            }
        return mockserver.make_response(status=404)

    async with postgres.get_connection(web_context) as conn:
        cube = cubes.CUBES['MetaCubeWaitForJobCommon'](
            web_context, task_data(), {'job_id': job_id}, [], conn,
        )
        await cube.update()

    assert cube.success is cube_is_success
    assert _handler.times_called == 1
    call = _handler.next_call()
    assert call['request'].json['job_id'] == job_id


@pytest.mark.pgsql('clownductor', files=['init_jobs.sql'])
@pytest.mark.parametrize(
    'job_ids, cube_is_success',
    [
        pytest.param([1, 2], True, id='all_ok'),
        pytest.param([2, 3], False, id='one_job_is_not_completed_yet'),
        pytest.param([3, 4], False, id='one_job_not_found'),
        pytest.param(1, True, id='single_job_id_ok'),
    ],
)
async def test_wait_for_jobs_common(
        mock_task_processor, mockserver, web_context, job_ids, cube_is_success,
):
    @mock_task_processor('/v1/jobs/')
    def _handler(request):
        jobs = []
        for job_id in request.json['job_ids']:
            if job_id in {1, 2}:
                jobs.append(
                    {
                        'job_info': {
                            'id': job_id,
                            'job_vars': {},
                            'name': 'aaa',
                            'recipe_id': 1,
                            'status': 'success',
                            'created_at': 1234,
                        },
                        'tasks': [],
                    },
                )
            if job_id == 3:
                jobs.append(
                    {
                        'job_info': {
                            'id': job_id,
                            'job_vars': {},
                            'name': 'aaa',
                            'recipe_id': 1,
                            'status': 'in_progress',
                            'created_at': 1234,
                        },
                        'tasks': [],
                    },
                )
        return {'jobs': jobs}

    async with postgres.get_connection(web_context) as conn:
        cube = cubes.CUBES['MetaCubeWaitForJobsCommon'](
            web_context, task_data(), {'job_ids': job_ids}, [], conn,
        )
        await cube.update()
    assert cube.success is cube_is_success
    assert _handler.times_called == 1

    calls = []
    while _handler.has_calls:
        calls.append(_handler.next_call())
    assert (
        calls[0]['request'].json['job_ids'] == job_ids
        if isinstance(job_ids, List)
        else [job_ids]
    )


@pytest.mark.features_on('on_change_service_yaml')
@pytest.mark.pgsql('clownductor', files=['init_jobs.sql'])
async def test_change_custom_parameters(
        mockserver,
        web_context,
        add_service,
        login_mockserver,
        staff_mockserver,
):
    login_mockserver()
    staff_mockserver()
    async with postgres.get_connection(web_context) as conn:
        cube = cubes.CUBES['MetaCubeStartChangeCustomParameters'](
            web_context,
            task_data(),
            {
                'service_id': 1,
                'ticket': 'ticket-0',
                'user': 'deoevgen',
                'service_yaml': {
                    'service_type': 'backendpy3',
                    'service_yaml_url': None,
                    'service_name': 'taxi-admin-data',
                    'wiki_path': 'https://wiki.yandex-team.ru/taxi/',
                    'maintainers': [],
                    'service_info': {
                        'name': None,
                        'clownductor_project': 'taxi',
                        'preset': {'name': 'x2nano'},
                        'design_review': (
                            'https://st.yandex-team.ru/TAXIPLATFORM-2'
                        ),
                    },
                    'tvm_name': None,
                },
            },
            [],
            conn,
        )
        await cube.update()
    assert cube.success
    assert cube.data['payload'] == {'job_id': 5}


@pytest.mark.pgsql('clownductor', files=['wait_all_jobs.sql'])
async def test_wait_all_jobs(
        mockserver,
        web_context,
        add_service,
        patch,
        st_get_myself,
        st_get_comments,
):
    @patch('taxi.clients.startrack.StartrackAPIClient.create_comment')
    async def _create_comment(ticket, text, **kwargs):
        assert ticket == 'TAXIADMIN-1'
        assert text == (
            'Джоба завершилась: '
            '((/services/1/edit/1/jobs?jobId=3&isClownJob=true cool_job))\n'
            'Джоба завершилась: '
            '((/services/1/edit/1/jobs?jobId=4&isClownJob=true cool_job))'
        )

    async with postgres.get_connection(web_context) as conn:
        cube_data = task_data()
        cube_data['payload'].update({'finished_jobs': [1, 2]})
        cube = cubes.CUBES['MetaCubeWaitForAllJobs'](
            web_context,
            cube_data,
            {'job_ids': [1, 2, 3, 4], 'ticket': 'TAXIADMIN-1'},
            [],
            conn,
        )
        await cube.update()
    assert cube.success
    assert cube.data['payload'] == {'finished_jobs': [1, 2, 3, 4]}
