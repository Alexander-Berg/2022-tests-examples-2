import pytest


async def test_simple(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        check_bulk_request,
):
    fill_pilorama_config('simple_pilorama_conf.json')
    fill_service_logs('simple_service.log')

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        check_bulk_request(request, 'expected_elastic_request_simple.jl')

        return load_json('elastic_response_simple.json')

    await taxi_pilorama.run_task('pilorama/restart')

    await _elastic_mock.wait_call()


@pytest.mark.config(
    PILORAMA_ELASTICSEARCH_CLUSTERS={
        'first_cluster': {
            'hosts': [{'$mockserver': '/elasticsearch/first/_bulk'}],
        },
        'second_cluster': {
            'hosts': [{'$mockserver': '/elasticsearch/second/_bulk'}],
        },
    },
    PILORAMA_OUTPUT_SETTINGS={
        'projects': {
            '777': {'my_output': {'elasticsearch_cluster': 'first_cluster'}},
        },
        'services': {},
    },
)
async def test_output_settings_cluster_reload(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        testpoint,
        taxi_config,
        check_bulk_request,
):
    fill_pilorama_config('simple_pilorama_conf.json')
    fill_service_logs('simple_service.log')

    # testpoint to fill environment variables as testsuite can't do it
    @testpoint('fill_clownductor_env_vars')
    def _aggregator_request_completed(data):
        pass

    await taxi_pilorama.enable_testpoints()

    # setting up two different handlers for elastic to check
    # if pilorama-output-settings periodic works
    @mockserver.json_handler('/elasticsearch/first/_bulk')
    def _elastic_first_mock(request):
        check_bulk_request(request, 'expected_elastic_request_simple.jl')

        return load_json('elastic_response_simple.json')

    @mockserver.json_handler('/elasticsearch/second/_bulk')
    def _elastic_second_mock(request):
        check_bulk_request(request, 'expected_elastic_request_simple.jl')

        return load_json('elastic_response_simple.json')

    # first pilorama run on initial config, set with pytest.mark.config
    await taxi_pilorama.run_task('pilorama/restart')
    await _elastic_first_mock.wait_call()

    # change elasticsearch_cluster and run pilorama-output-settings periodic
    taxi_config.set_values(
        {
            'PILORAMA_OUTPUT_SETTINGS': {
                'projects': {
                    '777': {
                        'my_output': {
                            'elasticsearch_cluster': 'second_cluster',
                        },
                    },
                },
                'services': {},
            },
        },
    )
    await taxi_pilorama.invalidate_caches()
    await taxi_pilorama.run_periodic_task('pilorama-output-settings')

    # syncdb is kept on pilorama-output-settings run, so need more logs
    fill_service_logs('simple_service.log')
    await _elastic_second_mock.wait_call()

    # checking if every elastic handler was called only once
    assert _elastic_first_mock.times_called == 0
    assert _elastic_second_mock.times_called == 0


@pytest.mark.config(
    PILORAMA_OUTPUT_SETTINGS={
        'projects': {
            '777': {
                'my_output': {
                    'elasticsearch_cluster': 'test_cluster',
                    'auth_profile': 'profile_01',
                },
            },
        },
        'services': {},
    },
    PILORAMA_ELASTICSEARCH_CLUSTERS={
        'test_cluster': {'hosts': [{'$mockserver': '/elasticsearch/_bulk'}]},
    },
)
async def test_output_settings_auth_profile_reload(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        testpoint,
        taxi_config,
):
    fill_pilorama_config('simple_pilorama_conf.json')
    fill_service_logs('simple_service.log')

    # testpoint to fill environment variables as testsuite can't do it
    @testpoint('fill_clownductor_env_vars')
    def _aggregator_request_completed(data):
        pass

    await taxi_pilorama.enable_testpoints()

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        assert request.headers['Authorization'] == 'Basic YWRtaW46cGFzc3dvcmQ='

        return load_json('elastic_response_simple.json')

    # first pilorama run on initial config, set with pytest.mark.config
    await taxi_pilorama.run_task('pilorama/restart')
    await _elastic_mock.wait_call()

    # change auth_profile and run pilorama-output-settings periodic
    taxi_config.set_values(
        {
            'PILORAMA_OUTPUT_SETTINGS': {
                'projects': {
                    '777': {
                        'my_output': {
                            'elasticsearch_cluster': 'test_cluster',
                            'auth_profile': 'profile_02',
                        },
                    },
                },
                'services': {},
            },
        },
    )
    await taxi_pilorama.invalidate_caches()

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        assert request.headers['Authorization'] == 'Basic cGFzc3dvcmQ6YWRtaW4='

        return load_json('elastic_response_simple.json')

    await taxi_pilorama.run_periodic_task('pilorama-output-settings')

    # syncdb is kept on pilorama-output-settings run, so need more logs
    fill_service_logs('simple_service.log')
    await _elastic_mock.wait_call()

    # checking if every elastic handler was called only once
    assert _elastic_mock.times_called == 0
    assert _elastic_mock.times_called == 0


