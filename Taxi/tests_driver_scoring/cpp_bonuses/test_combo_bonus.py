import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

HEADERS = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_combo_bonus(taxi_driver_scoring, experiments3):
    body = {
        'request': {
            'search': {
                'order_id': 'order0',
                'order': {
                    'request': {
                        'source': {'geopoint': [39.60258, 52.569089]},
                        'destinations': [{'geopoint': [39.60258, 52.569089]}],
                        'surge_price': 1.5,
                    },
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['econom', 'comfortplus'],
            },
            'candidates': [
                {  # not combo, would be pessimized
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 400,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom'],
                },
                {  # no saved_sh, would be pessimized
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 495,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom'],
                    'metadata': {'combo': {}},
                },
                {  # bonus: 10
                    'id': 'dbid2_uuid2',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom'],
                    'metadata': {'combo': {'extra_properties': {'score': 10}}},
                },
            ],
        },
        'intent': 'combo-pricing-info',
    }

    expected = [
        {'id': 'dbid0_uuid0', 'score': 400.0},
        {
            'id': 'dbid2_uuid2',
            'metadata': {'combo': {'extra_properties': {'score': 10}}},
            'score': 490.0,
        },
        {'id': 'dbid1_uuid1', 'metadata': {'combo': {}}, 'score': 495.0},
    ]
    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=body,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == expected
