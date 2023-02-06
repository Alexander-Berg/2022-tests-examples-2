import pytest

from tests_vgw_ya_tel_adapter import consts


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_ROBOCHECK_SETTINGS={
        'enable_quarantine': True,
        'enable_turning_off_quarantine': True,
        'sleep_before_make_broken_forwardings': 100,
    },
)
@consts.mock_tvm_configs()
async def test_post_full_request(
        taxi_vgw_ya_tel_adapter,
        mock_ya_tel,
        mock_ya_tel_grpc,
        mockserver,
        taxi_vgw_ya_tel_adapter_monitor,
        load_json,
):
    await taxi_vgw_ya_tel_adapter.tests_control(reset_metrics=True)

    @mockserver.json_handler('/vgw-api/v1/forwardings/state')
    def _forwardings_state(request):
        assert request.json['filter']['redirection_phones'] == ['+79672763662']
        assert request.json['state'] == 'broken'
        return mockserver.make_response(status=200, json={})

    request = load_json('request.json')
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/juggler/event', json=request,
    )
    assert response.status_code == 200
    assert _forwardings_state.times_called == 1

    assert (
        await taxi_vgw_ya_tel_adapter_monitor.get_metric(
            metric_name='juggler_event_processing',
        )
        == {
            'not_successful_quarantine': {'1min': 0},
            'not_successful_turning_off_quarantine': {'1min': 0},
            'request_warn': {'1min': 0},
            'successful_quarantine': {'1min': 1},
            'successful_turning_off_quarantine': {'1min': 0},
        }
    )


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_ROBOCHECK_SETTINGS={
        'enable_quarantine': True,
        'enable_turning_off_quarantine': True,
        'sleep_before_make_broken_forwardings': 100,
        'accepted_host_names': [
            'robocheck_host_name_1',
            'robocheck_host_name_2',
        ],
    },
)
@consts.mock_tvm_configs()
async def test_post_many(
        taxi_vgw_ya_tel_adapter,
        mock_ya_tel,
        mock_ya_tel_grpc,
        mockserver,
        taxi_vgw_ya_tel_adapter_monitor,
):
    await taxi_vgw_ya_tel_adapter.tests_control(reset_metrics=True)

    expected_redirection_phones = {'+79672763662', '+79672763663'}

    @mockserver.json_handler('/vgw-api/v1/forwardings/state')
    def _forwardings_state(request):
        assert (
            request.json['filter']['redirection_phones'][0]
            in expected_redirection_phones
        )
        expected_redirection_phones.remove(
            request.json['filter']['redirection_phones'][0],
        )
        assert request.json['state'] == 'broken'
        return mockserver.make_response(status=200, json={})

    request = {
        'checks': [
            {
                'host_name': 'robocheck_host_name_1',
                'status': 'CRIT',
                'description': '+79672763662 some info',
            },
            {
                'host_name': 'robocheck_host_name_2',
                'status': 'CRIT',
                'description': '+79672763663 some info',
            },
        ],
    }
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/juggler/event', json=request,
    )
    assert response.status_code == 200
    assert _forwardings_state.times_called == 2

    assert (
        await taxi_vgw_ya_tel_adapter_monitor.get_metric(
            metric_name='juggler_event_processing',
        )
        == {
            'not_successful_quarantine': {'1min': 0},
            'not_successful_turning_off_quarantine': {'1min': 0},
            'request_warn': {'1min': 0},
            'successful_quarantine': {'1min': 2},
            'successful_turning_off_quarantine': {'1min': 0},
        }
    )


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_ROBOCHECK_SETTINGS={
        'enable_quarantine': True,
        'enable_turning_off_quarantine': True,
        'sleep_before_make_broken_forwardings': 100,
    },
)
@consts.mock_tvm_configs()
async def test_ingnore_warn(
        taxi_vgw_ya_tel_adapter,
        mock_ya_tel,
        mock_ya_tel_grpc,
        mockserver,
        taxi_vgw_ya_tel_adapter_monitor,
):
    await taxi_vgw_ya_tel_adapter.tests_control(reset_metrics=True)

    @mockserver.json_handler('/vgw-api/v1/forwardings/state')
    def _forwardings_state(request):
        assert (
            request.json['filter']['redirection_phones'][0] == '+79672763662'
        )

        assert request.json['state'] == 'broken'
        return mockserver.make_response(status=200, json={})

    request = {
        'checks': [
            {
                'host_name': 'robocheck',
                'status': 'CRIT',
                'description': '+79672763662 some info',
            },
            {
                'host_name': 'robocheck',
                'status': 'WARN',
                'description': '+79672763663 some info',
            },
        ],
    }
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/juggler/event', json=request,
    )
    assert response.status_code == 200
    assert _forwardings_state.times_called == 1

    assert (
        await taxi_vgw_ya_tel_adapter_monitor.get_metric(
            metric_name='juggler_event_processing',
        )
        == {
            'not_successful_quarantine': {'1min': 0},
            'not_successful_turning_off_quarantine': {'1min': 0},
            'request_warn': {'1min': 1},
            'successful_quarantine': {'1min': 1},
            'successful_turning_off_quarantine': {'1min': 0},
        }
    )


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@pytest.mark.config(
    VGW_YA_TEL_ADAPTER_ROBOCHECK_SETTINGS={
        'enable_quarantine': True,
        'enable_turning_off_quarantine': True,
        'sleep_before_make_broken_forwardings': 100,
    },
)
@consts.mock_tvm_configs()
async def test_post_activate(
        taxi_vgw_ya_tel_adapter,
        mock_ya_tel,
        mock_ya_tel_grpc,
        mockserver,
        taxi_vgw_ya_tel_adapter_monitor,
):
    await taxi_vgw_ya_tel_adapter.tests_control(reset_metrics=True)

    @mockserver.json_handler('/vgw-api/v1/forwardings/state')
    def _forwardings_state(request):
        assert False

    request = {
        'checks': [
            {
                'host_name': 'robocheck',
                'status': 'OK',
                'description': '+79672763662 some info',
            },
        ],
    }
    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/juggler/event', json=request,
    )
    assert response.status_code == 200
    assert _forwardings_state.times_called == 0

    assert (
        await taxi_vgw_ya_tel_adapter_monitor.get_metric(
            metric_name='juggler_event_processing',
        )
        == {
            'not_successful_quarantine': {'1min': 0},
            'not_successful_turning_off_quarantine': {'1min': 0},
            'request_warn': {'1min': 0},
            'successful_quarantine': {'1min': 0},
            'successful_turning_off_quarantine': {'1min': 1},
        }
    )


