import aiohttp.web
import pytest


@pytest.mark.config(OPTEUM_MINI_REPORT_DRIVER_HOURS_SETTINGS={'hours': 100})
async def test_success(
        web_app_client,
        mock_parks,
        headers,
        mock_driver_supply_hours,
        load_json,
):
    driver_supply_hours_stub = load_json('driver_supply_hours_success.json')
    service_stub = load_json('service_success.json')

    @mock_driver_supply_hours('/v1/parks/drivers-profiles/supply/retrieve')
    async def _v1_parks_drivers_profiles_supply_retrieve(request):
        assert request.json == driver_supply_hours_stub['request']
        return aiohttp.web.json_response(driver_supply_hours_stub['response'])

    response = await web_app_client.post(
        '/api/v1/cards/driver/income/widgets/work-hours',
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
        '/api/v1/cards/driver/income/widgets/work-hours',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 400
