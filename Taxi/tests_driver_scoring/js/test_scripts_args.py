import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets

BODY = {
    'request': {
        'search': {
            'order_id': 'order0',
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
                'metadata': {'reposition': {'mode': 'home', 'suitable': True}},
            },
        ],
    },
    'intent': 'dispatch-buffer',
}


@pytest.mark.experiments3(filename='js_bonus.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['sample_js_scripts.sql'])
@pytest.mark.config(
    JS_BONUS_TIMEOUTS_BY_INTENT={
        '__default__': {
            'single_bonus_timeout': 10000,
            'all_bonuses_timeout': 10000,
        },
    },
)
@pytest.mark.tags_v2_index(
    tags_list=[
        ('dbid_uuid', 'dbid0_uuid0', 'silver'),
        ('dbid_uuid', 'dbid0_uuid0', 'private_car'),
    ],
)
@pytest.mark.reposition_matcher_check_results(
    {(b'dbid0', b'uuid0', b'order0'): {'mode': 'home'}},
)
async def test_js_scripts_args_validation(taxi_driver_scoring):
    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=BODY,
    )
    assert response.status_code == 200
    candidate = response.json()['candidates'][0]
    assert candidate['id'] == 'dbid0_uuid0'
    assert candidate['score'] == 200.0
