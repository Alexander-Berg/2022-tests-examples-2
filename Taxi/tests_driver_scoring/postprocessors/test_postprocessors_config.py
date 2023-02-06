import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

BODY = {
    'request': {
        'search': {
            'order_id': '16e83c16beb74880b819d2a7b1c06d93',
            'order': {
                'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                'nearest_zone': 'lipetsk',
            },
            'allowed_classes': ['child_tariff'],
        },
        'candidates': [
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 1001,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['child_tariff'],
            },
            {
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 1000,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['child_tariff'],
            },
            {
                'id': 'dbid2_uuid2',
                'route_info': {
                    'time': 600,
                    'distance': 1,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['child_tariff'],
                'metadata': {'reposition_check_required': True},
            },
        ],
    },
    'intent': 'dispatch-buffer',
}

HEADER = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}


@pytest.mark.experiments3(filename='no_bonuses.json')
@pytest.mark.experiments3(filename='exp3_postprocessors_sorting.json')
@pytest.mark.config(DISPATCH_CLASSES_ORDER=['child_tariff'])
async def test_sorting(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADER, json=BODY,
    )

    assert response.status_code == 200
    assert response.json()['candidates'] == [
        {
            'id': 'dbid2_uuid2',
            'metadata': {'reposition_check_required': True},
            'score': 600.0,
        },
        {'id': 'dbid0_uuid0', 'score': 1000.0},
        {'id': 'dbid1_uuid1', 'score': 1001.0},
    ]


@pytest.mark.experiments3(filename='bonus_with_filter.json')
@pytest.mark.experiments3(filename='exp3_postprocessors_sorting.json')
@pytest.mark.config(DISPATCH_CLASSES_ORDER=['child_tariff'])
async def test_sorting_with_filter(taxi_driver_scoring):
    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['child_tariff'],
            },
            'candidates': [
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 1001,
                        'distance': 1,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['child_tariff'],
                },
                {
                    'id': 'dbid3_uuid3',
                    'route_info': {
                        'time': 500,
                        'distance': 1,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['child_tariff'],
                    'metadata': {'reposition_check_required': True},
                },
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 1000,
                        'distance': 1,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['child_tariff'],
                },
                {
                    'id': 'dbid2_uuid2',
                    'route_info': {
                        'time': 600,
                        'distance': 1,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['child_tariff'],
                    'metadata': {'reposition_check_required': True},
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADER, json=body,
    )

    assert response.status_code == 200
    assert response.json()['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 1000.0},
        {'id': 'dbid1_uuid1', 'score': 1001.0},
        # pessimized: delta = 1001 - 500 + 1
        {
            'id': 'dbid3_uuid3',
            'metadata': {'reposition_check_required': True},
            'score': 1002.0,
        },
        {
            'id': 'dbid2_uuid2',
            'metadata': {'reposition_check_required': True},
            'score': 1102.0,
        },
    ]


@pytest.mark.experiments3(filename='bonus_with_filter.json')
@pytest.mark.experiments3(
    filename='exp3_postpro_exclude_by_filters_and_sorting.json',
)
@pytest.mark.config(DISPATCH_CLASSES_ORDER=['child_tariff'])
async def test_exclude_by_filters_and_sorting(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADER, json=BODY,
    )

    assert response.status_code == 200
    assert response.json()['candidates'] == [
        {'id': 'dbid0_uuid0', 'score': 1000.0},
        {'id': 'dbid1_uuid1', 'score': 1001.0},
    ]
