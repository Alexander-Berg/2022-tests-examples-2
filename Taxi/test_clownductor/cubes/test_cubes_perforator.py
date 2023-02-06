import pytest

from clownductor.internal.tasks import cubes


def task_data(name):
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


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'perforator_enable_cubes': True})
@pytest.mark.parametrize(
    'existed_service,is_error,is_edit',
    [
        (None, False, False),
        (
            {
                'id': 1,
                'tvm_name': 'service-tvm-name',
                'environments': [],
                'clown_service': {'project_id': 1, 'clown_id': 1},
                'is_internal': True,
            },
            False,
            False,
        ),
        (
            {
                'id': 1,
                'tvm_name': 'service-tvm-name',
                'environments': [],
                'is_internal': True,
            },
            True,
            False,
        ),
        (
            {
                'id': 1,
                'tvm_name': 'service-tvm-name',
                'environments': [],
                'clown_service': {'project_id': 1, 'clown_id': 2},
                'is_internal': True,
            },
            True,
            False,
        ),
        pytest.param(
            {
                'id': 1,
                'tvm_name': 'service-tvm-name',
                'environments': [],
                'clown_service': {'project_id': 1, 'clown_id': 2},
                'is_internal': True,
            },
            False,
            True,
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES={
                    'perforator_enable_edit_services': True,
                    'perforator_enable_cubes': True,
                },
            ),
        ),
    ],
)
async def test_create_service(
        web_context, mockserver, existed_service, is_error, is_edit,
):
    @mockserver.json_handler('/clowny-perforator/v1.0/services/create')
    def create_handler(request):
        response = {
            'id': 1,
            'tvm_name': 'service-tvm-name',
            'environments': [],
            'clown_service': {'project_id': 1, 'clown_id': 1},
            'is_internal': True,
        }
        assert request.json.keys() == {'tvm_name', 'clown_service'}
        assert request.json['tvm_name'] == response['tvm_name']
        assert request.json['clown_service'] == response['clown_service']
        return response

    @mockserver.json_handler('/clowny-perforator/v1.0/services/edit')
    def edit_handler(request):
        response = {
            'id': 1,
            'tvm_name': 'service-tvm-name',
            'environments': [],
            'clown_service': {'project_id': 1, 'clown_id': 1},
            'is_internal': True,
        }
        assert request.json.keys() == {'service_id', 'clown_service'}
        assert request.json['service_id'] == response['id']
        assert request.json['clown_service'] == response['clown_service']
        return response

    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    def retrieve_handler(request):
        services = []
        if existed_service:
            services.append(existed_service)
        response = {'services': services}

        assert request.json.keys() == {'limit', 'tvm_names'}
        assert request.json['tvm_names'] == ['service-tvm-name']
        return response

    cube = cubes.CUBES['PerforatorCreateService'](
        web_context,
        task_data('PerforatorCreateService'),
        {'service_id': 1, 'tvm_name': 'service-tvm-name'},
        [],
        None,
    )

    await cube.update()
    assert retrieve_handler.times_called == 1, cube.error
    if existed_service:
        assert not create_handler.times_called
    else:
        assert create_handler.times_called == 1
    if is_edit:
        assert edit_handler.times_called == 1
    if is_error:
        assert cube.status == 'in_progress'
        assert cube.error
        assert cube.sleep_duration
    else:
        assert cube.success
        assert cube.payload == {'perforator_service_id': 1}


