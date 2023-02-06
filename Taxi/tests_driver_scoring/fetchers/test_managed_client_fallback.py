import pytest

import tests_driver_scoring.tvm_tickets as tvm_tickets


@pytest.mark.experiments3(filename='driver_bonuses.json')
@pytest.mark.experiments3(filename='default_postprocessors.json')
async def test_driver_scoring_js_bonuses_user_tags(
        taxi_driver_scoring, mockserver,
):
    @mockserver.json_handler('/statistics/v1/service/health')
    async def _mock_v1_service_health(request):
        if request.args['service'] == 'userver@driver-scoring':
            return {'fallbacks': ['global-fallback']}
        return {'fallbacks': []}

    await taxi_driver_scoring.tests_control(invalidate_caches=True)

    @mockserver.json_handler(
        '/reposition-matcher/v1/service/match_orders_drivers',
    )
    def _reposition_matcher_handler(request):
        assert False, 'Must not be called on fallback'

    response = await taxi_driver_scoring.post(
        'v2/score-candidates',
        headers={'X-Ya-Service-Ticket': tvm_tickets.MOCK_SERVICE_TICKET},
        json={
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
        },
    )
    assert response.status_code == 200
    assert _reposition_matcher_handler.times_called == 0
