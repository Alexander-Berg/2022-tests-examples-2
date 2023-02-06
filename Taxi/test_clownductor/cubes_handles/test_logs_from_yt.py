import pytest


TANKER = {
    'LogbrokerConfigurationStartCube.logs_from_yt.configure_fail': {
        'ru': (
            'Не удалось убедиться, что все топики logbroker, '
            'в которые пишет ваш сервис, созданы и имеют корректные '
            'права на запись.\n\n'
            'ЭТО НЕ БЛОКЕР ВЫКАТКИ: ваш сервис поднимется.\n\n'
            'Однако, если с топиками действительно '
            'что-то не так, то push-client может не иметь возможности '
            'отправить данные, и ротация логов перестанет производиться, '
            'что может привести к заполнению диска. Если выкатка не срочная, '
            'обратитесь в чат поддержки: https://nda.ya.ru/t/ePhVLReX4jWesx\n'
            'Для справки: упал вызов ручки /v1/logbroker/configure, '
            'ошибка: {error}'
        ),
    },
    'LogbrokerConfigurationPollCube.logs_from_yt.configure_status_fail': {
        'ru': (
            'Тут тот же текст, что и выше, кроме справки.\n'
            'Для справки: упал вызов ручки /v1/logbroker/configure/status, '
            'ошибка: {error}'
        ),
    },
    'LogbrokerConfigurationPollCube.logbroker.operation_fail': {
        'ru': (
            'Тут тот же текст, что и выше, кроме справки.\n'
            'Для справки: упали операции конфигурации в logbroker, '
            'ошибка: {error}'
        ),
    },
}
pytestmark = [  # pylint: disable=invalid-name
    pytest.mark.translations(clownductor=TANKER),
]


@pytest.mark.parametrize(
    [
        'cube_params',
        'expected_response',
        'expected_configure_request',
        'configure_error',
        'expected_configure_times_called',
        'expected_st_request',
        'expected_st_times_called',
        'expected_stats',
    ],
    [
        pytest.param(
            'cube_params_start_simple.json',
            'expected_start_response_simple.json',
            'expected_configure_request_simple.json',
            False,
            1,
            None,
            0,
            [],
            id='happy path',
        ),
        pytest.param(
            'cube_params_start_simple.json',
            'expected_start_response_feature_disabled.json',
            None,
            False,
            0,
            None,
            0,
            [],
            marks=pytest.mark.config(
                CLOWNDUCTOR_FEATURES_PER_SERVICE={
                    '__default__': {'enable_logbroker_configuration': True},
                    'taxi-clients': {
                        '__default__': {},
                        'znedo': {'enable_logbroker_configuration': False},
                    },
                },
            ),
            id='feature disabled',
        ),
        pytest.param(
            'cube_params_start_no_lb_configuration.json',
            'expected_start_response_no_lb_configuration.json',
            None,
            False,
            0,
            None,
            0,
            [],
            id='no logbroker configuration in cube params',
        ),
        pytest.param(
            'cube_params_start_simple.json',
            'expected_start_response_no_lb_configuration.json',
            'expected_configure_request_simple.json',
            True,
            1,
            'expected_start_st_request_simple.json',
            1,
            [
                {
                    'value': 1,
                    'kind': 'IGAUGE',
                    'timestamp': None,
                    'labels': {
                        'task': 'LogbrokerConfigurationStartCube',
                        'sensor': 'tasks.nonblocking_fails',
                        'error_code': 'logs_from_yt.configure_fail',
                    },
                },
            ],
            id='logs-from-yt /v1/logbroker/configure returns 400',
        ),
        pytest.param(
            'cube_params_start_no_st_key.json',
            'expected_start_response_no_lb_configuration.json',
            'expected_configure_request_simple.json',
            True,
            1,
            None,
            0,
            [
                {
                    'value': 1,
                    'kind': 'IGAUGE',
                    'timestamp': None,
                    'labels': {
                        'task': 'LogbrokerConfigurationStartCube',
                        'sensor': 'tasks.nonblocking_fails',
                        'error_code': 'logs_from_yt.configure_fail',
                    },
                },
            ],
            id='logs-from-yt /v1/logbroker/configure returns 400, no st_key',
        ),
    ],
)
@pytest.mark.config(
    CLOWNDUCTOR_FEATURES_PER_SERVICE={
        '__default__': {'enable_logbroker_configuration': True},
    },
)
async def test_logbroker_configuration_start(
        web_app_client,
        web_app,
        patch,
        mockserver,
        load_json,
        cube_params,
        get_stats_by_label_values,
        expected_response,
        expected_configure_request,
        configure_error,
        expected_configure_times_called,
        expected_st_request,
        expected_st_times_called,
        expected_stats,
):
    @mockserver.json_handler('/logs-from-yt/v1/logbroker/configure')
    def _mock_configure(request):
        assert request.json == load_json(expected_configure_request)

        if configure_error:
            return mockserver.make_response(
                status=400, json={'code': 'code', 'message': 'message'},
            )

        return {'arbitrary': 'object'}

    @mockserver.json_handler('/startrek/issues/TAXIBACKEND-404/comments')
    def _mock_st(request):
        assert request.json == load_json(expected_st_request)

        return {}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(*args, **kwargs):
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself(*args, **kwargs):
        return {'login': 'login'}

    response = await web_app_client.post(
        '/task-processor/v1/cubes/LogbrokerConfigurationStart/',
        json={
            'input_data': load_json(cube_params),
            'job_id': 1,
            'retries': 0,
            'status': 'in_progress',
            'task_id': 1,
        },
    )
    assert response.status == 200
    assert await response.json() == load_json(expected_response)

    assert _mock_configure.times_called == expected_configure_times_called
    assert _mock_st.times_called == expected_st_times_called

    assert (
        get_stats_by_label_values(
            web_app['context'], {'task': 'LogbrokerConfigurationStartCube'},
        )
        == expected_stats
    )