@pytest.mark.parametrize(
    'has_service,is_error,existed_env',
    [
        (True, False, None),
        (False, True, None),
        (True, False, {'id': 3, 'env_type': 'production', 'tvm_id': 1001}),
        (True, True, {'id': 3, 'env_type': 'production', 'tvm_id': 1002}),
    ],
)
@pytest.mark.config(CLOWNDUCTOR_FEATURES={'perforator_enable_cubes': True})
async def test_create_environment(
        web_context, mockserver, has_service, is_error, existed_env,
):
    @mockserver.json_handler(
        '/clowny-perforator/v1.0/services/environments/create',
    )
    def create_handler(request):
        response = {'id': 1, 'env_type': 'production', 'tvm_id': 1001}
        assert request.json.keys() == {'service_id', 'env_type', 'tvm_id'}
        assert request.json['service_id'] == 1
        assert request.json['env_type'] == response['env_type']
        assert request.json['tvm_id'] == response['tvm_id']
        return response

    @mockserver.json_handler('/clowny-perforator/v1.0/services')
    def get_handler(request):
        envs = [
            {'id': 1, 'env_type': 'unstable', 'tvm_id': 1000},
            {'id': 2, 'env_type': 'testing', 'tvm_id': 1000},
        ]
        if existed_env:
            envs.append(existed_env)
        response = {
            'id': 1,
            'tvm_name': 'service-tvm-name',
            'environments': envs,
            'clown_service': {'project_id': 1, 'clown_id': 1},
            'is_internal': True,
        }
        assert request.query['id'] == '1'
        if has_service:
            return response
        return mockserver.make_response(
            json={'code': 'code', 'message': 'message'}, status=404,
        )

    cube = cubes.CUBES['PerforatorCreateEnvironment'](
        web_context,
        task_data('PerforatorCreateEnvironment'),
        {'service_id': 1, 'tvm_id': 1001, 'env_type': 'production'},
        [],
        None,
    )

    await cube.update()

    assert get_handler.times_called == 1
    if existed_env or is_error:
        assert not create_handler.times_called
    else:
        assert create_handler.times_called == 1
    if is_error:
        assert cube.failed, cube.error
    else:
        assert cube.success
        assert cube.payload == {}


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'perforator_enable_cubes': True})
async def test_old_create_rules(web_context, mockserver):
    @mockserver.json_handler(
        '/clowny-perforator/v1.0/services/environments/rules/create',
    )
    def handler(request):
        response = {
            'status': 'succeeded',
            'created_rules': [
                {
                    'rule_id': 1,
                    'source': {
                        'id': 1,
                        'environment_id': 1,
                        'tvm_name': 'new-service',
                        'tvm_id': 1001,
                    },
                    'destination': {
                        'id': 2,
                        'environment_id': 2,
                        'tvm_name': 'statistics',
                        'tvm_id': 1002,
                    },
                    'env_type': 'production',
                },
            ],
        }
        assert request.json.keys() == {'source', 'env_type', 'destinations'}
        assert request.json['source'] == 'new-service'
        assert request.json['env_type'] == 'production'
        assert request.json['destinations'] == ['statistics']
        return response

    cube = cubes.CUBES['PerforatorEnsureDefaultTvmRules'](
        web_context,
        task_data('PerforatorEnsureDefaultTvmRules'),
        {'source_tvm_name': 'new-service', 'env_type': 'production'},
        [],
        None,
    )

    await cube.update()

    assert cube.success, cube.error
    assert handler.times_called == 1
    assert cube.payload == {}


@pytest.mark.config(
    CLOWNDUCTOR_FEATURES={
        'perforator_enable_cubes': True,
        'perforator_new_rules_handle': True,
    },
)
@pytest.mark.parametrize('env_type', ['testing', 'production'])
async def test_create_rules(web_context, mockserver, env_type):
    @mockserver.json_handler(
        '/clowny-perforator/v1.0/internal/services/rules/create',
    )
    def handler(request):
        created_rules = [
            {
                'rule_id': 1,
                'source': {
                    'id': 1,
                    'environment_id': 1,
                    'tvm_name': 'new-service',
                    'tvm_id': 1001,
                },
                'destination': {
                    'id': 2,
                    'environment_id': 2,
                    'tvm_name': 'statistics',
                    'tvm_id': 1002,
                },
                'env_type': env_type,
            },
        ]
        request_rules = [
            {'source': 'new-service', 'destination': 'statistics'},
        ]
        if env_type != 'production':
            request_rules.append(
                {'source': 'developers', 'destination': 'new-service'},
            )
            created_rules.append(
                {
                    'rule_id': 2,
                    'source': {
                        'id': 3,
                        'environment_id': 3,
                        'tvm_name': 'developers',
                        'tvm_id': 3003,
                    },
                    'destination': {
                        'id': 1,
                        'environment_id': 1,
                        'tvm_name': 'new-service',
                        'tvm_id': 1001,
                    },
                    'env_type': env_type,
                },
            )
        response = {'status': 'succeeded', 'created_rules': created_rules}
        assert request.json.keys() == {'rules', 'env_types'}
        assert request.json['rules'] == request_rules
        assert request.json['env_types'] == [env_type]
        return response

    cube = cubes.CUBES['PerforatorEnsureDefaultTvmRules'](
        web_context,
        task_data('PerforatorEnsureDefaultTvmRules'),
        {'source_tvm_name': 'new-service', 'env_type': env_type},
        [],
        None,
    )

    await cube.update()

    assert cube.success, cube.error
    assert handler.times_called == 1
    assert cube.payload == {}


