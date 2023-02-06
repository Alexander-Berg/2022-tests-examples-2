# flake8: noqa
import aiohttp.web
import pytest

RESPONSE409 = {'body': '', 'code': 'NOT_ALLOWED_STATUS', 'message': '409'}


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    stub = load_json('service_success.json')

    await stq_runner.fleet_reports_summary_parks_download_async.call(
        task_id='1', args=(), kwargs=stub['request'],
    )

    assert _mock_frs.times_called == 1


@pytest.mark.pgsql('fleet_reports', files=('success.sql',))
async def test_success409(stq_runner, mockserver, load_json):
    @mockserver.json_handler('/fleet-reports-storage/internal/v1/file/upload')
    async def _mock_frs(request):
        return mockserver.make_response(status=409, json=RESPONSE409)

    stub = load_json('service_success.json')

    await stq_runner.fleet_reports_summary_parks_download_async.call(
        task_id='1', args=(), kwargs=stub['request'],
    )

    assert _mock_frs.times_called == 1