@pytest.mark.now('2021-06-17T12:12:12.121212+0000')
@consts.mock_tvm_configs()
@pytest.mark.parametrize(
    ['request_body', 'warn_stat'],
    [
        pytest.param(
            {
                'checks': [
                    {
                        'host_name': 'robocheck',
                        'status': 'CRIT',
                        'description': '+79672763662 some info',
                    },
                ],
            },
            0,
            id='turned off by config 1',
        ),
        pytest.param(
            {
                'checks': [
                    {
                        'host_name': 'robocheck',
                        'status': 'OK',
                        'description': '+79672763662 some info',
                    },
                ],
            },
            0,
            id='turned off by config 2',
        ),
        pytest.param(
            {
                'checks': [
                    {
                        'host_name': 'unknown',
                        'status': 'OK',
                        'description': '+79672763662 some info',
                    },
                ],
            },
            1,
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_ROBOCHECK_SETTINGS={
                    'enable_quarantine': True,
                    'enable_turning_off_quarantine': True,
                    'sleep_before_make_broken_forwardings': 100,
                },
            ),
            id='wrong host_name',
        ),
        pytest.param(
            {
                'checks': [
                    {
                        'host_name': 'robocheck',
                        'status': 'OK',
                        'description': (
                            'Forced OK by downtimes: (Automatic downtime '
                            'for the new check)'
                        ),
                    },
                ],
            },
            1,
            marks=pytest.mark.config(
                VGW_YA_TEL_ADAPTER_ROBOCHECK_SETTINGS={
                    'enable_quarantine': True,
                    'enable_turning_off_quarantine': True,
                    'sleep_before_make_broken_forwardings': 100,
                },
            ),
            id='wrong description',
        ),
    ],
)
async def test_do_nothing(
        taxi_vgw_ya_tel_adapter,
        mock_ya_tel,
        mock_ya_tel_grpc,
        mockserver,
        taxi_vgw_ya_tel_adapter_monitor,
        request_body,
        warn_stat,
):
    await taxi_vgw_ya_tel_adapter.tests_control(reset_metrics=True)

    @mockserver.json_handler('/vgw-api/v1/forwardings/state')
    def _forwardings_state(request):
        assert False

    response = await taxi_vgw_ya_tel_adapter.post(
        '/v1/juggler/event', json=request_body,
    )
    assert response.status_code == 200
    assert _forwardings_state.times_called == 0

    assert (
        await taxi_vgw_ya_tel_adapter_monitor.get_metric(
            metric_name='juggler_event_processing',
        )
        == {
            'not_successful_quarantine': {'1min': 0},
            'not_successful_turning_off_quarantine': {'1min': 0},
            'request_warn': {'1min': warn_stat},
            'successful_quarantine': {'1min': 0},
            'successful_turning_off_quarantine': {'1min': 0},
        }
    )
