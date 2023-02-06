# pylint: disable=invalid-name
import json

import pytest


EXPECTED_CREATE_SERVICE_VARS: dict = {
    'database': None,
    'draft_ticket': 'TAXIADMIN-1234',
    'is_attach_draft_ticket': False,
    'is_uservices': False,
    'needs_balancers': True,
    'needs_unstable': False,
    'preset_name': 'x2nano',
    'preset_overrides': None,
    'project_id': 1,
    'service_id': 1,
    'service_yaml': {
        'debian_unit': None,
        'maintainers': [],
        'service_info': {
            'abc': None,
            'awacs_preset': None,
            'clownductor_project': 'taxi',
            'deploy_callback_url': None,
            'description': None,
            'design_review': 'https://st.yandex-team.ru/TAXIPLATFORM-2',
            'disk_profile': {
                'production': None,
                'testing': None,
                'unstable': None,
            },
            'reallocation_settings': None,
            'duty_group_id': None,
            'duty': None,
            'release_flow': None,
            'critical_class': None,
            'networks': None,
            'grafana': None,
            'robots': None,
            'responsible_managers': None,
            'has_balancers': True,
            'has_unstable': False,
            'name': None,
            'preset': {'production': {'name': 'x2nano'}},
            'units': None,
            'yt_log_replications': None,
        },
        'service_name': 'taxi-admin-data',
        'service_type': 'backendpy3',
        'service_yaml_url': None,
        'tvm_name': None,
        'wiki_path': (
            'https://wiki.yandex-team.ru/taxi/'
            'backend/architecture/taxi-admin-data/'
        ),
        'hostnames': None,
    },
    'skip_db': True,
    'stable_env': 'stable',
    'testing_env': 'testing',
    'user': 'ilyasov',
    'volumes': [{'path': '/cache', 'size': 10240, 'type': 'hdd'}],
}


