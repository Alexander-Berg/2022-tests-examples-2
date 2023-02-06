import aiohttp.web


async def test_success(web_app_client, stq_runner, load_json, mockserver):
    service_stub = load_json('service_success.json')
    parks_cars_stub = load_json('park_drivers_success.json')

    @mockserver.json_handler('/parks/cars/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_cars_stub['request']
        return aiohttp.web.json_response(parks_cars_stub['response'])

    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    await stq_runner.fleet_reports_cars_download_async.call(
        task_id='1', args=(), kwargs=service_stub['request'],
    )
