import pytest


def _ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, _ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(_ordered(x) for x in obj)
    return obj


@pytest.mark.pgsql('callcenter_queues', files=['insert_agents.sql'])
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
    response = await taxi_callcenter_queues.post('/v1/queues/list', json={})
    assert response.status == 200
    result = response.json()
    print(_ordered(result))
    assert _ordered(result) == _ordered(
        {
            'metaqueues': [
                'ru_taxi_support',
                'ru_taxi_econom',
                'ru_taxi_disp',
            ],
            'queues': [
                {
                    'metaqueue': 'ru_taxi_support',
                    'subclusters': [
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '1',
                        },
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '2',
                        },
                    ],
                },
                {
                    'metaqueue': 'ru_taxi_econom',
                    'subclusters': [
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '1',
                        },
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '2',
                        },
                    ],
                },
                {
                    'metaqueue': 'ru_taxi_disp',
                    'subclusters': [
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '1',
                        },
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '2',
                        },
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '3',
                        },
                    ],
                },
            ],
            'subclusters': ['1', '2', '3'],
        },
    )

    response = await taxi_callcenter_queues.post(
        '/v1/queues/list', json={'metaqueues': ['ru_taxi_disp']},
    )
    assert response.status == 200
    result = response.json()
    assert _ordered(result) == _ordered(
        {
            'metaqueues': ['ru_taxi_disp'],
            'queues': [
                {
                    'metaqueue': 'ru_taxi_disp',
                    'subclusters': [
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '1',
                        },
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '2',
                        },
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '3',
                        },
                    ],
                },
            ],
            'subclusters': ['1', '2', '3'],
        },
    )

    response = await taxi_callcenter_queues.post(
        '/v1/queues/list', json={'subclusters': ['2']},
    )
    assert response.status == 200
    result = response.json()
    assert _ordered(result) == _ordered(
        {
            'metaqueues': [
                'ru_taxi_support',
                'ru_taxi_econom',
                'ru_taxi_disp',
            ],
            'queues': [
                {
                    'metaqueue': 'ru_taxi_support',
                    'subclusters': [
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '2',
                        },
                    ],
                },
                {
                    'metaqueue': 'ru_taxi_econom',
                    'subclusters': [
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '2',
                        },
                    ],
                },
                {
                    'metaqueue': 'ru_taxi_disp',
                    'subclusters': [
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '2',
                        },
                    ],
                },
            ],
            'subclusters': ['2'],
        },
    )

    response = await taxi_callcenter_queues.post(
        '/v1/queues/list',
        json={'metaqueues': ['ru_taxi_disp'], 'subclusters': ['2']},
    )
    assert response.status == 200
    result = response.json()
    assert _ordered(result) == _ordered(
        {
            'metaqueues': ['ru_taxi_disp'],
            'queues': [
                {
                    'metaqueue': 'ru_taxi_disp',
                    'subclusters': [
                        {
                            'enabled_for_call_balancing': False,
                            'enabled_for_sip_users_balancing': False,
                            'enabled': False,
                            'name': '2',
                        },
                    ],
                },
            ],
            'subclusters': ['2'],
        },
    )