@pytest.mark.config(
    PILORAMA_OUTPUT_SETTINGS={
        'projects': {'777': {'my_output': {'index': 'first-index-name'}}},
        'services': {},
    },
)
async def test_output_settings_index_reload(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        testpoint,
        taxi_config,
):
    fill_pilorama_config('simple_pilorama_conf.json')
    fill_service_logs('simple_service.log')

    # testpoint to fill environment variables as testsuite can't do it
    @testpoint('fill_clownductor_env_vars')
    def _aggregator_request_completed(data):
        pass

    await taxi_pilorama.enable_testpoints()

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        assert 'first-index-name' in str(request.get_data())
        assert 'second-index-name' not in str(request.get_data())

        return load_json('elastic_response_simple.json')

    # first pilorama run on initial config, set with pytest.mark.config
    await taxi_pilorama.run_task('pilorama/restart')
    await _elastic_mock.wait_call()

    # change auth_profile and run pilorama-output-settings periodic
    taxi_config.set_values(
        {
            'PILORAMA_OUTPUT_SETTINGS': {
                'projects': {
                    '777': {'my_output': {'index': 'second-index-name'}},
                },
                'services': {},
            },
        },
    )
    await taxi_pilorama.invalidate_caches()

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        assert 'first-index-name' not in str(request.get_data())
        assert 'second-index-name' in str(request.get_data())

        return load_json('elastic_response_simple.json')

    await taxi_pilorama.run_periodic_task('pilorama-output-settings')

    # syncdb is kept on pilorama-output-settings run, so need more logs
    fill_service_logs('simple_service.log')
    await _elastic_mock.wait_call()

    # checking if every elastic handler was called only once
    assert _elastic_mock.times_called == 0
    assert _elastic_mock.times_called == 0


@pytest.mark.config(
    PILORAMA_ELASTICSEARCH_CLUSTERS={
        'first_cluster': {
            'hosts': [{'$mockserver': '/elasticsearch/first/_bulk'}],
        },
        'second_cluster': {
            'hosts': [{'$mockserver': '/elasticsearch/second/_bulk'}],
        },
    },
)
@pytest.mark.parametrize(
    ['pilorama_conf', 'fill_clownductor_env_vars', 'elastic_endpoint'],
    [
        ('simple_pilorama_conf.json', False, '/elasticsearch/_bulk'),
        ('no_output_id_pilorama_conf.json', False, '/elasticsearch/_bulk'),
        ('simple_pilorama_conf.json', True, '/elasticsearch/_bulk'),
        pytest.param(
            'simple_pilorama_conf.json',
            False,
            '/elasticsearch/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'elasticsearch_cluster': 'first_cluster',
                            },
                        },
                    },
                    'services': {},
                },
            ),
        ),
        pytest.param(
            'no_output_id_pilorama_conf.json',
            True,
            '/elasticsearch/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'elasticsearch_cluster': 'first_cluster',
                            },
                        },
                    },
                    'services': {},
                },
            ),
        ),
        pytest.param(
            'simple_pilorama_conf.json',
            True,
            '/elasticsearch/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'elasticsearch_cluster': 'bad_cluster',
                            },
                        },
                    },
                    'services': {},
                },
            ),
        ),
        pytest.param(
            'simple_pilorama_conf.json',
            True,
            '/elasticsearch/first/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'elasticsearch_cluster': 'first_cluster',
                            },
                        },
                    },
                    'services': {},
                },
            ),
        ),
        pytest.param(
            'simple_pilorama_conf.json',
            True,
            '/elasticsearch/second/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'elasticsearch_cluster': 'first_cluster',
                            },
                        },
                    },
                    'services': {
                        '666': {
                            'my_output': {
                                'elasticsearch_cluster': 'second_cluster',
                            },
                        },
                    },
                },
            ),
        ),
        pytest.param(
            'simple_pilorama_conf.json',
            True,
            '/elasticsearch/second/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {},
                    'services': {
                        '666': {
                            'my_output': {
                                'elasticsearch_cluster': 'second_cluster',
                            },
                        },
                    },
                },
            ),
        ),
    ],
)
async def test_output_settings_configs(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        testpoint,
        check_bulk_request,
        pilorama_conf,
        fill_clownductor_env_vars,
        elastic_endpoint,
):
    fill_pilorama_config(pilorama_conf)
    fill_service_logs('simple_service.log')

    if fill_clownductor_env_vars:

        @testpoint('fill_clownductor_env_vars')
        def _aggregator_request_completed(data):
            pass

        await taxi_pilorama.enable_testpoints()

    @mockserver.json_handler(elastic_endpoint)
    def _elastic_mock(request):
        check_bulk_request(request, 'expected_elastic_request_simple.jl')

        return load_json('elastic_response_simple.json')

    await taxi_pilorama.run_task('pilorama/restart')
    await _elastic_mock.wait_call()


