from tests_lookup import lookup_params
from tests_lookup import mock_candidates

DRIVER_CAR_NUMBER = 'test_car_1'


# Check that ValidateExtendedRadius is working
async def test_in_extended_radius(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _acquire(request):
        candidates = mock_candidates.make_candidates()
        # extended radius should not be set for non-paid supply
        # so lookup should return 502 in acquire
        for candidate in candidates['candidates']:
            candidate['in_extended_radius'] = True
        return candidates

    order = lookup_params.create_params()
    await acquire_candidate(order, expect_fail=True)


# Check that ValidateCandidate does not fail if we don't put invalid values
async def test_validate_ok(acquire_candidate, mockserver):
    @mockserver.json_handler('/candidates/order-search')
    def _acquire(request):
        return mock_candidates.make_candidates()

    order = lookup_params.create_params()
    candidate = await acquire_candidate(order)
    assert candidate
