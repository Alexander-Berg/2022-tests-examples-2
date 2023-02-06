# flake8: noqa
from generated.clients import fleet_reports_storage
import aiohttp.web
import pytest

RESPONSE409 = {'body': '', 'code': 'NOT_ALLOWED_STATUS', 'message': '409'}


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    stub = load_json('service_success.json')
    cars_stub = load_json('cars_success.json')
    driver_profiles_stub = load_json('driver_profiles_success.json')

    @mockserver.json_handler('/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == cars_stub['request']
        return aiohttp.web.json_response(cars_stub['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == driver_profiles_stub['request']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    await stq_runner.fleet_reports_summary_cars_download_async.call(
        task_id='1', args=(), kwargs=stub['request'],
    )

    assert _mock_frs.times_called == 1
    assert _v1_parks_cars_list.times_called == 1
    assert _v1_parks_driver_profiles_list.times_called == 1


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success409(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return mockserver.make_response(status=409, json=RESPONSE409)

    stub = load_json('service_success.json')
    cars_stub = load_json('cars_success.json')
    driver_profiles_stub = load_json('driver_profiles_success.json')

    @mockserver.json_handler('/parks/cars/list')
    async def _v1_parks_cars_list(request):
        assert request.json == cars_stub['request']
        return aiohttp.web.json_response(cars_stub['response'])

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == driver_profiles_stub['request']
        return aiohttp.web.json_response(driver_profiles_stub['response'])

    await stq_runner.fleet_reports_summary_cars_download_async.call(
        task_id='1', args=(), kwargs=stub['request'],
    )

    assert _mock_frs.times_called == 1
    assert _v1_parks_cars_list.times_called == 1
    assert _v1_parks_driver_profiles_list.times_called == 1
