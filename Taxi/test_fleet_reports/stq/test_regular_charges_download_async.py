import aiohttp.web

URL = '/api/v1/regular-charges/download'


async def test_success(
        web_app_client, mockserver, mock_parks, headers, stq_runner, load_json,
):
    service_stub = load_json('service_success.json')
    fleet_rent_aggregations_stub = load_json(
        'fleet_rent_aggregations_success.json',
    )
    fleet_rent_list_stub = load_json('fleet_rent_list_success.json')
    fleet_rent_balances_stub = load_json('fleet_rent_balances_success.json')
    parks_drivers_stub = load_json('parks_drivers_success.json')
    parks_cars_stub = load_json('parks_cars_success.json')

    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    @mockserver.json_handler('/fleet-rent-py3/v1/park/rents/aggregations')
    async def _v1_park_rents_aggregations(request):
        assert request.json == fleet_rent_aggregations_stub['request']
        return aiohttp.web.json_response(
            fleet_rent_aggregations_stub['response'],
        )

    @mockserver.json_handler('/fleet-rent-py3/v1/park/rents/list')
    async def _v1_park_rents_list(request):
        assert request.json == fleet_rent_list_stub['request']
        return aiohttp.web.json_response(fleet_rent_list_stub['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_drivers_stub['request']
        return aiohttp.web.json_response(parks_drivers_stub['response'])

    @mockserver.json_handler('/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == parks_cars_stub['request']
        return aiohttp.web.json_response(parks_cars_stub['response'])

    @mockserver.json_handler('/fleet-rent-py3/v1/park/rents/balances/retrieve')
    async def _v1_park_rents_balances_retrieve(request):
        assert request.json == fleet_rent_balances_stub['request']
        return aiohttp.web.json_response(fleet_rent_balances_stub['response'])

    await stq_runner.fleet_reports_regular_charges_download_async.call(
        task_id='1', args=(), kwargs=service_stub['request'],
    )
