import pytest


# This config is duplicated in global config 'config.json' to prevent
# flap of this test in case when update metrics job already finished and
# we need to wait 60 seconds for a new start
@pytest.mark.config(
    CALLCENTER_QUEUES_METRICS_UPDATE_INTERVAL=1,
    CALLCENTER_OPERATORS_PAUSE_TYPES=['paused'],
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
        '1': {
            'endpoint': 'QPROC-s1',
            'endpoint_count': 2,
            'endpoint_strategy': 'TOPDOWN',
            'timeout_sec': 300,
            'endpoint_strategy_option': 1,
        },
    },
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_',
)
@pytest.mark.parametrize(
    'expected_metrics',
    [
        pytest.param(
            'expected_metrics.json',
            id='test metrics',
            marks=[
                pytest.mark.now('2020-06-22T10:00:10.00Z'),
                pytest.mark.pgsql(
                    'callcenter_queues',
                    files=[
                        'callcenter_queues_create_calls.sql',
                        'callcenter_queues_create_operators.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'expected_no_offset_metrics.json',
            id='test no window offset',
            marks=[
                pytest.mark.now('2020-06-22T08:05:00.00Z'),
                pytest.mark.config(CALLCENTER_QUEUES_METRICS_WINDOW_OFFSET=0),
                pytest.mark.pgsql(
                    'callcenter_queues',
                    files=['callcenter_queues_create_calls_offset.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_5_offset_metrics.json',
            id='test 5 sec window offset',
            marks=[
                pytest.mark.now('2020-06-22T08:05:00.00Z'),
                pytest.mark.config(CALLCENTER_QUEUES_METRICS_WINDOW_OFFSET=5),
                pytest.mark.pgsql(
                    'callcenter_queues',
                    files=['callcenter_queues_create_calls_offset.sql'],
                ),
            ],
        ),
    ],
)
async def test_metrics(
        taxi_callcenter_queues,
        taxi_callcenter_queues_monitor,
        testpoint,
        load_json,
        expected_metrics,
):
    @testpoint('update-metrics-finished')
    def metric_update_finished(data):
        return

    await taxi_callcenter_queues.enable_testpoints()

    # Run DistLockedTask and wait when it finishes
    async with taxi_callcenter_queues.spawn_task('distlock/update-metrics'):
        await metric_update_finished.wait_call()

    # Check monitor answer
    response = await taxi_callcenter_queues_monitor.get('/')
    assert response.status_code == 200
    metrics = response.json()['callcenter']['business']
    assert metrics == load_json(expected_metrics)


@pytest.mark.now('2020-06-22T10:00:10.00Z')
@pytest.mark.config(
    CALLCENTER_QUEUES_METRICS_UPDATE_INTERVAL=1,
    CALLCENTER_METAQUEUES=[
        {'name': 'disp', 'allowed_clusters': ['1', '2'], 'number': '123'},
    ],
    CALLCENTER_OPERATORS_PAUSE_TYPES=['paused'],
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={
        '1': {
            'endpoint': 'QPROC-s1',
            'endpoint_count': 2,
            'endpoint_strategy': 'TOPDOWN',
            'timeout_sec': 300,
            'endpoint_strategy_option': 1,
        },
    },
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_',
)
async def test_zero_metrics(
        taxi_callcenter_queues,
        taxi_callcenter_queues_monitor,
        testpoint,
        load_json,
):
    @testpoint('update-metrics-finished')
    def metric_update_finished(data):
        return

    await taxi_callcenter_queues.enable_testpoints()

    # Run DistLockedTask and wait when it finishes
    async with taxi_callcenter_queues.spawn_task('distlock/update-metrics'):
        await metric_update_finished.wait_call()

    # Check monitor answer
    response = await taxi_callcenter_queues_monitor.get('/')
    assert response.status_code == 200
    metrics = response.json()['callcenter']['business']
    assert metrics == load_json('expected_zero_metrics.json')