@pytest.mark.parametrize(
    [
        'cube_params',
        'expected_response',
        'expected_configure_status_request',
        'configure_status_status',
        'configure_status_response',
        'expected_configure_status_times_called',
        'expected_st_request',
        'expected_st_times_called',
        'expected_stats',
    ],
    [
        pytest.param(
            'cube_params_poll_simple.json',
            'expected_poll_response_simple.json',
            'expected_configure_status_request_simple.json',
            200,
            'configure_status_response_simple.json',
            1,
            None,
            0,
            [],
            id='happy path',
        ),
        pytest.param(
            'cube_params_poll_no_lb_operations.json',
            'expected_poll_response_simple.json',
            None,
            None,
            None,
            0,
            None,
            0,
            [],
            id='no logbroker_operations',
        ),
        pytest.param(
            'cube_params_poll_simple.json',
            'expected_poll_response_simple.json',
            'expected_configure_status_request_simple.json',
            500,
            'configure_status_response_lfy_fail.json',
            3,
            'expected_poll_st_request_lfy_fail.json',
            1,
            [
                {
                    'value': 1,
                    'kind': 'IGAUGE',
                    'timestamp': None,
                    'labels': {
                        'task': 'LogbrokerConfigurationPollCube',
                        'sensor': 'tasks.nonblocking_fails',
                        'error_code': 'logs_from_yt.configure_status_fail',
                    },
                },
            ],
            id='logs-from-yt /v1/logbroker/configure returns 500',
        ),
        pytest.param(
            'cube_params_poll_no_st_key.json',
            'expected_poll_response_simple.json',
            'expected_configure_status_request_simple.json',
            500,
            'configure_status_response_lfy_fail.json',
            3,
            None,
            0,
            [
                {
                    'value': 1,
                    'kind': 'IGAUGE',
                    'timestamp': None,
                    'labels': {
                        'task': 'LogbrokerConfigurationPollCube',
                        'sensor': 'tasks.nonblocking_fails',
                        'error_code': 'logs_from_yt.configure_status_fail',
                    },
                },
            ],
            id='logs-from-yt /v1/logbroker/configure returns 500, no st_key',
        ),
        pytest.param(
            'cube_params_poll_simple.json',
            'expected_poll_response_not_ready.json',
            'expected_configure_status_request_simple.json',
            200,
            'configure_status_response_not_ready.json',
            1,
            None,
            0,
            [],
            id='logbroker async operation in progress, sleep',
        ),
        pytest.param(
            'cube_params_poll_simple.json',
            'expected_poll_response_simple.json',
            'expected_configure_status_request_simple.json',
            200,
            'configure_status_response_operation_failed.json',
            1,
            'expected_poll_st_request_operation_failed.json',
            1,
            [
                {
                    'value': 1,
                    'kind': 'IGAUGE',
                    'timestamp': None,
                    'labels': {
                        'task': 'LogbrokerConfigurationPollCube',
                        'sensor': 'tasks.nonblocking_fails',
                        'error_code': 'logbroker.operation_fail',
                    },
                },
            ],
            id='logbroker async operation failed',
        ),
        pytest.param(
            'cube_params_poll_no_st_key.json',
            'expected_poll_response_simple.json',
            'expected_configure_status_request_simple.json',
            200,
            'configure_status_response_operation_failed.json',
            1,
            None,
            0,
            [
                {
                    'value': 1,
                    'kind': 'IGAUGE',
                    'timestamp': None,
                    'labels': {
                        'task': 'LogbrokerConfigurationPollCube',
                        'sensor': 'tasks.nonblocking_fails',
                        'error_code': 'logbroker.operation_fail',
                    },
                },
            ],
            id='logbroker async operation failed, no st_key',
        ),
    ],
)
async def test_logbroker_configuration_poll(
        web_app_client,
        web_app,
        mockserver,
        patch,
        load_json,
        cube_params,
        get_stats_by_label_values,
        expected_response,
        expected_configure_status_request,
        configure_status_status,
        configure_status_response,
        expected_configure_status_times_called,
        expected_st_request,
        expected_st_times_called,
        expected_stats,
):
    @mockserver.json_handler('/logs-from-yt/v1/logbroker/configure/status')
    def _mock_configure_status(request):
        assert request.json == load_json(expected_configure_status_request)

        return mockserver.make_response(
            status=configure_status_status,
            json=load_json(configure_status_response),
        )

    @mockserver.json_handler('/startrek/issues/TAXIBACKEND-404/comments')
    def _mock_st(request):
        assert request.json == load_json(expected_st_request)

        return {}

    @patch('taxi.clients.startrack.StartrackAPIClient.get_comments')
    async def _get_comments(*args, **kwargs):
        return []

    @patch('taxi.clients.startrack.StartrackAPIClient.get_myself')
    async def _get_myself(*args, **kwargs):
        return {'login': 'login'}

    response = await web_app_client.post(
        '/task-processor/v1/cubes/LogbrokerConfigurationPoll/',
        json={
            'input_data': load_json(cube_params),
            'job_id': 1,
            'retries': 0,
            'status': 'in_progress',
            'task_id': 1,
        },
    )
    assert response.status == 200
    assert await response.json() == load_json(expected_response)

    assert (
        _mock_configure_status.times_called
        == expected_configure_status_times_called
    )
    assert _mock_st.times_called == expected_st_times_called

    assert (
        get_stats_by_label_values(
            web_app['context'], {'task': 'LogbrokerConfigurationPollCube'},
        )
        == expected_stats
    )


