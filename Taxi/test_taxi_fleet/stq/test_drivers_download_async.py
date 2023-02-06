# flake8: noqa
from generated.clients import contractor_instant_payouts
import aiohttp.web
import pytest

RESPONSE409 = {'body': '', 'code': 'NOT_ALLOWED_STATUS', 'message': '409'}


async def test_success(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    service_stub = load_json('service_success.json')
    parks_drivers_stub = load_json('parks_drivers_success.json')
    driver_work_rules_stub = load_json('driver_work_rules_success.json')
    contractor_rules_list_stub = load_json(
        'contractor_instant_payouts_success.json',
    )

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_drivers_stub['request']
        return aiohttp.web.json_response(parks_drivers_stub['response'])

    @mockserver.json_handler('driver-work-rules/v1/work-rules/list')
    async def _v1_parks_driver_work_rules(request):
        assert request.json == driver_work_rules_stub['request']
        return aiohttp.web.json_response(driver_work_rules_stub['response'])

    @mockserver.json_handler(
        'contractor-instant-payouts/v1/contractors/rules/list',
    )
    async def _v1_contractors_rules_list(request):
        assert (
            request.query['park_id'] == contractor_rules_list_stub['park_id']
        )
        assert request.json == contractor_rules_list_stub['request']
        return aiohttp.web.json_response(
            contractor_rules_list_stub['response'],
        )

    await stq_runner.taxi_fleet_drivers_download_async.call(
        task_id='1', args=(), kwargs=service_stub['request'],
    )


async def test_success409(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return mockserver.make_response(status=409, json=RESPONSE409)

    service_stub = load_json('service_success.json')
    parks_drivers_stub = load_json('parks_drivers_success.json')
    driver_work_rules_stub = load_json('driver_work_rules_success.json')
    contractor_rules_list_stub = load_json(
        'contractor_instant_payouts_success.json',
    )

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        assert request.json == parks_drivers_stub['request']
        return aiohttp.web.json_response(parks_drivers_stub['response'])

    @mockserver.json_handler('driver-work-rules/v1/work-rules/list')
    async def _v1_parks_driver_work_rules(request):
        assert request.json == driver_work_rules_stub['request']
        return aiohttp.web.json_response(driver_work_rules_stub['response'])

    @mockserver.json_handler(
        'contractor-instant-payouts/v1/contractors/rules/list',
    )
    async def _v1_contractors_rules_list(request):
        assert (
            request.query['park_id'] == contractor_rules_list_stub['park_id']
        )
        assert request.json == contractor_rules_list_stub['request']
        return aiohttp.web.json_response(
            contractor_rules_list_stub['response'],
        )

    await stq_runner.taxi_fleet_drivers_download_async.call(
        task_id='1', args=(), kwargs=service_stub['request'],
    )
