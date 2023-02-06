import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.config(
    VERYBUSY_BONUS={
        '__default__': {'__default__': 0},
        'lipetsk': {'__default__': 0, 'econom': -90, 'comfortplus': -100},
    },
)
async def test_penalty_for_approximate_position(taxi_driver_scoring):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}

    common_candidate = {
        'route_info': {'time': 650, 'distance': 1450, 'approximate': False},
        'position': [39.59568, 52.568001],
        'classes': ['econom', 'business'],
        'status': {'driver': 'verybusy'},
    }

    cand1 = {'id': 'dbid0_uuid0', 'metadata': {'verybusy_order': True}}
    cand1.update(common_candidate)

    cand2 = {'id': 'dbid1_uuid1'}
    cand2.update(common_candidate)

    body = {
        'request': {
            'search': {
                'order_id': '16e83c16beb74880b819d2a7b1c06d93',
                'order': {
                    'request': {'source': {'geopoint': [39.60258, 52.569089]}},
                    'nearest_zone': 'lipetsk',
                },
                'allowed_classes': ['econom', 'comfortplus'],
            },
            'candidates': [cand1, cand2],
        },
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=headers, json=body,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 650.0},
        {
            'id': 'dbid0_uuid0',
            'metadata': {'verybusy_order': True},
            'score': 740.0,
        },
    ]
