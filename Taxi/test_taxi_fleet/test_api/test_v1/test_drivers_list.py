import aiohttp.web
import pytest


@pytest.mark.config(TAXI_FLEET_DEVICE_MODEL_MAPPING={'iPhone9,1': 'iPhone 7'})
async def test_success(web_app_client, headers, mockserver, load_json):
    stub = load_json('success.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['parks_request']
        return aiohttp.web.json_response(stub['parks_response'])

    response = await web_app_client.post(
        '/api/v1/drivers/list', headers=headers, json={'limit': 2},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_support(
        web_app_client, headers_support, mockserver, load_json,
):
    stub = load_json('success-support.json')

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _list_drivers(request):
        assert request.json == stub['parks_request']
        return aiohttp.web.json_response(stub['parks_response'])

    response = await web_app_client.post(
        '/api/v1/drivers/list', headers=headers_support, json={'limit': 2},
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