EXISTING_TVM = 'existing-tvm'


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'check_existing_tvm': True})
@pytest.mark.parametrize(
    'env_type, tvm_name, override_tvm_id, expected_tvm_id',
    [
        ('testing', 'non-existing-tvm', '', ''),
        ('unstable', EXISTING_TVM, '', ''),
        ('production', EXISTING_TVM, '', '1234'),
        ('production', EXISTING_TVM, '111', '111'),
    ],
    ids=['no-tvm', 'no-env', 'ok', 'override'],
)
async def test_existing_tvm(
        web_context,
        mockserver,
        env_type,
        tvm_name,
        override_tvm_id,
        expected_tvm_id,
):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/clowny-perforator/v1.0/services/retrieve')
    def retrieve_handler(request):
        services = []
        _tvm_name = request.json.get('tvm_names')[0]
        if _tvm_name == EXISTING_TVM:
            services.append(
                {
                    'id': 1,
                    'is_internal': True,
                    'tvm_name': EXISTING_TVM,
                    'environments': [
                        {'id': 1, 'env_type': 'production', 'tvm_id': 1234},
                    ],
                },
            )
        return {'services': services}

    cube = cubes.CUBES['PerforatorCheckExistingTvm'](
        web_context,
        task_data('PerforatorCheckExistingTvm'),
        {
            'env_type': env_type,
            'tvm_name': tvm_name,
            'override_tvm_id': override_tvm_id,
        },
        [],
        None,
    )

    await cube.update()

    assert cube.success
    payload = cube.data['payload']
    assert payload['tvm_id'] == expected_tvm_id


ENVIRONMENTS = ['production', 'testing', 'unstable']


@pytest.mark.parametrize(
    'env_exists,service_id,environment_type',
    [
        pytest.param(False, None, None, id='empty arguments'),
        pytest.param(True, 1, 'production', id='existing env -- production'),
        pytest.param(
            True, 2, 'unstable', id='another existing env -- unstable',
        ),
        pytest.param(True, 1, 'testing', id='existing env -- testing'),
        pytest.param(
            False,
            6,
            'testing',
            id='non-existing service with correct env type',
        ),
        pytest.param(
            False, 1, 'Galois', id='existing service with incorrect env type',
        ),
        pytest.param(
            False,
            6,
            'Ramanujan',
            id='non-existing service with incorrect env type',
        ),
    ],
)
@pytest.mark.features_on('perforator_enable_environment_removal')
async def test_delete_perf_environment(
        web_context, mockserver, env_exists, service_id, environment_type,
):
    rules = []
    services = []
    for i in range(3):
        services.append(
            {
                'id': i,
                'tvm_name': f'service_tvm_name_{str(i)}',
                'environments': [
                    {'id': j + i * j, 'env_type': env_type, 'tvm_id': i}
                    for j, env_type in enumerate(ENVIRONMENTS)
                ],
                'clown_service': None,
                'is_internal': True,
            },
        )
    for source_service in services:
        for dest_service in services:
            for j, env_type in enumerate(ENVIRONMENTS):
                if source_service['id'] == 2 or dest_service['id'] == 2:
                    # No rules for service 2 to see how it works without rules
                    continue
                rules.append(
                    {
                        'rule_id': (
                            source_service['id'] * dest_service['id'] + j
                        ),
                        'env_type': env_type,
                        'source': {
                            'id': source_service['id'],
                            'tvm_name': source_service['tvm_name'],
                            'tvm_id': source_service['id'],
                            'clown_service': None,
                            'environment_id': j + source_service['id'] * j,
                        },
                        'destination': {
                            'id': dest_service['id'],
                            'tvm_name': dest_service['tvm_name'],
                            'tvm_id': dest_service['id'],
                            'clown_service': None,
                            'environment_id': j + dest_service['id'] * j,
                        },
                    },
                )
    true_number_of_deleted_rules = len(
        list(
            filter(
                lambda x: (
                    x['env_type'] == environment_type
                    and (
                        service_id
                        in (x['source']['id'], x['destination']['id'])
                    )
                ),
                rules,
            ),
        ),
    )
    number_of_rules = len(rules)

    @mockserver.json_handler('/clowny-perforator/v1.0/services/rules/retrieve')
    def retrieve_rules_handler(request):
        assert request.json.keys() in (
            {'source_tvm_name', 'limit'},
            {'destination_tvm_name', 'limit'},
        )
        if request.json.keys() == {'source_tvm_name', 'limit'}:
            return {
                'rules': list(
                    filter(
                        lambda x: x['source']['tvm_name']
                        == request.json['source_tvm_name'],
                        rules,
                    ),
                ),
            }
        return {
            'rules': list(
                filter(
                    lambda x: x['destination']['tvm_name']
                    == request.json['destination_tvm_name'],
                    rules,
                ),
            ),
        }

    @mockserver.json_handler('/clowny-perforator/v1.0/services')
    def get_service_handler(request):
        for i in services:
            if request.query['id'] == str(i['id']):
                return i
        return mockserver.make_response(
            json={'code': 'FAIL', 'message': 'invalid source_id'}, status=404,
        )

    def filter_generator(source, dest, env_type):
        def filter_func(x):
            if (
                    x['env_type'] == env_type
                    and x['source']['tvm_name'] == source
                    and x['destination']['tvm_name'] == dest
            ):
                return False
            return True

        return filter_func

    @mockserver.json_handler(
        '/clowny-perforator/v1.0/services/environments/rules/delete',
    )
    def delete_by_source_handler(request):
        nonlocal rules
        response = {'deleted_rules': [], 'status': 'succeeded'}
        assert request.json.keys() == {'source', 'env_type', 'destinations'}
        for i in request.json['destinations']:
            rules = list(
                filter(
                    filter_generator(
                        request.json['source'], i, request.json['env_type'],
                    ),
                    rules,
                ),
            )
        return response

    @mockserver.json_handler(
        '/clowny-perforator/v1.0/'
        'services/environments/rules/destination/delete',
    )
    def delete_by_destination_handler(request):
        nonlocal rules
        response = {'deleted_rules': [], 'status': 'succeeded'}
        assert request.json.keys() == {'sources', 'env_type', 'destination'}
        for i in request.json['sources']:
            rules = list(
                filter(
                    filter_generator(
                        i,
                        request.json['destination'],
                        request.json['env_type'],
                    ),
                    rules,
                ),
            )
        return response

    @mockserver.json_handler(
        '/clowny-perforator/v1.0/services/environments/delete',
    )
    def delete_env_handler(request):
        assert request.json.keys() == {'environment_id'}
        response = {}
        k = 0
        for i in services:
            for j in i['environments']:
                if (
                        j['env_type'] == environment_type
                        and i['id'] == service_id
                        and j['id'] == request.json['environment_id']
                ):
                    k += 1
        assert k == 1
        return response

    cube = cubes.CUBES['PerforatorDeleteEnvironment'](
        web_context,
        task_data('PerforatorDeleteEnvironment'),
        {'service_id': service_id, 'env_type': environment_type},
        [],
        None,
    )

    await cube.update()

    if service_id:
        assert get_service_handler.times_called == 1
    else:
        assert not get_service_handler.times_called

    if service_id and env_exists:
        assert retrieve_rules_handler.times_called == 2
        if not true_number_of_deleted_rules:
            assert not delete_by_source_handler.times_called
            assert not delete_by_destination_handler.times_called
        else:
            assert delete_by_source_handler.times_called == 1
            assert delete_by_destination_handler.times_called == 1
        assert delete_env_handler.times_called == 1
    else:
        assert not retrieve_rules_handler.times_called
        assert not delete_by_source_handler.times_called
        assert not delete_by_destination_handler.times_called
        assert not delete_env_handler.times_called

    assert len(rules) == number_of_rules - true_number_of_deleted_rules