async def test_meta_service_400_with_empty_body(
        web_app_client, add_project, login_mockserver,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']
    result = await web_app_client.post(
        f'/v1/requests/service/?project_id={project_id}', json={},
    )

    assert result.status == 400


@pytest.mark.features_on('deprecate_old_service_form')
async def test_meta_service_400_enable_block_form(
        web_app_client, add_project, login_mockserver,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']

    body = {
        'project_id': project_id,
        'service_name': 'taxi-admin-data',
        'preset': 'x2nano',
        'needs_unstable': False,
        'needs_balancers': True,
        'repo_path': 'https://github.yandex-team.ru/taxi/backend-py3',
        'wiki_path': (
            'https://wiki.yandex-team.ru/taxi/'
            'backend/architecture/taxi-admin-data/'
        ),
        'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
        'design_review_ticket': 'https://st.yandex-team.ru/TAXIPLATFORM-2',
    }

    result = await web_app_client.post(
        f'/v1/requests/service/',
        json=body,
        headers={
            'X-Yandex-Login': 'ilyasov',
            'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
        },
    )
    assert result.status == 400
    content = await result.json()
    assert (
        content['message'] == 'is not supported, you can use '
        'https://tariff-editor.taxi.yandex-team.ru/services'
    )


@pytest.mark.parametrize(
    'repo_path,expected_service_type',
    [
        ('https://github.yandex-team.ru/taxi/backend-py3', 'backendpy3'),
        (None, 'unknown_repo'),
    ],
)
@pytest.mark.features_off('deprecate_old_service_form')
async def test_meta_service(
        web_app_client,
        add_project,
        login_mockserver,
        get_job,
        get_job_variables,
        repo_path,
        expected_service_type,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']

    body = {
        'project_id': project_id,
        'service_name': 'taxi-admin-data',
        'preset': 'x2nano',
        'needs_unstable': False,
        'needs_balancers': True,
        'repo_path': repo_path,
        'wiki_path': (
            'https://wiki.yandex-team.ru/taxi/'
            'backend/architecture/taxi-admin-data/'
        ),
        'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
        'design_review_ticket': 'https://st.yandex-team.ru/TAXIPLATFORM-2',
    }

    result = await web_app_client.post(
        f'/v1/requests/service/',
        json=body,
        headers={
            'X-Yandex-Login': 'ilyasov',
            'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
        },
    )

    assert result.status == 200
    content = await result.json()
    assert content == {'job_id': 1}

    job = await get_job(content['job_id'])
    job_name = job[0]['job']['name']
    variables = await get_job_variables(content['job_id'])
    variables = json.loads(variables['variables'])

    expected = EXPECTED_CREATE_SERVICE_VARS.copy()
    expected['service_yaml']['service_type'] = expected_service_type
    for field in ['volumes', 'preset_overrides', 'preset_name']:
        del expected[field]
    assert job_name == 'CreateFullNannyService'
    assert variables == expected


@pytest.mark.features_off('deprecate_old_service_form')
async def test_meta_service_with_token_retry(
        web_app_client, add_project, login_mockserver,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']

    body = {
        'project_id': project_id,
        'service_name': 'taxi-admin-data',
        'preset': 'x2nano',
        'needs_unstable': False,
        'needs_balancers': True,
        'repo_path': 'https://github.yandex-team.ru/taxi/backend-py3',
        'wiki_path': (
            'https://wiki.yandex-team.ru/taxi/'
            'backend/architecture/taxi-admin-data/'
        ),
        'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
        'design_review_ticket': 'https://st.yandex-team.ru/TAXIPLATFORM-2',
    }

    for _ in range(2):
        result = await web_app_client.post(
            f'/v1/requests/service/',
            json=body,
            headers={
                'X-Yandex-Login': 'ilyasov',
                'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
                'X-YaTaxi-Draft-Id': 'TAXIADMIN-1234',
            },
        )

        assert result.status == 200


@pytest.mark.features_off('deprecate_old_service_form')
async def test_meta_service_retry_without_token(
        web_app_client, add_project, login_mockserver,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']

    body = {
        'project_id': project_id,
        'service_name': 'taxi-admin-data',
        'preset': 'x2nano',
        'needs_unstable': False,
        'needs_balancers': True,
        'repo_path': 'https://github.yandex-team.ru/taxi/backend-py3',
        'wiki_path': (
            'https://wiki.yandex-team.ru/taxi/'
            'backend/architecture/taxi-admin-data/'
        ),
        'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
        'design_review_ticket': 'https://st.yandex-team.ru/TAXIPLATFORM-2',
    }

    result = await web_app_client.post(
        f'/v1/requests/service/',
        json=body,
        headers={
            'X-Yandex-Login': 'ilyasov',
            'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
            'X-YaTaxi-Draft-Id': 'TAXIADMIN-1234',
        },
    )

    assert result.status == 200

    result = await web_app_client.post(
        f'/v1/requests/service/',
        json=body,
        headers={
            'X-Yandex-Login': 'ilyasov',
            'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
        },
    )

    assert result.status == 409


@pytest.mark.features_on('disk_profiles')
@pytest.mark.parametrize(
    'repo_path,code',
    [
        pytest.param(
            'https://github.yandex-team.ru/taxi/backend-py3',
            200,
            marks=[pytest.mark.features_off('deprecate_old_service_form')],
            id='github_link',
        ),
        pytest.param(
            'https://a.yandex-team.ru/review/1791719/files/1#file-0-68184751',
            200,
            marks=[pytest.mark.features_off('deprecate_old_service_form')],
            id='arcadia_link',
        ),
        pytest.param(
            'https://a.yandex-team.ru/review/1791719/files/1#file-0-68184751',
            400,
            marks=[pytest.mark.features_on('deprecate_old_service_form')],
            id='enable_block_service_form',
        ),
    ],
)
async def test_meta_service_validation(
        web_app_client, add_project, login_mockserver, repo_path, code,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']
    body = {
        'project_id': project_id,
        'service_name': 'taxi-admin-data',
        'preset': 'x2nano',
        'needs_unstable': False,
        'needs_balancers': True,
        'repo_path': repo_path,
        'wiki_path': (
            'https://wiki.yandex-team.ru/taxi/'
            'backend/architecture/taxi-admin-data/'
        ),
        'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
        'design_review_ticket': 'https://st.yandex-team.ru/TAXIPLATFORM-2',
        'volumes': [{'path': '/cache', 'type': 'hdd', 'size': 10240}],
    }

    result = await web_app_client.post(
        f'/v1/requests/service/validate/',
        json=body,
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == code
    result_json = await result.json()
    if code == 200:
        handler_data = result_json['data']
        meta = handler_data.pop('meta_data')
        assert meta == {
            'project_name': 'taxi',
            'preset': {
                'name': 'x2nano',
                'ram': 4,
                'cpu': 1,
                'stable_instances': 1,
                'datacenters_count': 2,
                'datacenters_regions': ['vla', 'man', 'sas'],
                'instances_count': 1,
                'root_size': 10,
                'work_dir': 0.25,
            },
            'disk_profile': {
                '/var/cache/yandex': {
                    'path': '/var/cache/yandex',
                    'size': 2048,
                    'type': 'hdd',
                    'bandwidth_limit_mb_per_sec': 2,
                    'bandwidth_guarantee_mb_per_sec': 1,
                },
                '/cores': {
                    'size': 10240,
                    'type': 'hdd',
                    'path': '/cores',
                    'bandwidth_limit_mb_per_sec': 2,
                    'bandwidth_guarantee_mb_per_sec': 1,
                },
                '/logs': {
                    'size': 50000,
                    'type': 'hdd',
                    'path': '/logs',
                    'bandwidth_limit_mb_per_sec': 2,
                    'bandwidth_guarantee_mb_per_sec': 1,
                },
            },
        }
        assert handler_data == body
    else:
        assert (
            result_json['message'] == 'is not supported, you can use '
            'https://tariff-editor.taxi.yandex-team.ru/services'
        )


@pytest.mark.features_off('deprecate_old_service_form')
async def test_validate_and_apply(
        web_app_client, add_project, login_mockserver,
):
    login_mockserver()
    project = await add_project('taxi')
    project_id = project['id']
    body = {
        'project_id': project_id,
        'service_name': 'taxi-admin-data',
        'preset': 'x2nano',
        'needs_unstable': False,
        'needs_balancers': True,
        'repo_path': 'https://github.yandex-team.ru/taxi/backend-py3',
        'wiki_path': (
            'https://wiki.yandex-team.ru/'
            'taxi/backend/architecture/taxi-admin-data/'
        ),
        'st_task': 'https://st.yandex-team.ru/TAXIPLATFORM-1',
        'design_review_ticket': 'https://st.yandex-team.ru/TAXIPLATFORM-2',
        'volumes': [{'path': '/cache', 'type': 'hdd', 'size': 10240}],
    }
    result = await web_app_client.post(
        f'/v1/requests/service/validate/',
        json=body,
        headers={'X-Yandex-Login': 'ilyasov'},
    )
    assert result.status == 200
    data = await result.json()

    result = await web_app_client.post(
        f'/v1/requests/service/',
        json=data['data'],
        headers={
            'X-Yandex-Login': 'ilyasov',
            'X-YaTaxi-Ticket': 'TAXIADMIN-1234',
        },
    )
    assert result.status == 200
