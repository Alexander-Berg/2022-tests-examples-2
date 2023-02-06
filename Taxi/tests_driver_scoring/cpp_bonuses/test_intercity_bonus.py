import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

HEADERS = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}


@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
@pytest.mark.reposition_matcher_check_results(
    {
        (b'dbid0', b'uuid0', b'order0'): {
            'mode': 'home',
            'suitable': True,
            'score': 0.25,
        },
        (b'dbid1', b'uuid1', b'order0'): {
            'mode': 'home',
            'suitable': True,
            'score': 0.05,
        },
        (b'dbid2', b'uuid2', b'order0'): {'mode': 'home', 'suitable': False},
    },
)
async def test_intercity_bonus(taxi_driver_scoring, experiments3):
    experiments3.add_experiment(
        consumers=['driver-scoring/driver-scoring'],
        name='driver_scoring_intercity_settings',
        match={
            'enabled': True,
            'consumers': [{'name': 'driver-scoring/driver-scoring'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'true',
                'predicate': {'type': 'true'},
                'value': {
                    'reposition_score_threshold': 0.1,
                    'bonus_value': 1000,
                },
            },
        ],
    )

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
                    'intercity': {'enabled': True},
                },
                'allowed_classes': ['econom', 'comfortplus'],
            },
            'candidates': [
                {  # bonus: 1000
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom'],
                    'metadata': {'reposition_check_required': True},
                },
                {  # bonus: 0
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'comfortplus'],
                    'metadata': {'reposition_check_required': True},
                },
                {  # bonus: 0
                    'id': 'dbid2_uuid2',
                    'route_info': {
                        'time': 500,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['comfortplus'],
                    'metadata': {'reposition_check_required': True},
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    expected = [
        {
            'id': 'dbid0_uuid0',
            'score': -500.0,
            'metadata': {
                'reposition_check_required': True,
                'reposition': {
                    'mode': 'home',
                    'suitable': True,
                    'score': 0.25,
                },
            },
        },
    ]

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=body,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == expected
