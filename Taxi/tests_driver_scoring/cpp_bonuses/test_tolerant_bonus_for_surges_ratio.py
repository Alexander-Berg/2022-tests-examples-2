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
            'svs': [5.0],
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
async def test_driver_scoring_tolerant_bonus_for_surges_ratio(
        taxi_driver_scoring,
):

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 2

    # tanh(2) ~ 0.96
    # bonus = 60 * tanh(0.5 * (5 - 1)) ~ 57.8

    # eta = 124
    # 124 - 57.8 ~ 66.2
    assert candidates[0]['id'] == 'dbid1_uuid1'
    assert 66.0 < candidates[0]['score'] < 67.0

    # eta = 650
    # 650 - 57.8 ~ 593
    assert candidates[1]['id'] == 'dbid0_uuid0'
    assert 592.0 < candidates[1]['score'] < 593.0
