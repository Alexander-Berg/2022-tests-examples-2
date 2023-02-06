import pytest


@pytest.fixture(name='call_cube_handle')
def _call_cube_handle(web_app_client):
    async def _wrapper(
            cube_name: str, request_data: dict, expected_data: dict,
    ):
        response = await web_app_client.post(
            f'/task-processor/v1/cubes/{cube_name}/', json=request_data,
        )
        assert response.status == 200, await response.text()
        content = await response.json()
        assert content == expected_data
        return response

    return _wrapper


@pytest.fixture(name='init_services')
async def _init_services(
        add_service,
        add_nanny_branch,
        make_empty_config,
        set_remote_params,
        add_granted_roles,
):
    # will do nothing with idm, cause no duty section at all
    service_1 = await add_service('taxi', 'service-1')
    await add_nanny_branch(
        service_1['id'], 'stable', direct_link='taxi_service-1_stable',
    )

    # will require new and revoke old roles, cause changing abc slug
    service_2 = await add_service('taxi', 'service-2')
    branch_2_id = await add_nanny_branch(
        service_2['id'], 'stable', direct_link='taxi_service-2_stable',
    )
    cfg = make_empty_config()
    cfg.service_info.stable.duty.value = {
        'abc_slug': 'some_abc',
        'primary_schedule': 'some_schedule',
    }
    await set_remote_params(service_2['id'], branch_2_id, cfg)
    await add_granted_roles(service_2['id'], 1)

    # will only revoke roles, cause new params has exclude_roots
    service_3 = await add_service('taxi', 'service-3')
    branch_3_id = await add_nanny_branch(
        service_3['id'], 'stable', direct_link='taxi_service-3_stable',
    )
    cfg = make_empty_config()
    cfg.service_info.stable.duty.value = {
        'abc_slug': 'some_abc',
        'primary_schedule': 'some_schedule',
    }
    await set_remote_params(service_3['id'], branch_3_id, cfg)


@pytest.fixture(name='mock_idm')
async def _mock_idm(mock_idm, get_last_granted_roles_idm_id):
    idm_requests = []
    idm_revokes = []

    last_idm_id = await get_last_granted_roles_idm_id()

    @mock_idm('/api/v1/batch/')
    def _batch_handler(request):
        def _body(id_):
            method: str = requests[0]['method']
            path: str = requests[0]['path']
            if method == 'DELETE':
                if path.startswith('/roles/'):
                    idm_revokes.append(int(path.split('/')[-2]))
                return ''
            if method == 'POST':
                if path == '/rolenodes/':
                    return None
                new_id = id_ + 1
                idm_requests.append(new_id)
                return {'id': new_id}
            raise RuntimeError(f'unknown method {method} for mock')

        requests = request.json
        return {
            'responses': [
                {
                    'id': x['id'],
                    'status_code': 204 if x['method'] == 'DELETE' else 200,
                    'body': _body(i),
                }
                for i, x in enumerate(requests, start=last_idm_id)
            ],
        }

    return {
        'handler': _batch_handler,
        'idm_requests': idm_requests,
        'idm_revokes': idm_revokes,
    }


@pytest.fixture(name='run_job')
def _run_job(load_yaml, task_processor, run_job_common, call_cube_handle):
    async def _wrapper(job_data):
        task_processor.load_recipe(
            load_yaml('recipes/ChangeServiceInfoSystem.yaml')['data'],
        )

        await call_cube_handle(
            'MetaCubeStartChangeServiceInfoSystem',
            job_data['request_data'],
            job_data['expected_data'],
        )

        job = task_processor.job(job_data['created_job_id'])
        await run_job_common(job)

        assert job.job_vars == job_data['resulting_job_vars']

    return _wrapper


@pytest.fixture(name='config_handler')
def _config_handler(mockserver):
    def _wrapper(job_data):
        @mockserver.json_handler(
            '/abk-configs/CLOWNY_ALERT_MANAGER_DUTY_GROUPS/',
        )
        def _handler(request):
            if request.method == 'GET':
                return {
                    'value': job_data.get('config_updates', {}).get(
                        'old_value',
                    ),
                }
            return {}

        return _handler

    return _wrapper


def _get_config_update_call(mock):
    while mock.has_calls:
        call = mock.next_call()
        if call['request'].method == 'POST':
            return call

    return None


@pytest.mark.usefixtures(
    'mocks_for_service_creation', 'mock_internal_tp', 'init_services',
)
@pytest.mark.features_on('enable_revoke_role_for_duty')
async def test_service_has_no_duty(
        load_yaml, run_job, mock_idm, config_handler,
):
    # service-1 has no duty at all
    job_data = load_yaml('case_1.yaml')
    configs_mock = config_handler(job_data)
    await run_job(job_data)
    assert not mock_idm['idm_requests']
    assert not mock_idm['idm_revokes']
    assert _get_config_update_call(configs_mock) is None


@pytest.mark.usefixtures(
    'mocks_for_service_creation', 'mock_internal_tp', 'init_services',
)
@pytest.mark.features_on('enable_revoke_role_for_duty')
async def test_change_duty(load_yaml, run_job, mock_idm, config_handler):
    # service-2 has duty and we change it
    job_data = load_yaml('case_2.yaml')
    configs_mock = config_handler(job_data)
    await run_job(job_data)
    assert mock_idm['idm_requests'] == job_data['idm_requests']
    assert mock_idm['idm_revokes'] == job_data['idm_revokes']
    assert _get_config_update_call(configs_mock) is None


@pytest.mark.usefixtures(
    'mocks_for_service_creation', 'mock_internal_tp', 'init_services',
)
@pytest.mark.features_on('enable_revoke_role_for_duty')
async def test_revokes_root_for_duty_excludes(
        load_yaml, run_job, mock_idm, config_handler,
):
    # service-2 has duty and only revokes
    job_data = load_yaml('case_3.yaml')
    configs_mock = config_handler(job_data)
    await run_job(job_data)
    assert mock_idm['idm_requests'] == job_data['idm_requests']
    assert mock_idm['idm_revokes'] == job_data['idm_revokes']
    assert _get_config_update_call(configs_mock) is None


@pytest.mark.usefixtures(
    'mocks_for_service_creation', 'mock_internal_tp', 'init_services',
)
@pytest.mark.features_on('enable_revoke_role_for_duty')
async def test_revokes_root_for_duty_excludes_no_db_saves(
        load_yaml, run_job, mock_idm, config_handler,
):
    # service-3 has duty but no revokes (no granted roles in db)
    job_data = load_yaml('case_4.yaml')
    configs_mock = config_handler(job_data)
    await run_job(job_data)
    assert mock_idm['idm_requests'] == job_data['idm_requests']
    assert mock_idm['idm_revokes'] == job_data['idm_revokes']
    assert _get_config_update_call(configs_mock) is None


@pytest.mark.usefixtures(
    'mocks_for_service_creation', 'mock_internal_tp', 'init_services',
)
@pytest.mark.features_on('enable_revoke_role_for_duty')
async def test_change_duty_group_id_to_duty(
        load_yaml, run_job, mock_idm, config_handler,
):
    # switch from duty_group_id to duty for service-1
    job_data = load_yaml('case_5.yaml')
    configs_mock = config_handler(job_data)
    await run_job(job_data)
    assert mock_idm['idm_requests'] == job_data['idm_requests']
    assert mock_idm['idm_revokes'] == job_data['idm_revokes']

    update_call = _get_config_update_call(configs_mock)
    assert update_call['request'].json == job_data['config_updates']


@pytest.mark.usefixtures(
    'mocks_for_service_creation', 'mock_internal_tp', 'init_services',
)
@pytest.mark.parametrize(
    'case_file',
    [
        pytest.param(
            'no-revokes-cases/case_1.yaml', id='no service_info subsystem',
        ),
        pytest.param('no-revokes-cases/case_2.yaml', id='no new duty changes'),
        pytest.param(
            'no-revokes-cases/case_3.yaml', id='no old, so no revokes',
        ),
    ],
)
async def test_no_subsystem_changes(
        load_yaml, run_job, mock_idm, config_handler, case_file,
):
    # service has already requested role and not revokes emitted
    job_data = load_yaml(case_file)
    configs_mock = config_handler(job_data)
    await run_job(job_data)

    assert not mock_idm['idm_requests']
    assert not mock_idm['idm_revokes']
    assert _get_config_update_call(configs_mock) is None
