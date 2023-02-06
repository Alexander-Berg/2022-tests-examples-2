import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


HEADERS = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}


@pytest.mark.reposition_matcher_check_results(
    {
        (b'dbid0', b'uuid0', b'order0'): {
            'mode': 'home',
            'suitable': True,
            'score': 0.5,
        },
        (b'dbid1', b'uuid1', b'order0'): {
            'mode': 'SuperSurge_completed',
            'suitable': True,
            'score': 0.5,
        },
        (b'dbid2', b'uuid2', b'order0'): {
            'mode': 'SuperSurge_completed',
            'suitable': True,
        },
    },
)
@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_driver_scoring_js_bonuses(taxi_driver_scoring, experiments3):
    experiments3.add_experiment(
        consumers=['driver-scoring/reposition-score'],
        name='driver_scoring_reposition_score',
        match={
            'enabled': True,
            'consumers': [{'name': 'driver-scoring/reposition-score'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[
            {
                'title': 'home',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'reposition_mode',
                        'arg_type': 'string',
                        'value': 'home',
                    },
                },
                'value': {'b': 100.0, 'c': 1.0, 'd': 40.0},
            },
            {
                'title': 'SuperSurge_completed',
                'predicate': {
                    'type': 'eq',
                    'init': {
                        'arg_name': 'reposition_mode',
                        'arg_type': 'string',
                        'value': 'SuperSurge_completed',
                    },
                },
                'value': {'b': 100.0, 'c': 2.0, 'd': 20.0},
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
                },
                'allowed_classes': ['econom', 'comfortplus'],
            },
            'candidates': [
                {  # bonus: 120
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
                {  # bonus: 60
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
                {  # bonus: 60
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
            'score': 270.0,
            'metadata': {
                'reposition_check_required': True,
                'reposition': {
                    'mode': 'home',
                    'suitable': True,
                    'score': 0.5,
                    'score_parameters': {'b': 100.0, 'c': 1.0, 'd': 40.0},
                },
            },
        },
        {
            'id': 'dbid1_uuid1',
            'score': 285.0,
            'metadata': {
                'reposition_check_required': True,
                'reposition': {
                    'mode': 'SuperSurge_completed',
                    'suitable': True,
                    'score': 0.5,
                    'score_parameters': {'b': 100.0, 'c': 2.0, 'd': 20.0},
                },
            },
        },
        {
            'id': 'dbid2_uuid2',
            'score': 330.0,
            'metadata': {
                'reposition_check_required': True,
                'reposition': {
                    'mode': 'SuperSurge_completed',
                    'suitable': True,
                    'score_parameters': {'b': 100.0, 'c': 2.0, 'd': 20.0},
                },
            },
        },
    ]

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=HEADERS, json=body,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == expected
