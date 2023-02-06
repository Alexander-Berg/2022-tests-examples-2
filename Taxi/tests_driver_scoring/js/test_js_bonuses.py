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


@pytest.mark.experiments3(filename='js_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_driver_scoring_js_bonuses(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == [
        {'id': 'dbid1_uuid1', 'score': 90.0},
        {'id': 'dbid0_uuid0', 'score': 190.0},
    ]


@pytest.mark.experiments3(filename='js_filtration.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_driver_scoring_js_filtration(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    assert response.json()['candidates'] == []


@pytest.mark.experiments3(filename='js_exception.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
async def test_driver_scoring_js_exception(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    candidates = response.json()['candidates']
    assert len(candidates) == 2

    # fallback to cpp bonus:
    assert candidates[0]['id'] == 'dbid1_uuid1'
    assert 142.0 < candidates[0]['score'] < 143.0

    assert candidates[1]['id'] == 'dbid0_uuid0'
    assert 242.0 < candidates[1]['score'] < 243.0


@pytest.mark.experiments3(filename='js_timeout.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_scripts.sql'])
@pytest.mark.config(
    JS_BONUS_TIMEOUTS_BY_INTENT={
        '__default__': {
            'single_bonus_timeout': 200,
            'all_bonuses_timeout': 2000,
        },
    },
)
async def test_driver_scoring_js_timeout(taxi_driver_scoring):
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
