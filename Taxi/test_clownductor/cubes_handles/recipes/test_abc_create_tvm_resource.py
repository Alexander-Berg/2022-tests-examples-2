import pytest

from clownductor.internal.utils import task_processor as tp_module


@pytest.fixture(name='cube_caller')
def _cube_caller(taxi_clownductor_web):
    async def _wrapper(stage, cube, request_data):
        return await taxi_clownductor_web.post(
            f'/task-processor/v1/cubes/{cube.name}/', json=request_data,
        )

    return _wrapper


@pytest.fixture(name='external_call_cube')
def _external_call_cube(mockserver, mock_perforator_context):
    async def _wrapper(stage, cube, request_data):
        assert cube.name in ['ChangeOwnersCompletely', 'FindServiceForClown']
        response_data = {'status': 'success'}
        if cube.name == 'FindServiceForClown':
            clown_id = request_data['input_data']['clowny_service_id']
            services = [
                x
                for x in mock_perforator_context.services
                if x.clown_service.clown_id == clown_id
            ]
            if len(services) != 1:
                response_data['status'] = 'failed'
            else:
                response_data['payload'] = {'service_id': services[0].id}
        return mockserver.make_response(json=response_data)

    return _wrapper


@pytest.fixture(name='call_cube_externally')
def _call_cube_externally(taxi_clownductor_web):
    async def _wrapper(name, input_data):
        response = await taxi_clownductor_web.post(
            f'/task-processor/v1/cubes/{name}/',
            json={
                'job_id': 1,
                'task_id': 1,
                'status': 'in_progress',
                'retries': 0,
                'input_data': input_data,
            },
        )
        assert response.status == 200, await response.text()
        data = await response.json()
        assert data['status'] == 'success'
        return data['payload']

    return _wrapper


@pytest.fixture(name='call_meta_cube')
def _call_meta_cube(call_cube_externally):
    async def _wrapper(input_data):
        return await call_cube_externally(
            'MetaCubeAbcCreateTvmResource', input_data,
        )

    return _wrapper


@pytest.fixture(name='call_waiter_cube')
def _call_waiter_cube(call_cube_externally):
    async def _wrapper(job_id):
        return await call_cube_externally(
            'MetaCubeAbcWaitTvmResource', {'job_id': job_id},
        )

    return _wrapper


@pytest.fixture(name='perforator_mocks')
def _perforator_mocks(perforator_mockserver, mock_perforator_context):
    # just for more convenient test, we will retrieve some uniq id
    mock_perforator_context.add_service(
        'extra-mock', clown_id=100500, project_id=100500,
    )
    mock_perforator_context.add_service('some', clown_id=1, project_id=1)


@pytest.fixture(name='job_mocks')
def _job_mocks(
        mockserver,
        mock_strongbox,
        add_project,
        tvm_info_mockserver,
        yav_mockserver,
        task_processor,
        add_external_cubes,
):
    tvm_created = False

    async def _wrapper():
        await add_project('prj-1')

        @mockserver.json_handler('/client-abc/v3/services/')
        def abc_get_services(request):
            results = []
            slug = request.query['slug']
            if slug == 'prj1srv1':
                results.append({'id': 1})
            if slug == 'marketservice':
                results.append({'id': 2})
            return {'next': None, 'previous': None, 'results': results}

        @mockserver.json_handler('/client-abc/v3/resources/consumers/')
        def abc_get_resources(request):
            results = []
            service = request.query['service']
            if service == '1':
                if tvm_created:
                    results.append(
                        {
                            'id': 1,
                            'resource': {
                                'external_id': '123456',
                                'type': {'id': 47},
                                'name': 'tvmprjsrvstable',
                            },
                            'state': 'granted',
                        },
                    )
            elif service == '2':
                if tvm_created:
                    results.append(
                        {
                            'id': 2,
                            'resource': {
                                'external_id': '123456',
                                'type': {'id': 47},
                                'name': 'marketslug',
                            },
                            'state': 'granted',
                        },
                    )
            else:
                return mockserver.make_response(
                    status=404,
                    json={
                        'error': {
                            'detail': 'Сервис не найден',
                            'code': 'not_found',
                            'message': {
                                'ru': (
                                    'Наши еноты ничего не нашли '
                                    'по вашему запросу'
                                ),
                                'en': (
                                    'Our raccoons could not find '
                                    'anything to satisfy your query'
                                ),
                            },
                            'title': {'ru': 'Не найдено', 'en': 'Not found'},
                        },
                    },
                )
            return {'next': None, 'previous': None, 'results': results}

        @mockserver.json_handler('/client-abc/v3/resources/request/')
        def abc_request_resources(request):
            nonlocal tvm_created
            tvm_created = True
            return {}

        tvm_info_mockserver()
        yav_mockserver_handler = yav_mockserver()

        @mock_strongbox('/v1/secrets/')
        def strongbox_secrets_handler(request):
            return {
                'name': 'TVM_SECRET',
                'yav_secret_uuid': 'strongbox-sec-XXX',
                'yav_version_uuid': 'strongbox-ver-XXX',
            }

        @mock_strongbox('/v1/secretes/yav/')
        def strongbox_secret_yav_handler(request):
            return {
                'yav_secret_uuid': 'strongbox-sec-XXX',
                'yav_version_uuid': 'strongbox-ver-XXX',
            }

        add_external_cubes()

        return {
            'strongbox_secrets_handler': strongbox_secrets_handler,
            'strongbox_secret_yav_handler': strongbox_secret_yav_handler,
            'abc_get_services': abc_get_services,
            'abc_get_resources': abc_get_resources,
            'abc_request_resources': abc_request_resources,
            'yav_mockserver': yav_mockserver_handler,
        }

    return _wrapper


