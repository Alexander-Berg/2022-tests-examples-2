import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates


@pytest.mark.config(
    LOOKUP_PAID_SUPPLY_SETTINGS={
        '__default__': {
            '__default__': {
                'min_distance': 400,
                'min_time': 400,
                'max_price': 100,
            },
        },
        'moscow': {
            '__default__': {
                'min_distance': 400,
                'min_time': 400,
                'max_price': 100,
            },
            'econom': {'min_distance': 300, 'min_time': 300, 'max_price': 300},
            'business': {
                'min_distance': 100,
                'min_time': 100,
                'max_price': 50,
            },
        },
    },
)
async def test_direct_request(acquire_candidate, mockserver, load_json):
    @mockserver.json_handler('/candidates/order-search')
    def _order_search(request):
        result = mock_candidates.make_candidates()
        result_driver = result['candidates'][0]
        result_driver['route_info']['distance'] = 300
        return result

    # order = lookup_params.create_params()
    order = lookup_params.create_params(tariffs=['econom', 'business'])
    order['order']['fixed_price']['paid_supply_price'] = 90
    candidate = await acquire_candidate(order)
    assert candidate['paid_supply']
