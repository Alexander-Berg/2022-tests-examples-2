from tests_lookup import lookup_params
from tests_lookup import mock_candidates


async def test_already_have_surge_price(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _acquire(request):
        return mock_candidates.make_candidates()

    order = lookup_params.create_params(surge_price=4.0)
    candidate = await acquire_candidate(order)
    assert candidate


async def test_multiple_tariffs_selected(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _acquire(request):
        return mock_candidates.make_candidates()

    order = lookup_params.create_params(
        surge_price=None, tariffs=['econom', 'business'],
    )
    candidate = await acquire_candidate(order)
    assert candidate


async def test_type_exacturgent(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _acquire(request):
        return mock_candidates.make_candidates()

    order = lookup_params.create_params(surge_price=None, type='exacturgent')
    candidate = await acquire_candidate(order)
    assert candidate


async def test_surge_price_required(acquire_candidate):
    order = lookup_params.create_params(
        surge_price=None, surge_price_required=1.7,
    )
    candidate = await acquire_candidate(order)
    assert not candidate
