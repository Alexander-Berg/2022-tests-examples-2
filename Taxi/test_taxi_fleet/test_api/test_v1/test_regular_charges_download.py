import aiohttp.web

URL = '/api/v1/regular-charges/download'


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        load_json,
        mock_fleet_rent_py3,
        mock_api7,
):
    service_stub = load_json('service_success.json')
    fleet_rent_aggregations_stub = load_json(
        'fleet_rent_aggregations_success.json',
    )
    fleet_rent_list_stub = load_json('fleet_rent_list_success.json')
    api7_drivers_stub = load_json('api7_drivers_success.json')
    api7_cars_stub = load_json('api7_cars_success.json')
    fleet_rent_balances_stub = load_json('fleet_rent_balances_success.json')

    @mock_fleet_rent_py3('/v1/park/rents/aggregations')
    async def _v1_park_rents_aggregations(request):
        assert request.json == fleet_rent_aggregations_stub['request']
        return aiohttp.web.json_response(
            fleet_rent_aggregations_stub['response'],
        )

    @mock_fleet_rent_py3('/v1/park/rents/list')
    async def _v1_park_rents_list(request):
        assert request.json == fleet_rent_list_stub['request']
        return aiohttp.web.json_response(fleet_rent_list_stub['response'])

    @mock_api7('/v1/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == api7_drivers_stub['request']
        return aiohttp.web.json_response(api7_drivers_stub['response'])

    @mock_api7('/v1/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == api7_cars_stub['request']
        return aiohttp.web.json_response(api7_cars_stub['response'])

    @mock_fleet_rent_py3('/v1/park/rents/balances/retrieve')
    async def _v1_park_rents_balances_retrieve(request):
        assert request.json == fleet_rent_balances_stub['request']
        return aiohttp.web.json_response(fleet_rent_balances_stub['response'])

    response = await web_app_client.post(
        URL, headers=headers, json=service_stub['request'],
    )

    assert response.status == 200
