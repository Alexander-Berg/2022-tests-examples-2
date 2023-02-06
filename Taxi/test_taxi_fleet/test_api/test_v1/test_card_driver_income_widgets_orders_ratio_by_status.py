import aiohttp.web
import pytest


@pytest.mark.config(OPTEUM_MINI_REPORT_DRIVER_HOURS_SETTINGS={'hours': 168})
async def test_success(
        web_app_client, mock_parks, headers, mock_driver_orders, load_json,
):
    api7_stub = load_json('api7_success.json')
    service_stub = load_json('service_success.json')

    @mock_driver_orders('/v1/parks/orders/list')
    async def _v1_parks_orders_list(request):
        assert request.json == api7_stub['request']
        return aiohttp.web.json_response(api7_stub['response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/income/widgets/orders-ratio-by-status',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200
    data = await response.json()
    assert data == service_stub['response']


@pytest.mark.config(OPTEUM_MINI_REPORT_DRIVER_HOURS_SETTINGS={'hours': 1})
async def test_date_range(web_app_client, mock_parks, headers, load_json):
    service_stub = load_json('service_success.json')

    response = await web_app_client.post(
        '/api/v1/cards/driver/income/widgets/orders-ratio-by-status',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 400
