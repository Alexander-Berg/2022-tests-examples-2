import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


BODY = {
    'request': {
        'search': {
            'order_id': '16e83c16beb74880b819d2a7b1c06d93',
            'order': {
                'request': {'source': {'geopoint': [39.60258, 52.569089]}},
            },
            'allowed_classes': ['econom'],
            'sv': 5.0,
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


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    TVM_ENABLED=True, TVM_RULES=[{'src': 'mock', 'dst': 'driver-scoring'}],
)
async def test_driver_scoring_tolerant_bonus_for_surge(taxi_driver_scoring):

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200

    assert response.json()['candidates'] == [
        # eta = 650
        # score = 2.0 * (5 - 1 - 1) - 0.5 * max(1 - 5, 0) = 6
        # 650 - 6 = 644
        {'id': 'dbid1_uuid1', 'score': 118.0},
        {'id': 'dbid0_uuid0', 'score': 644.0},
    ]