@pytest.mark.config(
    PILORAMA_OUTPUT_SETTINGS={
        'projects': {
            '777': {
                'my_output': {
                    'index': 'custom-%Y.%m.%d.%H',
                    'error_index': 'custom-error-%Y.%m.%d.%H',
                },
            },
        },
        'services': {},
    },
)
async def test_output_settings_indices(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        testpoint,
        check_bulk_request,
):
    fill_pilorama_config('simple_pilorama_conf.json')
    fill_service_logs('simple_service.log')

    @testpoint('fill_clownductor_env_vars')
    def _aggregator_request_completed(data):
        pass

    await taxi_pilorama.enable_testpoints()

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        if 'INFO' in request.get_data().decode('utf-8'):
            check_bulk_request(
                request, 'expected_elastic_request_custom_index.jl',
            )
            return load_json('elastic_response_custom_index.json')

        check_bulk_request(request, 'expected_elastic_request_error_index.jl')
        return load_json('elastic_response_error_index.json')

    await taxi_pilorama.run_task('pilorama/restart')

    for _ in range(2):
        await _elastic_mock.wait_call()


@pytest.mark.parametrize(
    'exp_auth_header_present, elastic_endpoint',
    [
        pytest.param(
            True,
            '/elasticsearch/test/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'auth_profile': 'profile_01',
                                'elasticsearch_cluster': 'test_cluster',
                            },
                        },
                    },
                    'services': {},
                },
                PILORAMA_ELASTICSEARCH_CLUSTERS={
                    'test_cluster': {
                        'hosts': [
                            {'$mockserver': '/elasticsearch/test/_bulk'},
                        ],
                    },
                },
            ),
            id='ok',
        ),
        pytest.param(
            False,
            '/elasticsearch/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'auth_profile': 'nonexistent',
                                'elasticsearch_cluster': 'test_cluster',
                            },
                        },
                    },
                    'services': {},
                },
                PILORAMA_ELASTICSEARCH_CLUSTERS={
                    'test_cluster': {
                        'hosts': [
                            {'$mockserver': '/elasticsearch/test/_bulk'},
                        ],
                    },
                },
            ),
            id='nonexistent profile',
        ),
        pytest.param(
            False,
            '/elasticsearch/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'auth_profile': 'profile_01',
                                'elasticsearch_cluster': 'test_cluster_',
                            },
                        },
                    },
                    'services': {},
                },
                PILORAMA_ELASTICSEARCH_CLUSTERS={
                    'test_cluster': {
                        'hosts': [
                            {'$mockserver': '/elasticsearch/test/_bulk'},
                        ],
                    },
                },
            ),
            id='nonexistent cluster',
        ),
        pytest.param(
            False,
            '/elasticsearch/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {'my_output': {'auth_profile': 'profile_01'}},
                    },
                    'services': {},
                },
                PILORAMA_ELASTICSEARCH_CLUSTERS={
                    'test_cluster': {
                        'hosts': [
                            {'$mockserver': '/elasticsearch/test/_bulk'},
                        ],
                    },
                },
            ),
            id='no cluster',
        ),
        pytest.param(
            False,
            '/elasticsearch/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'auth_profile': 'profile_01',
                                'elasticsearch_cluster': 'test_cluster',
                            },
                        },
                    },
                    'services': {},
                },
            ),
            id='no cluster in PILORAMA_ELASTICSEARCH_CLUSTERS',
        ),
        pytest.param(
            False,
            '/elasticsearch/test/_bulk',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    'projects': {
                        '777': {
                            'my_output': {
                                'elasticsearch_cluster': 'test_cluster',
                            },
                        },
                    },
                    'services': {},
                },
                PILORAMA_ELASTICSEARCH_CLUSTERS={
                    'test_cluster': {
                        'hosts': [
                            {'$mockserver': '/elasticsearch/test/_bulk'},
                        ],
                    },
                },
            ),
            id='no auth profile',
        ),
    ],
)
async def test_output_settings_auth(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        testpoint,
        exp_auth_header_present,
        elastic_endpoint,
):
    fill_pilorama_config('simple_pilorama_conf.json')
    fill_service_logs('simple_service.log')

    @testpoint('fill_clownductor_env_vars')
    def _aggregator_request_completed(data):
        pass

    await taxi_pilorama.enable_testpoints()

    @mockserver.json_handler(elastic_endpoint)
    def _elastic_mock(request):
        if exp_auth_header_present:
            assert (
                request.headers['Authorization']
                == 'Basic YWRtaW46cGFzc3dvcmQ='
            )
        else:
            assert 'Authorization' not in request.headers

        return load_json('elastic_response_simple.json')

    await taxi_pilorama.run_task('pilorama/restart')

    await _elastic_mock.wait_call()


