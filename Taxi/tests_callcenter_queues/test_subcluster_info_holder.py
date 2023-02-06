import pytest


@pytest.mark.config(
    CALLCENTER_ROUTING_SUBCLUSTER_INFO_MAP={}, CALLCENTER_METAQUEUES=[],
)
async def test_subcluster_info_holder(
        taxi_callcenter_queues, taxi_config, pgsql,
):

    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.get(
        '/tests/system-info-holder/get_info',
    )
    assert response.status == 200
    result = response.json()
    assert result == {'metaqueues_info': {}, 'subcluster_list': []}

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
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.get(
        '/tests/system-info-holder/get_info',
    )
    assert response.status == 200
    result = response.json()
    assert result == {'metaqueues_info': {}, 'subcluster_list': ['1']}

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
                    'name': 'kz_taxi_disp',
                    'number': '840100',
                },
            ],
        },
    )
    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.get(
        '/tests/system-info-holder/get_info',
    )
    assert response.status == 200
    result = response.json()
    assert result == {
        'metaqueues_info': {
            'kz_taxi_disp': {
                'subclusters': [
                    {
                        'enabled_for_call_balancing': False,
                        'enabled_for_sip_user_autobalancing': False,
                        'enabled': False,
                        'subcluster': '1',
                    },
                ],
            },
        },
        'subcluster_list': ['1'],
    }

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
                    'endpoint': 'QPROC02',
                    'endpoint_count': 1,
                    'endpoint_strategy': 'TOPDOWN',
                    'endpoint_strategy_option': 1,
                    'timeout_sec': 180,
                },
                '3': {
                    'endpoint': 'QPROC03',
                    'endpoint_count': 1,
                    'endpoint_strategy': 'TOPDOWN',
                    'endpoint_strategy_option': 1,
                    'timeout_sec': 180,
                },
            },
            'CALLCENTER_METAQUEUES': [
                {
                    'allowed_clusters': ['1', '2', '3'],
                    'name': 'kz_taxi_disp',
                    'number': '840100',
                },
                {
                    'allowed_clusters': ['1', '2', '3'],
                    'name': 'ru_taxi_disp',
                    'number': '850100',
                },
            ],
        },
    )
    cursor = pgsql['callcenter_queues'].cursor()
    cursor.execute('DELETE FROm callcenter_queues.callcenter_system_info')
    cursor.execute(
        """INSERT INTO callcenter_queues.callcenter_system_info
           (
           metaqueue,
           subcluster,
           enabled_for_call_balancing,
           enabled_for_sip_user_autobalancing,
           enabled
           )
           VALUES
           ('ru_taxi_disp', '1', true, false, true),
           ('ru_taxi_disp', '2', true, false, true),
           ('ru_taxi_disp', '3', true, true, true),
           ('kz_taxi_disp', '1', true, true, true),
           ('kz_taxi_disp', '2', true, true, true),
           ('kz_taxi_disp', '3', true, false, true);""",
    )
    cursor.close()
    await taxi_callcenter_queues.invalidate_caches()
    response = await taxi_callcenter_queues.get(
        '/tests/system-info-holder/get_info',
    )
    assert response.status == 200
    result = response.json()
    metaqueues = set(result['metaqueues_info'].keys())
    assert metaqueues == {'kz_taxi_disp', 'ru_taxi_disp'}

    clusters = set(result['subcluster_list'])
    assert clusters == {'1', '2', '3'}
    kz_taxi_disp_enabled = set(
        sub['subcluster']
        for sub in result['metaqueues_info']['kz_taxi_disp']['subclusters']
        if sub['enabled_for_sip_user_autobalancing']
    )
    kz_taxi_disp_disabled = set(
        sub['subcluster']
        for sub in result['metaqueues_info']['kz_taxi_disp']['subclusters']
        if not sub['enabled_for_sip_user_autobalancing']
    )
    assert kz_taxi_disp_enabled == {'1', '2'}
    assert kz_taxi_disp_disabled == {'3'}
    ru_taxi_disp_enabled = set(
        sub['subcluster']
        for sub in result['metaqueues_info']['ru_taxi_disp']['subclusters']
        if sub['enabled_for_sip_user_autobalancing']
    )
    ru_taxi_disp_disabled = set(
        sub['subcluster']
        for sub in result['metaqueues_info']['ru_taxi_disp']['subclusters']
        if not sub['enabled_for_sip_user_autobalancing']
    )
    assert ru_taxi_disp_enabled == {'3'}
    assert ru_taxi_disp_disabled == {'1', '2'}
