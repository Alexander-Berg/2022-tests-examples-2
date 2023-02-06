import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),  # bonus: 10
        ('dbid_uuid', 'dbid0_uuid0', 'private_car'),  # bonus: 20
        ('park', 'dbid1', 'park_bonus_top'),  # bonus: 30
        ('dbid_uuid', 'dbid3_uuid3', 'topbusinesscars_new'),  # bonus: 40
        ('udid', 'udid0', 'reposition_super_surge'),  # bonus: 50
    ],
)  # bonus: 50
async def test_bonus_for_tags(taxi_driver_scoring):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
    body = {
        'request': {
            'search': {
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['econom'],
            },
            'candidates': [
                {  # bonus: 10 + 20 + 50 = 80
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
                {  # bonus: 30
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                },
                {  # bonus: 0
                    'id': 'dbid2_uuid2',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                    'car_number': 'b888bb88',
                },
                {  # bonus: 40
                    'id': 'dbid3_uuid3',
                    'dbid': 'dbid3',
                    'uuid': 'uuid3',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': ['econom', 'business'],
                    'car_number': 'a777aa77',
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
        {'id': 'dbid0_uuid0', 'score': 420.0},
        {'id': 'dbid3_uuid3', 'score': 460.0},
        {'id': 'dbid1_uuid1', 'score': 470.0},
        {'id': 'dbid2_uuid2', 'score': 500.0},
    ]
