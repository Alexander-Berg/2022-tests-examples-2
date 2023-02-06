import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.tags_v2_index(
    tags_list=[('dbid_uuid', 'dbid0_uuid0', 'antibonus_tag')],
)
async def test_penalty_for_tags_full_cashback_orders(taxi_driver_scoring):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
    body = {
        'request': {
            'search': {
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['econom'],
                'payment_tech': {'type': 'personal_wallet'},
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                    'unique_driver_id': 'udid0',
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=headers, json=body,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 500.0},
        {'id': 'dbid0_uuid0', 'score': 531.0},
    ]


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.tags_v2_index(
    tags_list=[('dbid_uuid', 'dbid0_uuid0', 'antibonus_tag')],
)
async def test_penalty_for_tags_complement_cashback_orders(
        taxi_driver_scoring,
):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
    body = {
        'request': {
            'search': {
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['econom'],
                'payment_tech': {
                    'type': 'cash',
                    'complements': [
                        {
                            'type': 'personal_wallet',
                            'payment_method_id': (
                                'w/92c4f7ba-16fb-5229-b995-6425d6c72df2'
                            ),
                        },
                    ],
                },
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                    'unique_driver_id': 'udid0',
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=headers, json=body,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 500.0},
        {'id': 'dbid0_uuid0', 'score': 531.0},
    ]