@pytest.mark.pgsql('clownductor', files=['init_service.sql'])
@pytest.mark.features_on('perforator_enable_service_removal')
@pytest.mark.parametrize(
    'service_id',
    [
        pytest.param(None, id='empty arguments'),
        pytest.param(1, id='existing service'),
        pytest.param(2, id='non-existing service'),
    ],
)
async def test_delete_service(web_context, mockserver, service_id):
    @mockserver.json_handler('/clowny-perforator/v1.0/services/delete')
    def delete_handler(request):

        response = {
            'id': 1,
            'tvm_name': 'service-tvm-name',
            'environments': [],
            'clown_service': {'project_id': 1, 'clown_id': 1},
            'is_internal': True,
        }
        assert request.json.keys() == {'service_id'}
        assert request.json['service_id'] == response['id']
        return {}

    @mockserver.json_handler('/clowny-perforator/v1.0/services')
    def get_handler(request):

        response = {
            'id': 1,
            'tvm_name': 'service-tvm-name',
            'environments': [],
            'clown_service': {'project_id': 1, 'clown_id': 1},
            'is_internal': True,
        }
        if int(request.query['id']) == response['id']:
            return response
        return mockserver.make_response(
            json={'code': 'FAIL', 'message': 'invalid source_id'}, status=404,
        )

    cube = cubes.CUBES['PerforatorDeleteService'](
        web_context,
        task_data('PerforatorCreateService'),
        {'service_id': service_id},
        [],
        None,
    )

    await cube.update()

    if service_id:
        assert get_handler.times_called == 1
    else:
        assert not get_handler.times_called

    if service_id == 1:
        assert delete_handler.times_called == 1
    else:
        assert not delete_handler.times_called
