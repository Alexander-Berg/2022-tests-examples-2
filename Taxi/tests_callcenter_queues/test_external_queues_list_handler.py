import pytest


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    return obj


@pytest.mark.pgsql(
    'callcenter_queues', files=['insert_agents.sql', 'insert_system_info.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'disp': {
            'metaqueues': ['ru_taxi_disp'],
            'should_use_internal_queue_service': True,
            'display_name': '',
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
async def test_subclusters_list_handler(
        taxi_callcenter_queues, taxi_config, pgsql,
):
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
                    'allowed_clusters': ['1', '2'],
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
        '/cc/v1/callcenter-queues/v1/queues/list', json={},
    )
    assert response.status == 200
    result = response.json()
    print(_ordered(result))
    assert _ordered(result) == _ordered(
        {
            'metaqueues': [
                {
                    'name': 'ru_taxi_support',
                    'subclusters': ['1', '2'],
                    'number': '840100',
                },
                {
                    'name': 'ru_taxi_econom',
                    'subclusters': ['1', '2'],
                    'number': '840100',
                },
                {
                    'name': 'ru_taxi_disp',
                    'subclusters': ['1', '2'],
                    'number': '840100',
                },
            ],
        },
    )

    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/list',
        json={'metaqueues': ['ru_taxi_disp']},
    )
    assert response.status == 200
    result = response.json()
    assert _ordered(result) == _ordered(
        {
            'metaqueues': [
                {
                    'name': 'ru_taxi_disp',
                    'subclusters': ['1', '2'],
                    'number': '840100',
                },
            ],
        },
    )

    # test good project
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/list',
        json={'metaqueues': ['ru_taxi_disp'], 'project': 'disp'},
    )
    assert response.status == 200
    result = response.json()
    assert _ordered(result) == _ordered(
        {
            'metaqueues': [
                {
                    'name': 'ru_taxi_disp',
                    'subclusters': ['1', '2'],
                    'number': '840100',
                },
            ],
        },
    )

    # test unknown project
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/list',
        json={'metaqueues': ['ru_taxi_disp'], 'project': 'help'},
    )
    assert response.status == 500

    # test unconsistent project
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/list',
        json={'metaqueues': ['ru_taxi_disp'], 'project': 'support'},
    )
    assert response.status == 409

    # test project
    response = await taxi_callcenter_queues.post(
        '/cc/v1/callcenter-queues/v1/queues/list', json={'project': 'disp'},
    )
    assert response.status == 200
    result = response.json()
    assert _ordered(result) == _ordered(
        {
            'metaqueues': [
                {
                    'name': 'ru_taxi_disp',
                    'subclusters': ['1', '2'],
                    'number': '840100',
                },
            ],
        },
    )
