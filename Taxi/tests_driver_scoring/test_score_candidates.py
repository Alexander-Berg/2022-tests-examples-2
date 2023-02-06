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
async def test_score_candidates(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    assert response.json() == {
        'search': {'order_id': '16e83c16beb74880b819d2a7b1c06d93'},
        'candidates': [
            {'id': 'dbid1_uuid1', 'score': 124.0},
            {'id': 'dbid0_uuid0', 'score': 650.0},
        ],
    }


@pytest.mark.experiments3(filename='no_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_score_candidates_invalid_intent(taxi_driver_scoring):
    BODY['intent'] = 'random_intent'
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 400
    assert response.json() == {
        'code': 400,
        'message': 'RequestError: got invalid intent random_intent',
    }
