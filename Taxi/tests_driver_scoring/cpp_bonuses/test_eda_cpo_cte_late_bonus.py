import copy

import pytest

import tests_driver_scoring.dispatch_settings as dispatch_settings
import tests_driver_scoring.tvm_tickets as tvm_tickets


REQUEST = {
    'request': {
        'search': {
            'order_id': 'TBD',
            'order': {
                'request': {
                    'source': {'geopoint': [39.60258, 52.569089]},
                    'surge_price': 5.0,
                },
            },
            'allowed_classes': ['courier'],
        },
        'candidates': [
            {
                'id': 'dbid0_uuid0',
                'route_info': {
                    'time': 770,
                    'distance': 2450,
                    'approximate': False,
                },
                'position': [39.59570, 52.56800],
                'classes': ['courier', 'express'],
            },
            {
                'id': 'dbid1_uuid1',
                'route_info': {
                    'time': 770,
                    'distance': 2450,
                    'approximate': False,
                },
                'position': [39.59560, 52.56800],
                'classes': ['courier', 'express'],
            },
        ],
    },
    'intent': 'united-dispatch-eats',
}


def get_limited_dispatch_settings(
        dispatch_max_positive_bonus_seconds=None,
        dispatch_min_negative_bonus_seconds=None,
):
    settings = copy.deepcopy(dispatch_settings._DEFAULT_VALUES)
    settings['parameters'] = [
        {
            'values': {
                'DISPATCH_MAX_POSITIVE_BONUS_SECONDS': (
                    dispatch_max_positive_bonus_seconds
                ),
                'DISPATCH_MIN_NEGATIVE_BONUS_SECONDS': (
                    dispatch_min_negative_bonus_seconds
                ),
            },
        },
    ]
    return settings


#
# Тест на отказ js-скрипта скоринга и фоллбек на отрицательный бонус.
#
@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
@pytest.mark.pgsql('driver_scoring', files=['js_return_endless.sql'])
@pytest.mark.config(
    TVM_ENABLED=True, TVM_RULES=[{'src': 'mock', 'dst': 'driver-scoring'}],
)
@pytest.mark.dispatch_settings(settings=get_limited_dispatch_settings())
@pytest.mark.parametrize(
    'oid, score',
    [pytest.param('order-011', 770), pytest.param('order-022', 100770)],
)
async def test_eda_cpo_cte_late_bonus_js_invalid(
        taxi_driver_scoring, oid, score,
):
    request = copy.deepcopy(REQUEST)
    request['request']['search']['order_id'] = oid

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json=request,
    )
    assert response.status_code == 200

    assert response.json()['candidates'] == [
        # score = eta - bonus
        {'id': 'dbid0_uuid0', 'score': score},
        {'id': 'dbid1_uuid1', 'score': score},
    ]
