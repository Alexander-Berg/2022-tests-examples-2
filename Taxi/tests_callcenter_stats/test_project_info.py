import pytest


@pytest.mark.config(
    CALLCENTER_STATS_PROJECT_INFO_MAP={
        'cargo': {
            'display_name': 'Карго',
            'metaqueues': ['ru_davos_disp_cargo'],
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
        'davos': {
            'display_name': 'Давос',
            'metaqueues': [
                'ru_davos_disp',
                'ru_davos_disp_cargo',
                'ru_taxi_disp_economy',
            ],
            'reg_groups': [],
            'should_use_internal_queue_service': True,
        },
    },
)
async def test_values(taxi_callcenter_stats):
    await taxi_callcenter_stats.invalidate_caches()
    # wo project
    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v1/project/info/',
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'projects': [
            {
                'display_name': 'Давос',
                'metaqueues': [
                    'ru_davos_disp',
                    'ru_davos_disp_cargo',
                    'ru_taxi_disp_economy',
                ],
                'name': 'davos',
            },
            {
                'display_name': 'Карго',
                'metaqueues': ['ru_davos_disp_cargo'],
                'name': 'cargo',
            },
        ],
    }
    # project
    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v1/project/info/', json={'project': 'davos'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {
        'projects': [
            {
                'display_name': 'Давос',
                'metaqueues': [
                    'ru_davos_disp',
                    'ru_davos_disp_cargo',
                    'ru_taxi_disp_economy',
                ],
                'name': 'davos',
            },
        ],
    }
    # bad project
    response = await taxi_callcenter_stats.post(
        '/cc/v1/callcenter-stats/v1/project/info/', json={'project': 'disp'},
    )
    assert response.status_code == 200
    response_json = response.json()
    assert response_json == {'projects': []}
