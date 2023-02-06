import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        load_json,
        mockserver,
        mock_fleet_rent_py3,
        mock_api7,
):
    service_stub = load_json('service_success.json')
    fleet_rent_stub = load_json('fleet_rent_success.json')
    parks_drivers_stub = load_json('parks_drivers_success.json')
    api7_cars_stub = load_json('api7_cars_success.json')

    @mock_fleet_rent_py3('/v1/park/rents/')
    async def _v1_park_rents_get(request):
        assert request.query == fleet_rent_stub['request']
        return aiohttp.web.json_response(fleet_rent_stub['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_drivers_stub['request']
        return aiohttp.web.json_response(parks_drivers_stub['response'])

    @mock_api7('/v1/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == api7_cars_stub['request']
        return aiohttp.web.json_response(api7_cars_stub['response'])

    response = await web_app_client.post(
        '/api/v1/regular-charges/item',
        headers=headers,
        json=service_stub['request'],
    )

    assert response.status == 200

    data = await response.json()
    assert data == service_stub['response']
