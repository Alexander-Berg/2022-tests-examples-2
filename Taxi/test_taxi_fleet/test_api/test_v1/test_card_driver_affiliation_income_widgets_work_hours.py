import aiohttp.web
import pytest

URL = '/api/v1/cards/driver/affiliation/income/widgets/work-hours'


@pytest.mark.config(OPTEUM_MINI_REPORT_DRIVER_HOURS_SETTINGS={'hours': 100})
async def test_success(
        web_app_client,
        mock_parks,
        headers,
        mockserver,
        mock_fleet_rent_py3,
        mock_fleet_parks,
        mock_driver_supply_hours,
        load_json,
):
    parks_drivers_stub = load_json('parks_drivers_success.json')
    fleet_parks_stub = load_json('fleet_parks_success.json')
    fleet_rent_stub = load_json('fleet_rent_success.json')
    driver_supply_hours_stub = load_json('driver_supply_hours_success.json')
    service_stub = load_json('service_success.json')

    @mock_fleet_rent_py3('/v1/park/rents/aggregations')
    async def _v1_park_rents_aggregations(request):
        assert request.json == fleet_rent_stub['request']
        return aiohttp.web.json_response(fleet_rent_stub['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_drivers_stub['request']
        return aiohttp.web.json_response(parks_drivers_stub['response'])

    @mock_fleet_parks('/v1/parks/list')
    async def _v1_parks_list(request):
        if request.json['query']['park']['ids'] == [
                '7ad36bc7560449998acbe2c57a75c293',
        ]:
            return mock_parks
        assert request.json == fleet_parks_stub['request']
        return aiohttp.web.json_response(fleet_parks_stub['response'])

    @mock_driver_supply_hours('/v1/parks/drivers-profiles/supply/retrieve')
    async def _v1_parks_drivers_profiles_supply_retrieve(request):
        assert request.json == driver_supply_hours_stub['request']
        return aiohttp.web.json_response(driver_supply_hours_stub['response'])

    response = await web_app_client.post(
        URL, headers=headers, json=service_stub['request'],
    )

    assert response.status == 200
    data = await response.json()
    assert data == service_stub['response']
