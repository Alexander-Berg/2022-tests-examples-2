# pylint: disable=redefined-outer-name

import json

import pytest


class Context:
    def __init__(self):
        self.return500 = False

    def set_return500(self, _f):
        self.return500 = _f


@pytest.fixture
def ctx_overlord():
    return Context()


@pytest.fixture(name='overlord_service')
def mock_overlord(mockserver, ctx_overlord, load_json):
    class Overlord:
        @staticmethod
        @mockserver.json_handler(
            '/overlord-catalog/v1/catalog/nomenclature', prefix=True,
        )
        def handler(request):
            if ctx_overlord.return500:
                raise mockserver.NetworkError()
            return load_json('catalog_nomenclature_response.json')

    return Overlord()


# test that the proxy cache is functioning
async def test_proxy_cache(
        taxi_grocery_wms_gateway, load_json, ctx_overlord, overlord_service,
):
    resp_data = load_json('catalog_nomenclature_response.json')

    # successful request populates the cache...
    response = await taxi_grocery_wms_gateway.post(
        '/v1/catalog/nomenclature/87840',
    )
    assert response.status_code == 200
    assert response.json() == resp_data

    # ... and the cached value is returned
    ctx_overlord.set_return500(True)
    response = await taxi_grocery_wms_gateway.post(
        '/v1/catalog/nomenclature/87840',
    )
    assert response.status_code == 200
    assert response.json() == resp_data


async def test_basic(taxi_grocery_wms_gateway, mockserver, load_json):
    resp_data = load_json('catalog_nomenclature_response.json')

    @mockserver.json_handler(
        '/overlord-catalog/v1/catalog/nomenclature', prefix=True,
    )
    def _test(request):
        return resp_data

    response = await taxi_grocery_wms_gateway.post(
        '/v1/catalog/nomenclature/87840',
    )
    assert response.status_code == 200
    assert response.json() == resp_data


# check that 404 is proxied with original data
async def test_404(taxi_grocery_wms_gateway, mockserver):
    resp_data = {
        'code': 'DEPOT_NOT_FOUND',
        'message': 'This message must not be altered by the gateway',
    }

    @mockserver.json_handler(
        '/overlord-catalog/v1/catalog/nomenclature', prefix=True,
    )
    def _test(request):
        return mockserver.make_response(json.dumps(resp_data), 404)

    response = await taxi_grocery_wms_gateway.post(
        '/v1/catalog/nomenclature/87840',
    )
    assert response.status_code == 404
    assert response.json() == resp_data


# check that 500 is proxied
async def test_500(taxi_grocery_wms_gateway, mockserver):
    @mockserver.json_handler(
        '/overlord-catalog/v1/catalog/nomenclature', prefix=True,
    )
    def _test(request):
        raise mockserver.TimeoutError()

    response = await taxi_grocery_wms_gateway.post(
        '/v1/catalog/nomenclature/87840',
    )
    assert response.status_code == 500