@pytest.mark.config(CLOWNDUCTOR_FEATURES={'use_infinite_retries': True})
@pytest.mark.parametrize(
    ['handle', 'cube', 'cube_params'],
    [
        (
            'LogbrokerConfigurationStart',
            'LogbrokerConfigurationStartCube',
            'cube_params_start_simple.json',
        ),
        (
            'LogbrokerConfigurationPoll',
            'LogbrokerConfigurationPollCube',
            'cube_params_poll_simple.json',
        ),
    ],
)
async def test_logbroker_configuration_retries_exceed(
        web_app_client,
        web_app,
        load_json,
        get_stats_by_label_values,
        handle,
        cube,
        cube_params,
):
    response = await web_app_client.post(
        f'/task-processor/v1/cubes/{handle}/',
        json={
            'input_data': load_json(cube_params),
            'job_id': 1,
            'retries': 666,
            'status': 'in_progress',
            'task_id': 1,
        },
    )
    assert response.status == 200
    response_json = await response.json()
    assert response_json['status'] == 'success'

    assert get_stats_by_label_values(web_app['context'], {'task': cube}) == [
        {
            'value': 1,
            'kind': 'IGAUGE',
            'timestamp': None,
            'labels': {
                'task': cube,
                'sensor': 'tasks.nonblocking_fails',
                'error_code': 'max_retries_exceed',
            },
        },
    ]
