import pytest

from tests_lookup import lookup_params
from tests_lookup import mock_candidates


@pytest.mark.config()
async def test_response_200(acquire_candidate, mockserver):
    @mockserver.json_handler('/combo-matcher/performer-for-order')
    def combo_matcher(request):
        response = {
            'candidate': mock_candidates.make_candidates()['candidates'][0],
        }
        return response

    @mockserver.json_handler('/driver-freeze/freeze')
    def freeze(request):
        return {'freezed': True}

    @mockserver.json_handler('/driver-freeze/defreeze')
    def _defreeze(request):
        assert False, 'should not be called'

    order = lookup_params.create_params()
    order['order']['buffer_combo'] = {'enabled': True}

    candidate = await acquire_candidate(order)
    assert candidate

    await combo_matcher.wait_call(timeout=1)
    await freeze.wait_call(timeout=1)


async def test_not_found(acquire_candidate, mockserver):
    @mockserver.json_handler('/combo-matcher/performer-for-order')
    def combo_matcher(request):
        return mockserver.make_response(status=200, json={})

    order = lookup_params.create_params()
    order['order']['buffer_combo'] = {'enabled': True}

    candidate = await acquire_candidate(order)
    assert not candidate

    await combo_matcher.wait_call(timeout=1)