@pytest.mark.now('2021-10-25T18:10:00+0000')
@pytest.mark.parametrize(
    'pilorama_conf, exp_elastic_request',
    [
        (
            'simple_pilorama_conf.json',
            'expected_elastic_request_wo_ignore_older.jl',
        ),
        (
            'ignore_older_pilorama_conf.json',
            'expected_elastic_request_ignore_older.jl',
        ),
    ],
)
async def test_filter_ignore_lines_older_than(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        check_bulk_request,
        pilorama_conf,
        exp_elastic_request,
):
    fill_pilorama_config(pilorama_conf)
    fill_service_logs('ignore_older.log')

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        check_bulk_request(request, exp_elastic_request)

        return load_json('elastic_response_simple.json')

    await taxi_pilorama.run_task('pilorama/restart')

    await _elastic_mock.wait_call()


@pytest.mark.parametrize(
    [
        'send_errors_only',
        'expected_elastic_times_called',
        'expected_error_index_times_called',
        'expected_full_index_times_called',
    ],
    [
        pytest.param(
            True,
            1,
            1,
            0,
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    '__default__': {
                        'my_output': {
                            'error_index': 'custom-error-%Y.%m.%d.%H',
                            'send_errors_only': True,
                        },
                    },
                    'projects': {},
                    'services': {},
                },
            ),
        ),
        pytest.param(
            False,
            2,
            1,
            1,
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    '__default__': {
                        'my_output': {
                            'error_index': 'custom-error-%Y.%m.%d.%H',
                            'send_errors_only': False,
                        },
                    },
                    'projects': {},
                    'services': {},
                },
            ),
        ),
        pytest.param(
            False,
            2,
            1,
            1,
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    '__default__': {
                        'my_output': {
                            'error_index': 'custom-error-%Y.%m.%d.%H',
                        },
                    },
                    'projects': {},
                    'services': {},
                },
            ),
        ),
    ],
)
async def test_send_errors_only(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        check_bulk_request,
        send_errors_only,
        expected_elastic_times_called,
        expected_error_index_times_called,
        expected_full_index_times_called,
):
    fill_pilorama_config('simple_pilorama_conf.json')
    fill_service_logs('simple_service.log')

    error_index_times_called = 0
    full_index_times_called = 0

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        nonlocal error_index_times_called
        nonlocal full_index_times_called

        if 'INFO' in request.get_data().decode('utf-8'):
            assert not send_errors_only

            full_index_times_called += 1
            check_bulk_request(request, 'expected_elastic_request_simple.jl')
            return load_json('elastic_response_simple.json')

        error_index_times_called += 1
        check_bulk_request(request, 'expected_elastic_request_error_index.jl')
        return load_json('elastic_response_error_index.json')

    await taxi_pilorama.run_task('pilorama/restart')

    # process the same log 2 times to make sure pilorama doesn't send info
    # messages on `send_errors_only: True`
    for _ in range(expected_elastic_times_called):
        await _elastic_mock.wait_call()

    fill_service_logs('simple_service.log')

    for _ in range(expected_elastic_times_called):
        await _elastic_mock.wait_call()

    assert error_index_times_called == 2 * expected_error_index_times_called
    assert full_index_times_called == 2 * expected_full_index_times_called


