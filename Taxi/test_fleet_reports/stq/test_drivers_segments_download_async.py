import aiohttp.web
import pytest


@pytest.mark.pgsql('fleet_reports', files=('dump.sql',))
async def test_success(
        web_app_client,
        headers,
        stq_runner,
        mockserver,
        mock_parks,
        mock_fleet_reports_storage,
        load_json,
):
    service_stub = load_json('service.json')
    drivers_stub = load_json('drivers.json')
    work_rules_stub = load_json('work_rules.json')

    @mock_fleet_reports_storage('/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == drivers_stub['request']
        return aiohttp.web.json_response(drivers_stub['response'])

    @mockserver.json_handler('/driver-work-rules/v1/work-rules/list')
    async def _v1_parks_driver_work_rules(request):
        assert request.json == work_rules_stub['request']
        return aiohttp.web.json_response(work_rules_stub['response'])

    await stq_runner.fleet_reports_drivers_segments_download_async.call(  # noqa
        task_id='1', args=(), kwargs=service_stub['request'],
    )
