import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


BODY = {
    'request': {
        'search': {
            'order_id': '16e83c16beb74880b819d2a7b1c06d93',
            'order': {
                'request': {
                    'source': {'geopoint': [39.60258, 52.569089]},
                    'surge_price': 5.0,
                },
            },
            'allowed_classes': ['econom'],
        },
        'candidates': [
            {
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 650,
                    'distance': 1450,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom', 'business'],
            },
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 124,
                    'distance': 3200,
                    'approximate': False,
                },
                'position': [39.609112, 52.570000],
                'classes': ['econom', 'business'],
            },
        ],
    },
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='no_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.parametrize(
    'weights,expected',
    [
        (
            {'ALPHA': 0, 'BETA': 0},
            {'dbid0_uuid0': 650.0, 'dbid1_uuid1': 124.0},
        ),
        (
            {'ALPHA': 0.3, 'BETA': 2},
            {'dbid0_uuid0': 1325.0, 'dbid1_uuid1': 2006.8},
        ),
    ],
)
async def test_driver_scoring_weights(
        taxi_driver_scoring, weights, taxi_config, expected, experiments3,
):
    experiments3.add_config(
        consumers=['driver-scoring/driver-scoring'],
        name='driver_scoring_time_dist_weights',
        match={
            'enabled': True,
            'consumers': [{'name': 'driver-scoring/driver-scoring'}],
            'predicate': {'type': 'true', 'init': {}},
        },
        clauses=[],
        default_value=weights,
    )

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200

    candidates = response.json()['candidates']
    candidates.sort(key=lambda x: x['id'])
    assert candidates == [
        {'id': 'dbid0_uuid0', 'score': expected['dbid0_uuid0']},
        {'id': 'dbid1_uuid1', 'score': expected['dbid1_uuid1']},
    ]


@pytest.mark.experiments3(filename='time_dist_weights.json')
@pytest.mark.experiments3(filename='no_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    TAG_SCORE_COEFFS={'__default__': 1.0, 'tag-10': 10.0, 'tag-0.1': 0.1},
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'tag-0.1'),
        ('dbid_uuid', 'dbid0_uuid0', 'random-tag'),
        ('dbid_uuid', 'dbid1_uuid1', 'tag-10'),
        ('park', 'dbid1', 'tag-0.1'),
        ('dbid_uuid', 'dbid3_uuid3', 'random-tag-1'),
        ('dbid_uuid', 'dbid3_uuid3', 'random-tag-2'),
    ],
)
async def test_driver_scoring_tag_score_coeffs(
        taxi_driver_scoring, taxi_config,
):
    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {
                        'source': {'geopoint': [39.60258, 52.569089]},
                        'surge_price': 5.0,
                    },
                },
                'allowed_classes': ['econom'],
            },
            'candidates': [
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 650,
                        'distance': 1450,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid1_uuid1',
                    'route_info': {
                        'time': 124,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid2_uuid2',
                    'route_info': {
                        'time': 124,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': ['econom', 'business'],
                },
                {
                    'id': 'dbid3_uuid3',
                    'route_info': {
                        'time': 124,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.609112, 52.570000],
                    'classes': ['econom', 'business'],
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=body,
    )
    assert response.status_code == 200

    candidates = response.json()['candidates']
    candidates.sort(key=lambda x: x['id'])
    assert candidates == [
        {'id': 'dbid0_uuid0', 'score': 68.75},  # 0.1
        {'id': 'dbid1_uuid1', 'score': 8620.0},  # max(0.1, 10.0)
        {'id': 'dbid2_uuid2', 'score': 862.0},  # 1.0 (default)
        {'id': 'dbid3_uuid3', 'score': 862.0},  # 1.0 (default)
    ]
