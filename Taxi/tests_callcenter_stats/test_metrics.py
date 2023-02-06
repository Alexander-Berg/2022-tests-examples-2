import pytest


# This config is duplicated in global config 'config.json' to prevent
# flap of this test in case when update metrics job already finished and
# we need to wait 60 seconds for a new start
@pytest.mark.config(
    CALLCENTER_STATS_METRICS_UPDATE_INTERVAL=1,
    CALLCENTER_OPERATORS_PAUSE_TYPES=['break'],
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
                    'callcenter_stats',
                    files=[
                        'callcenter_stats_create_calls.sql',
                        'callcenter_stats_create_operators.sql',
                    ],
                ),
            ],
        ),
        pytest.param(
            'expected_no_offset_metrics.json',
            id='test no window offset',
            marks=[
                pytest.mark.now('2020-06-22T08:05:00.00Z'),
                pytest.mark.config(CALLCENTER_STATS_METRICS_WINDOW_OFFSET=0),
                pytest.mark.pgsql(
                    'callcenter_stats',
                    files=['callcenter_stats_create_calls_offset.sql'],
                ),
            ],
        ),
        pytest.param(
            'expected_5_offset_metrics.json',
            id='test 5 sec window offset',
            marks=[
                pytest.mark.now('2020-06-22T08:05:00.00Z'),
                pytest.mark.config(CALLCENTER_STATS_METRICS_WINDOW_OFFSET=5),
                pytest.mark.pgsql(
                    'callcenter_stats',
                    files=['callcenter_stats_create_calls_offset.sql'],
                ),
            ],
        ),
    ],
)
async def test_metrics(
        taxi_callcenter_stats,
        taxi_callcenter_stats_monitor,
        testpoint,
        load_json,
        expected_metrics,
):
    @testpoint('update-metrics-finished')
    def metric_update_finished(data):
        return

    await taxi_callcenter_stats.enable_testpoints()

    # Run DistLockedTask and wait when it finishes
    async with taxi_callcenter_stats.spawn_task('distlock/update-metrics'):
        await metric_update_finished.wait_call()

    # Check monitor answer
    response = await taxi_callcenter_stats_monitor.get('/')
    assert response.status_code == 200
    metrics = response.json()['callcenter']['business']
    assert metrics == load_json(expected_metrics)


@pytest.mark.now('2020-06-22T10:00:10.00Z')
@pytest.mark.config(
    CALLCENTER_STATS_METRICS_UPDATE_INTERVAL=1,
    CALLCENTER_METAQUEUES=[
        {'name': 'disp', 'allowed_clusters': ['1', '2'], 'number': '123'},
    ],
    CALLCENTER_OPERATORS_PAUSE_TYPES=['break'],
)
async def test_zero_metrics(
        taxi_callcenter_stats,
        taxi_callcenter_stats_monitor,
        testpoint,
        load_json,
        mockserver,
):
    @testpoint('queue-list-cache-finish')
    def queue_list_cache_finished(data):
        return

    @testpoint('update-metrics-finished')
    def metric_update_finished(data):
        return

    @mockserver.json_handler('/callcenter-queues/v1/queues/list')
    def _queues_list(request):
        return mockserver.make_response(
            status=200,
            json={
                'subclusters': ['1', '2'],
                'metaqueues': ['disp'],
                'queues': [
                    {
                        'metaqueue': 'disp',
                        'subclusters': [
                            {
                                'name': '1',
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_users_balancing': True,
                                'enabled': True,
                            },
                            {
                                'name': '2',
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_users_balancing': True,
                                'enabled': True,
                            },
                        ],
                    },
                ],
            },
        )

    await taxi_callcenter_stats.enable_testpoints()
    await queue_list_cache_finished.wait_call()
    await taxi_callcenter_stats.invalidate_caches()

    # Run DistLockedTask and wait when it finishes
    async with taxi_callcenter_stats.spawn_task('distlock/update-metrics'):
        await metric_update_finished.wait_call()

    # Check monitor answer
    response = await taxi_callcenter_stats_monitor.get('/')
    assert response.status_code == 200
    metrics = response.json()['callcenter']['business']
    assert metrics == load_json('expected_zero_metrics.json')
