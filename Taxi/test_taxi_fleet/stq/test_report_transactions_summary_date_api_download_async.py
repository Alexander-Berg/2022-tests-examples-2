import aiohttp.web

RESPONSE409 = {'body': '', 'code': 'NOT_ALLOWED_STATUS', 'message': '409'}


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        stq_runner,
        mock_fleet_transactions_api,
        mock_fleet_reports_storage,
        load_json,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _list_drivers_transactions(request):
        assert request.json == stub['balances']['request']
        return aiohttp.web.json_response(stub['balances']['response'])

    await stq_runner.taxi_fleet_report_transactions_summary_date_api_download_async.call(  # noqa
        task_id='1', args=(), kwargs=stub['service']['request'],
    )


async def test_success409(
        web_app_client,
        mock_parks,
        headers,
        stq_runner,
        mockserver,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success.json')

    @mockserver.json_handler(
        '/fleet-reports-storage/internal/v1/file/upload',
    )  # noqa
    async def _mock_frs(request):
        return mockserver.make_response(status=409, json=RESPONSE409)

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _list_drivers_transactions(request):
        assert request.json == stub['balances']['request']
        return aiohttp.web.json_response(stub['balances']['response'])

    await stq_runner.taxi_fleet_report_transactions_summary_date_api_download_async.call(  # noqa
        task_id='1', args=(), kwargs=stub['service']['request'],
    )
