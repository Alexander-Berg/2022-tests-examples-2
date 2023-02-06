import pytest

from testsuite.utils import http


@pytest.mark.servicetest
async def test_cars_catalog_fallback(taxi_candidates, mockserver, testpoint):
    # first update emulation
    @testpoint('invalidate_brand_models_cache')
    def invalidate_brand_models(data):
        return {'invalidate': True}

    @testpoint('invalidate_price_ages_cache')
    def invalidate_price_ages(data):
        return {'invalidate': True}

    # service doesn't work
    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_prices')
    def mock_cars_catalog_prices(request):
        return mockserver.make_response('{"code": 500}', 500)

    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_brand_models')
    def mock_cars_catalog_brand_models(request):
        return mockserver.make_response('{"code": 500}', 500)

    response = await taxi_candidates.get('ping')

    assert invalidate_brand_models.has_calls
    assert invalidate_price_ages.has_calls

    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''

    assert mock_cars_catalog_prices.has_calls
    assert mock_cars_catalog_brand_models.has_calls

    # cars-catalog still returns 500
    # caches keep current state
    @testpoint('invalidate_brand_models_cache')
    def doesnt_invalidate_brand_models(data):
        return {'invalidate': False}

    @testpoint('invalidate_price_ages_cache')
    def doesnt_invalidate_price_ages(data):
        return {'invalidate': False}

    # Update throws exception in test/control (catch in periodic task)
    # Restore doesn't work
    try:
        await taxi_candidates.invalidate_caches()
    except http.HttpResponseError as error:
        assert error.status == 500

    assert (
        doesnt_invalidate_brand_models.has_calls
        or doesnt_invalidate_price_ages.has_calls
    )
