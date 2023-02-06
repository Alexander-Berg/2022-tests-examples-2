# flake8: noqa
# pylint: disable=import-error,wildcard-import
import pytest
from market_hide_offers_dyn2yt_plugins.generated_tests import *

# Feel free to provide your custom implementation to override generated tests.


@pytest.mark.servicetest
async def test_ping(taxi_market_hide_offers_dyn2yt, mockserver):
    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_mds(request):
        if request.method == 'GET':
            dynamic_file = 'ping-test'
            return mockserver.make_response(dynamic_file, 200)
        return mockserver.make_response('Wrong method', 500)

    response = await taxi_market_hide_offers_dyn2yt.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


async def test_incremental_cache_update(
        taxi_market_hide_offers_dyn2yt, mockserver,
):
    """The service needs a handle to put result dynamic, so we override the test"""

    @mockserver.handler(
        '/mds-s3/current-unified-hide-offers-rule.mmap', prefix=True,
    )
    def _mock_mds_update_mmap(request):
        if request.method == 'PUT':
            mockserver.make_response('Ok', 200)
        return mockserver.make_response('Wrong method', 500)

    await taxi_market_hide_offers_dyn2yt.update_server_state()
    await taxi_market_hide_offers_dyn2yt.invalidate_caches(clean_update=False)
