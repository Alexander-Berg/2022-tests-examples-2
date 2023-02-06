import pytest


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    return obj


@pytest.mark.now('2020-04-21T12:18:50.123456+0000')
@pytest.mark.pgsql(
    'callcenter_queues',
    files=['insert_calls.sql', 'insert_agents.sql', 'insert_system_info.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'metaqueues': ['ru_taxi_disp'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
        'support': {
            'metaqueues': ['ru_taxi_support'],
            'display_name': '',
            'should_use_internal_queue_service': True,
            'reg_groups': [],
        },
    },
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={},
    CALLCENTER_METAQUEUES=[],
    CALLCENTER_SUBCLUSTER_MAX_OPERATORS_AMOUNT=10,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
)
async def test_subclusters_statistics_handler(
        taxi_callcenter_queues, taxi_config, pgsql,
):
    await taxi_callcenter_queues.invalidate_caches()
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('SELECT * from callcenter_queues.tel_state')
    agents = cursor.fetchall()
    assert agents
    cursor.close()

    taxi_config.set_values(
        {
            'CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP': {
                '1': {
                    'endpoint': 'QPROC01',
                    'endpoint_count': 1,
                    'endpoint_strategy': 'TOPDOWN',
                    'endpoint_strategy_option': 1,
                    'timeout_sec': 180,
                },
                '2': {
                    'endpoint': 'QPROC01',
                    'endpoint_count': 1,
                    'endpoint_strategy': 'TOPDOWN',
                    'endpoint_strategy_option': 1,
                    'timeout_sec': 180,
                },
                '3': {
                    'endpoint': 'QPROC01',
                    'endpoint_count': 1,
                    'endpoint_strategy': 'TOPDOWN',
                    'endpoint_strategy_option': 1,
                    'timeout_sec': 180,
                },
            },
            'CALLCENTER_METAQUEUES': [
                {
                    'allowed_clusters': ['1', '2', '3'],
                    'name': 'ru_taxi_disp',
                    'number': '840100',
                },
                {
                    'allowed_clusters': ['1', '2'],
                    'name': 'ru_taxi_support',
                    'number': '840100',
                },
                {
                    'allowed_clusters': ['1'],
                    'name': 'ru_taxi_econom',
                    'number': '840100',
                },
            ],
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/statistics', json={},
    )
    assert response.status == 200
    result = response.json()
    print(result)

    assert _ordered(result) == _ordered(
        {
            'subclusters_statistics': [
                {
                    'name': '1',
                    'stats': {'total': 5, 'connected': 3, 'paused': 2},
                },
                {
                    'name': '2',
                    'stats': {'total': 2, 'connected': 1, 'paused': 1},
                },
                {
                    'name': '3',
                    'stats': {'total': 1, 'connected': 1, 'paused': 0},
                },
            ],
            'metaqueues_statistics': [
                {
                    'name': 'ru_taxi_support',
                    'stats': {'total': 4, 'connected': 2, 'paused': 2},
                },
                {
                    'name': 'ru_taxi_econom',
                    'stats': {'total': 2, 'connected': 1, 'paused': 1},
                },
                {
                    'name': 'ru_taxi_disp',
                    'stats': {'total': 4, 'connected': 3, 'paused': 1},
                },
            ],
            'queues_statistics': [
                {
                    'metaqueue': 'ru_taxi_disp',
                    'subclusters': [
                        {
                            'subcluster': '1',
                            'operators_stats': {
                                'total': 2,
                                'connected': 1,
                                'paused': 1,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:17:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 1,
                                'calls_now_in_queue_max_wait_time_sec': 60.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                        {
                            'subcluster': '2',
                            'operators_stats': {
                                'total': 1,
                                'connected': 1,
                                'paused': 0,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:17:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 1,
                                'calls_now_in_queue_max_wait_time_sec': 60.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                        {
                            'subcluster': '3',
                            'operators_stats': {
                                'total': 1,
                                'connected': 1,
                                'paused': 0,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:17:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 2,
                                'calls_now_in_queue_max_wait_time_sec': 60.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                    ],
                },
                {
                    'metaqueue': 'ru_taxi_econom',
                    'subclusters': [
                        {
                            'subcluster': '1',
                            'operators_stats': {
                                'total': 2,
                                'connected': 1,
                                'paused': 1,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:18:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 0,
                                'calls_now_in_queue_max_wait_time_sec': 0.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                    ],
                },
                {
                    'metaqueue': 'ru_taxi_support',
                    'subclusters': [
                        {
                            'subcluster': '1',
                            'operators_stats': {
                                'total': 2,
                                'connected': 1,
                                'paused': 1,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:18:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 0,
                                'calls_now_in_queue_max_wait_time_sec': 0.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                        {
                            'subcluster': '2',
                            'operators_stats': {
                                'total': 2,
                                'connected': 1,
                                'paused': 1,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:18:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 0,
                                'calls_now_in_queue_max_wait_time_sec': 0.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                    ],
                },
            ],
        },
    )

    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/statistics',
        json={'metaqueues': ['ru_taxi_disp']},
    )
    assert response.status == 200
    result = response.json()
    print(result)
    assert _ordered(result) == _ordered(
        {
            'subclusters_statistics': [
                {
                    'name': '1',
                    'stats': {'total': 5, 'connected': 3, 'paused': 2},
                },
                {
                    'name': '2',
                    'stats': {'total': 2, 'connected': 1, 'paused': 1},
                },
                {
                    'name': '3',
                    'stats': {'total': 1, 'connected': 1, 'paused': 0},
                },
            ],
            'metaqueues_statistics': [
                {
                    'name': 'ru_taxi_disp',
                    'stats': {'total': 4, 'connected': 3, 'paused': 1},
                },
            ],
            'queues_statistics': [
                {
                    'metaqueue': 'ru_taxi_disp',
                    'subclusters': [
                        {
                            'subcluster': '1',
                            'operators_stats': {
                                'total': 2,
                                'connected': 1,
                                'paused': 1,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:17:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 1,
                                'calls_now_in_queue_max_wait_time_sec': 60.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                        {
                            'subcluster': '2',
                            'operators_stats': {
                                'total': 1,
                                'connected': 1,
                                'paused': 0,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:17:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 1,
                                'calls_now_in_queue_max_wait_time_sec': 60.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                        {
                            'subcluster': '3',
                            'operators_stats': {
                                'total': 1,
                                'connected': 1,
                                'paused': 0,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:17:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 2,
                                'calls_now_in_queue_max_wait_time_sec': 60.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                    ],
                },
            ],
        },
    )

    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/statistics',
        json={'metaqueues': ['ru_taxi_disp'], 'subclusters': ['2']},
    )
    assert response.status == 200
    result = response.json()
    print(result)
    assert _ordered(result) == _ordered(
        {
            'subclusters_statistics': [
                {
                    'name': '2',
                    'stats': {'total': 2, 'connected': 1, 'paused': 1},
                },
            ],
            'metaqueues_statistics': [
                {
                    'name': 'ru_taxi_disp',
                    'stats': {'total': 4, 'connected': 3, 'paused': 1},
                },
            ],
            'queues_statistics': [
                {
                    'metaqueue': 'ru_taxi_disp',
                    'subclusters': [
                        {
                            'subcluster': '2',
                            'operators_stats': {
                                'total': 1,
                                'connected': 1,
                                'paused': 0,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:17:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 1,
                                'calls_now_in_queue_max_wait_time_sec': 60.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                    ],
                },
            ],
        },
    )

    # unknown project
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/statistics',
        json={
            'metaqueues': ['ru_taxi_disp'],
            'subclusters': ['2'],
            'project': 'unknown',
        },
    )
    assert response.status == 500

    # unconsistent project and queues
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/statistics',
        json={
            'metaqueues': ['ru_taxi_disp', 'ru_taxi_support'],
            'subclusters': ['2'],
            'project': 'disp',
        },
    )
    assert response.status == 409

    # subclusters (2 sub) + project filtering (1 2 3 sub) = total 2 sub
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/statistics',
        json={
            'metaqueues': ['ru_taxi_disp'],
            'subclusters': ['2'],
            'project': 'disp',
        },
    )
    assert response.status == 200
    result = response.json()
    print(result)
    assert _ordered(result) == _ordered(
        {
            'subclusters_statistics': [
                {
                    'name': '2',
                    'stats': {'total': 2, 'connected': 1, 'paused': 1},
                },
            ],
            'metaqueues_statistics': [
                {
                    'name': 'ru_taxi_disp',
                    'stats': {'total': 4, 'connected': 3, 'paused': 1},
                },
            ],
            'queues_statistics': [
                {
                    'metaqueue': 'ru_taxi_disp',
                    'subclusters': [
                        {
                            'subcluster': '2',
                            'operators_stats': {
                                'total': 1,
                                'connected': 1,
                                'paused': 0,
                            },
                            'calls_stats': {
                                'last_event_time': (
                                    '2020-04-21T12:17:50.123456+0000'
                                ),
                                'calls_now_in_queue_count': 1,
                                'calls_now_in_queue_max_wait_time_sec': 60.0,
                            },
                            'params': {
                                'enabled': True,
                                'enabled_for_call_balancing': True,
                                'enabled_for_sip_user_autobalancing': True,
                            },
                        },
                    ],
                },
            ],
        },
    )