@pytest.fixture(name='run_job')
def _run_job(load_yaml, task_processor, run_job_common, call_meta_cube):
    async def _wrapper(job, result_job_vars):
        await run_job_common(job)
        assert job.job_vars == result_job_vars
        return job

    return _wrapper


@pytest.fixture(name='init_services')
async def _init_services(mocks_for_service_creation, add_service):
    await add_service('prj-1', 'srv-1', abc_service='prj1srv1')


@pytest.mark.usefixtures(
    'mock_internal_tp', 'init_services', 'perforator_mocks',
)
@pytest.mark.features_on('check_existing_tvm')
async def test_recipe(
        load_yaml,
        task_processor,
        run_job_common,
        job_mocks,
        run_job,
        call_meta_cube,
        call_waiter_cube,
):

    mocks = await job_mocks()

    task_processor.load_recipe(
        load_yaml('recipes/AbcCreateTvmResource.yaml')['data'],
    )
    init_job_vars = {
        'service_id': 1,
        'env': 'production',
        'tvm_name': 'srv-1',
        'abc_slug': None,
    }
    response = await call_meta_cube(init_job_vars)
    job = task_processor.job(response['job_id'])
    job = await run_job(
        job=job,
        result_job_vars={
            'env': 'production',
            'service_id': 1,
            'project_name': 'prj-1',
            'service_name': 'srv-1',
            'abc_slug': 'prj1srv1',
            'tvm_name': 'srv-1',
            'override_tvm_id': None,
            'tvm_resource_name': 'TVM for prj-1/srv-1 - stable',
            'tvm_resource_slug': 'tvmprjsrvstable',
            'tvm_id': '123456',
            'tvm_secret_tmp_yav_id': 'sec-XXX',
            'strongbox_yav_id': 'strongbox-sec-XXX',
            'override_tvm_resource_name': None,
            'override_tvm_resource_slug': None,
            'new_secret_owners': None,
            'skip_db_record': False,
            'tvm_extra_robot': None,
            'perforator_service_id': 2,
        },
    )
    assert await call_waiter_cube(job.id) == {
        'tvm_id': '123456',
        'tmp_tvm_secret_yav_id': 'sec-XXX',
    }
    assert mocks['strongbox_secrets_handler'].times_called == 1
    assert mocks['strongbox_secret_yav_handler'].times_called == 0

    _check_mocks_oauth(mocks['abc_request_resources'], 'abc_oauth')
    _check_mocks_oauth(mocks['yav_mockserver'], 'yav-oauth', 2)


@pytest.mark.usefixtures(
    'mock_internal_tp', 'init_services', 'perforator_mocks',
)
@pytest.mark.features_on(
    'check_existing_tvm', 'abc_try_use_extra_robot', 'yav_try_use_extra_robot',
)
async def test_recipe_for_market_case(
        load_yaml,
        task_processor,
        web_context,
        run_job_common,
        job_mocks,
        run_job,
        call_waiter_cube,
):
    mocks = await job_mocks()

    task_processor.load_recipe(
        load_yaml('recipes/AbcCreateTvmResource.yaml')['data'],
    )
    job = await tp_module.create_job(
        context=web_context,
        initiator='automation',
        provider='clownductor',
        job_name='AbcCreateTvmResource',
        variables={
            'service_id': 1,
            'project_name': 'prj-1',
            'service_name': 'srv-1',
            'env': 'production',
            'abc_slug': 'marketservice',
            'tvm_name': 'srv-1',
            'override_tvm_id': None,
            'override_tvm_resource_slug': 'marketslug',
            'override_tvm_resource_name': 'market name',
            'new_secret_owners': ['robot-market'],
            'skip_db_record': True,
            'tvm_extra_robot': 'robot-market',
        },
        service_id=1,
        change_doc_id='change_doc_id',
        idempotency_token='idempotency_token',
    )

    job = task_processor.job(job.request.remote_job_id)
    job = await run_job(
        job=job,
        result_job_vars={
            'env': 'production',
            'service_id': 1,
            'project_name': 'prj-1',
            'service_name': 'srv-1',
            'abc_slug': 'marketservice',
            'tvm_name': 'srv-1',
            'override_tvm_id': None,
            'tvm_resource_name': 'market name',
            'tvm_resource_slug': 'marketslug',
            'tvm_id': '123456',
            'tvm_secret_tmp_yav_id': 'sec-XXX',
            'strongbox_yav_id': 'strongbox-sec-XXX',
            'override_tvm_resource_slug': 'marketslug',
            'override_tvm_resource_name': 'market name',
            'new_secret_owners': ['robot-market'],
            'skip_db_record': True,
            'tvm_extra_robot': 'robot-market',
            'perforator_service_id': 2,
        },
    )
    assert await call_waiter_cube(job.id) == {
        'tvm_id': '123456',
        'tmp_tvm_secret_yav_id': 'sec-XXX',
    }

    assert mocks['strongbox_secrets_handler'].times_called == 0
    assert mocks['strongbox_secret_yav_handler'].times_called == 1

    _check_mocks_oauth(mocks['abc_request_resources'], 'MARKET_OAUTH')
    _check_mocks_oauth(mocks['yav_mockserver'], 'MARKET_OAUTH', 2)


def _check_mocks_oauth(mock, expected_oauth, times_called=1):
    assert mock.times_called == times_called
    for _ in range(times_called):
        call = mock.next_call()
        assert (
            call['request'].headers['Authorization']
            == f'OAuth {expected_oauth}'
        )
