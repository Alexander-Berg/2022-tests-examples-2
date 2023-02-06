import pytest


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={},
    CALLCENTER_METAQUEUES=[],
    CALLCENTER_SUBCLUSTER_MAX_OPERATORS_AMOUNT=10,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
)
async def test_subcluster_loadness_calculator_no_data(
        taxi_callcenter_queues, taxi_config,
):
    # no cluster no agents
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()
    assert result == {}

    # has cluster but no agents
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
            },
            'CALLCENTER_METAQUEUES': [
                {
                    'allowed_clusters': ['1'],
                    'name': 'ru_taxi_disp',
                    'number': '840100',
                },
            ],
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()['loadness']
    assert result == {'ru_taxi_disp': {'1': 0.0}}


@pytest.mark.pgsql('callcenter_queues', files=['insert_agents.sql'])
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={},
    CALLCENTER_METAQUEUES=[],
    CALLCENTER_SUBCLUSTER_MAX_OPERATORS_AMOUNT=10,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
)
async def test_subcluster_loadness_calculator_with_data(
        taxi_callcenter_queues, taxi_config, pgsql,
):
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('SELECT * from callcenter_queues.tel_state')
    agents = cursor.fetchall()
    assert agents
    cursor.close()
    # no clusters
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()
    assert result == {}

    # one cluster in config
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
            },
            'CALLCENTER_METAQUEUES': [
                {
                    'allowed_clusters': ['1'],
                    'name': 'ru_taxi_disp',
                    'number': '840100',
                },
            ],
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()['loadness']
    assert result == {'ru_taxi_disp': {'1': 0.25}}

    # two clusters in config
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
            },
            'CALLCENTER_METAQUEUES': [
                {
                    'allowed_clusters': ['1', '2'],
                    'name': 'ru_taxi_disp',
                    'number': '840100',
                },
            ],
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()['loadness']
    assert result == {'ru_taxi_disp': {'1': 0.25, '2': 0.05}}

    # more clusters allowed, but not in work by metaqueue
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
                '4': {
                    'endpoint': 'QPROC01',
                    'endpoint_count': 1,
                    'endpoint_strategy': 'TOPDOWN',
                    'endpoint_strategy_option': 1,
                    'timeout_sec': 180,
                },
            },
            'CALLCENTER_METAQUEUES': [
                {
                    'allowed_clusters': ['1', '2'],
                    'name': 'ru_taxi_disp',
                    'number': '840100',
                },
            ],
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()['loadness']
    assert result == {
        'ru_taxi_disp': {'1': 0.25, '2': 0.05, '3': 0.025, '4': 0.0},
    }

    # new metaqueueus and new clusters (disp_on_4 is empty)
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
                '4': {
                    'endpoint': 'QPROC01',
                    'endpoint_count': 1,
                    'endpoint_strategy': 'TOPDOWN',
                    'endpoint_strategy_option': 1,
                    'timeout_sec': 180,
                },
            },
            'CALLCENTER_METAQUEUES': [
                {
                    'allowed_clusters': ['1', '2', '3', '4'],
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
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()['loadness']
    assert result == {
        'ru_taxi_disp': {'1': 0.25, '2': 0.05, '3': 0.025, '4': 0.0},
        'ru_taxi_econom': {'1': 0.5, '2': 0.0, '3': 0.0, '4': 0.0},
        'ru_taxi_support': {'1': 0.25, '2': 0.1, '3': 0.0, '4': 0.0},
    }

    # disp_on_4 disp_on_3 is disabled
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
                '4': {
                    'endpoint': 'QPROC01',
                    'endpoint_count': 1,
                    'endpoint_strategy': 'TOPDOWN',
                    'endpoint_strategy_option': 1,
                    'timeout_sec': 180,
                },
            },
            'CALLCENTER_METAQUEUES': [
                {
                    'allowed_clusters': ['1', '2', '3', '4'],
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
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()['loadness']
    assert result == {
        'ru_taxi_disp': {'1': 0.25, '2': 0.05, '3': 0.025, '4': 0.0},
        'ru_taxi_econom': {'1': 0.5, '2': 0.0, '3': 0.0, '4': 0.0},
        'ru_taxi_support': {'1': 0.25, '2': 0.1, '3': 0.0, '4': 0.0},
    }

    # limit is 2 and 1 and 2 subs are full
    taxi_config.set_values(
        {
            'CALLCENTER_SUBCLUSTER_MAX_OPERATORS_AMOUNT': 2,
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
            ],
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    await taxi_callcenter_queues.run_periodic_task(
        'subcluster-loadness-calculator',
    )
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()['loadness']
    assert result == {'ru_taxi_disp': {'1': 1.0, '2': 1.0, '3': 0.125}}


@pytest.mark.pgsql('callcenter_queues', files=['insert_agents.sql'])
@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={},
    CALLCENTER_METAQUEUES=[],
    CALLCENTER_SUBCLUSTER_MAX_OPERATORS_AMOUNT=10,
    CALLCENTER_ROUTING_QUEUE_NAME_DELIMITER='_on_',
)
async def test_subcluster_loadness_calculator_counters(
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
    response = await taxi_callcenter_queues.get(
        '/tests/subcluster-loadness-calculator',
    )
    assert response.status == 200
    result = response.json()['counters']
    assert result == {
        'by_metaqueues': {
            'ru_taxi_disp': {'connected': 3, 'paused': 1, 'total': 4},
            'ru_taxi_econom': {'connected': 1, 'paused': 1, 'total': 2},
            'ru_taxi_support': {'connected': 2, 'paused': 2, 'total': 4},
        },
        'by_subclusters': {
            '1': {'connected': 3, 'paused': 2, 'total': 5},
            '2': {'connected': 1, 'paused': 1, 'total': 2},
            '3': {'connected': 1, 'paused': 0, 'total': 1},
        },
        'by_queues': {
            'ru_taxi_disp': {
                '1': {'connected': 1, 'paused': 1, 'total': 2},
                '2': {'connected': 1, 'paused': 0, 'total': 1},
                '3': {'connected': 1, 'paused': 0, 'total': 1},
            },
            'ru_taxi_support': {
                '1': {'connected': 1, 'paused': 1, 'total': 2},
                '2': {'connected': 1, 'paused': 1, 'total': 2},
                '3': {'connected': 0, 'paused': 0, 'total': 0},
            },
            'ru_taxi_econom': {
                '1': {'connected': 1, 'paused': 1, 'total': 2},
                '2': {'connected': 0, 'paused': 0, 'total': 0},
                '3': {'connected': 0, 'paused': 0, 'total': 0},
            },
        },
    }
