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
                    'time': 300,
                    'distance': 1000,
                    'approximate': False,
                },
                'position': [39.59568, 52.568001],
                'classes': ['econom', 'business'],
            },
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 200,
                    'distance': 500,
                    'approximate': False,
                },
                'position': [39.609112, 52.570000],
                'classes': ['econom', 'business'],
            },
        ],
    },
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='js_invalid_calculate.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_return_nan.sql'])
async def test_driver_scoring_js_nan(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    # fallback to cpp bonus:
    assert response.json()['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 213.0},
        {'id': 'dbid0_uuid0', 'score': 313.0},
    ]


@pytest.mark.experiments3(filename='js_invalid_calculate.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_return_inf.sql'])
async def test_driver_scoring_js_inf(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    # fallback to cpp bonus:
    assert response.json()['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 213.0},
        {'id': 'dbid0_uuid0', 'score': 313.0},
    ]


@pytest.mark.experiments3(filename='js_invalid_calculate.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_return_object.sql'])
async def test_driver_scoring_js_object(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    # fallback to cpp bonus:
    assert response.json()['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 213.0},
        {'id': 'dbid0_uuid0', 'score': 313.0},
    ]


@pytest.mark.experiments3(filename='js_invalid_filter.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_return_minus_one.sql'])
@pytest.mark.config(
    ROUTER_EXPERIMENTS_BY_INTENT={'dispatch-buffer': ['dispatch-buffer']},
)
@pytest.mark.reposition_matcher_check_results(
    {
        (b'dbid0', b'uuid0', b'driver_scoring_fake_id_0'): {
            'mode': 'home',
            'suitable': False,
        },
    },
)
async def test_bonus_for_reposition_js_minus_one(taxi_driver_scoring):
    headers = {'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET}
    body = {
        'request': {
            'search': {
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
                {
                    'id': 'dbid0_uuid0',
                    'route_info': {
                        'time': 0,
                        'distance': 3200,
                        'approximate': False,
                    },
                    'position': [39.59568, 52.568001],
                    'classes': ['econom'],
                    'metadata': {'reposition_check_required': True},
                },
            ],
        },
        'intent': 'dispatch-buffer',
    }

    response = await taxi_driver_scoring.post(
        'v2/score-candidates', headers=headers, json=body,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == []
