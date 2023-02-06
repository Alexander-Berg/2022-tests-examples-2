import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='default_priority_coefficient.json')
async def test_bonus_for_priority(
        taxi_driver_scoring, driver_priority_values_mock,
):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}

    driver_priority_values_mock.set_priority('dbid0', 'uuid0', [('aba', 1)])
    driver_priority_values_mock.set_priority('dbid1', 'uuid1', [('caba', 2)])
    driver_priority_values_mock.set_priority('dbid2', 'uuid2', [('daba', 3)])
    body = {
        'requests': [
            {
                # no nearest zone
                'search': {
                    'order': {
                        'request': {
                            'source': {'geopoint': [49.60252, 52.569082]},
                        },
                    },
                    'allowed_classes': ['econom'],
                },
                'candidates': [
                    {
                        'id': 'dbid4_uuid4',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [49.59568, 52.568001],
                        'classes': ['econom', 'business'],
                        'unique_driver_id': 'udid0',
                    },
                ],
            },
            {
                'search': {
                    'order': {
                        'request': {
                            'source': {'geopoint': [39.60258, 52.569089]},
                        },
                        'nearest_zone': 'lipetsk',
                    },
                    'allowed_classes': ['econom'],
                },
                'candidates': [
                    {  # priority: 1
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
                    {  # priority: 2
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
            {
                'search': {
                    'order': {
                        'request': {
                            'source': {'geopoint': [39.60252, 52.569082]},
                        },
                        'nearest_zone': 'lipetsk',
                    },
                    'allowed_classes': ['econom'],
                },
                'candidates': [
                    {  # priority: 3
                        'id': 'dbid2_uuid2',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom', 'business'],
                        'unique_driver_id': 'udid0',
                    },
                    {  # no priority
                        'id': 'dbid3_uuid3',
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
        ],
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=headers, json=body,
    )

    should_be = [
        {'dbid4_uuid4': 500.0},
        {'dbid0_uuid0': 499.0, 'dbid1_uuid1': 498.0},
        {'dbid2_uuid2': 497.0, 'dbid3_uuid3': 500.0, 'dbid5_uuid5': 490},
    ]
    assert response.status_code == 200
    for should_be_chunk, chunk in zip(should_be, response.json()['responses']):
        for score in chunk['candidates']:
            assert score['id'] in should_be_chunk
            assert score['score'] == should_be_chunk[score['id']]


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='priority_coefficient.json')
@pytest.mark.tags_v2_index(
    tags_list=[('dbid_uuid', 'dbid0_uuid0', 'driver_fix_bad_guy')],
)
async def test_priority_experiment(
        taxi_driver_scoring, driver_priority_values_mock,
):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}

    for i in range(3):
        driver_priority_values_mock.set_priority(
            f'dbid{i}', f'uuid{i}', [('aba', 1)],
        )
    body = {
        'requests': [
            {
                'search': {
                    'order': {
                        'request': {
                            'source': {'geopoint': [39.60258, 52.569089]},
                        },
                        'nearest_zone': 'moscow',
                    },
                    'allowed_classes': ['econom', 'business'],
                },
                'candidates': [
                    {  # priority: 1, multiplied by 100 in experiment
                        'id': 'dbid0_uuid0',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom'],
                        'unique_driver_id': 'udid0',
                    },
                ],
            },
            {
                'search': {
                    'order': {
                        'request': {
                            'source': {'geopoint': [39.60258, 52.569089]},
                        },
                        'nearest_zone': 'moscow',
                    },
                    'allowed_classes': ['econom', 'business', 'vip'],
                },
                'candidates': [
                    {  # priority: 1, multiplied by 10 in experiment
                        'id': 'dbid1_uuid1',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom'],
                        'unique_driver_id': 'udid0',
                    },
                    {  # priority: 1, multiplied by 2 in experiment
                        # as default value because vip is not in
                        # dictionary from experiment
                        'id': 'dbid2_uuid2',
                        'route_info': {
                            'time': 500,
                            'distance': 3200,
                            'approximate': False,
                        },
                        'position': [39.59568, 52.568001],
                        'classes': ['econom', 'business', 'vip'],
                        'unique_driver_id': 'udid0',
                    },
                ],
            },
        ],
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates-bulk', headers=headers, json=body,
    )

    should_be = [
        {'dbid0_uuid0': 400.0},
        {'dbid1_uuid1': 490.0, 'dbid2_uuid2': 498.0},
    ]
    assert response.status_code == 200
    for should_be_chunk, chunk in zip(should_be, response.json()['responses']):
        for score in chunk['candidates']:
            assert score['id'] in should_be_chunk
            assert score['score'] == should_be_chunk[score['id']]