@pytest.mark.config(
    PILORAMA_OUTPUT_SETTINGS={
        '__default__': {'my_output': {'elasticsearch_cluster': 'my_cluster'}},
        'projects': {},
        'services': {},
    },
)
@pytest.mark.parametrize(
    ['pilorama_conf', 'expected_elastic_handler'],
    [
        pytest.param(
            'simple_pilorama_conf.json',
            '/elasticsearch/_bulk',
            id='sanity check, no overrides',
        ),
        pytest.param(
            'simple_pilorama_conf.json',
            '/elasticsearch/_second',
            marks=pytest.mark.config(
                PILORAMA_ELASTICSEARCH_CLUSTERS={
                    'my_cluster': {
                        'hosts': [
                            {'$mockserver': '/elasticsearch/_first'},
                            {'$mockserver': '/elasticsearch/_second'},
                        ],
                        'host_blacklist': ['_first'],
                    },
                },
            ),
            id='_first blacklisted, _second is called',
        ),
        pytest.param(
            'simple_pilorama_conf.json',
            '/elasticsearch/_first',
            marks=pytest.mark.config(
                PILORAMA_ELASTICSEARCH_CLUSTERS={
                    'my_cluster': {
                        'hosts': [
                            {'$mockserver': '/elasticsearch/_first'},
                            {'$mockserver': '/elasticsearch/_second'},
                        ],
                        'host_blacklist': ['_second'],
                    },
                },
            ),
            id='_second blacklisted, _first is called',
        ),
        pytest.param(
            'simple_pilorama_conf.json',
            '/elasticsearch/_first',
            marks=pytest.mark.config(
                PILORAMA_ELASTICSEARCH_CLUSTERS={
                    'my_cluster': {
                        'hosts': [{'$mockserver': '/elasticsearch/_first'}],
                        'host_blacklist': ['_first'],
                    },
                },
            ),
            id='all hosts blacklisted, host_blacklist is ignored',
        ),
    ],
)
async def test_host_blacklist(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        load_json,
        pilorama_conf,
        expected_elastic_handler,
):
    fill_pilorama_config(pilorama_conf)
    fill_service_logs('simple_service.log')

    @mockserver.json_handler(expected_elastic_handler)
    def _elastic_mock(request):
        return load_json('elastic_response_simple.json')

    await taxi_pilorama.run_task('pilorama/restart')

    await _elastic_mock.wait_call()


@pytest.mark.parametrize(
    ['pilorama_conf', 'expected_elastic_request'],
    [
        pytest.param(
            'error_index_pilorama_conf.json',
            'expected_elastic_request_ei_default.jl',
            id='sanity check, no overrides',
        ),
        pytest.param(
            'minimal_error_log_level_pilorama_conf.json',
            'expected_elastic_request_ei_warning.jl',
            id='minimal_error_log_level=warning in pilorama fs config',
        ),
        pytest.param(
            'error_index_pilorama_conf.json',
            'expected_elastic_request_ei_info.jl',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    '__default__': {
                        'my_output': {'minimal_error_log_level': 'info'},
                    },
                    'projects': {},
                    'services': {},
                },
            ),
            id='minimal_error_log_level=info in taxi config',
        ),
        pytest.param(
            'minimal_error_log_level_pilorama_conf.json',
            'expected_elastic_request_ei_info.jl',
            marks=pytest.mark.config(
                PILORAMA_OUTPUT_SETTINGS={
                    '__default__': {
                        'my_output': {'minimal_error_log_level': 'info'},
                    },
                    'projects': {},
                    'services': {},
                },
            ),
            id=(
                'minimal_error_log_level=info in taxi config & '
                'minimal_error_log_level=warning in pilorama fs config'
            ),
        ),
    ],
)
async def test_minimal_error_log_level(
        taxi_pilorama,
        fill_pilorama_config,
        fill_service_logs,
        mockserver,
        check_bulk_request,
        load_json,
        pilorama_conf,
        expected_elastic_request,
):
    fill_pilorama_config(pilorama_conf)
    fill_service_logs('different_levels_service.log')
    error_index_times_called = 0

    @mockserver.json_handler('/elasticsearch/_bulk')
    def _elastic_mock(request):
        nonlocal error_index_times_called
        payload = request.get_data().decode('utf-8')

        if 'errors-yandex-taxi' in payload:
            error_index_times_called += 1

            check_bulk_request(request, expected_elastic_request)

        return load_json('elastic_response_simple.json')

    await taxi_pilorama.run_task('pilorama/restart')

    for _ in range(2):
        await _elastic_mock.wait_call()

    assert error_index_times_called == 1
