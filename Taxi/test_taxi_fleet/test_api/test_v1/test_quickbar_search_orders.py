import aiohttp.web
import pytest


@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_success(web_app_client, headers, mock_driver_orders, load_json):

    drivers_orders_stub = load_json('drivers_orders_success.json')
    service_stub = load_json('service_success.json')

    @mock_driver_orders('/v1/parks/orders/list')
    async def _v1_parks_orders_list(request):
        assert request.json == drivers_orders_stub['request']
        return aiohttp.web.json_response(drivers_orders_stub['response'])

    response = await web_app_client.post(
        '/api/v1/quickbar/search/orders',
        headers=headers,
        json=service_stub['request'],
    )
    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
