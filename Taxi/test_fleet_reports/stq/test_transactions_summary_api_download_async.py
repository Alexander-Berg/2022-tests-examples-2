import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        mockserver,
        stq_runner,
        mock_fleet_transactions_api,
        mock_driver_profiles,
        mock_fleet_reports_storage,
        load_json,
):
    stub = load_json('success.json')
    parks_drivers_stub = load_json('parks_drivers_success.json')
    work_rules_stub = load_json('work_rules.json')

    @mock_fleet_reports_storage('/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    @mockserver.json_handler('/parks/driver-profiles/list')
    async def _v1_parks_driver_profiles_list(request):
        branch = 'limit_1' if request.json['limit'] == 1 else 'limit_n'
        assert request.json == parks_drivers_stub[branch]['request']
        return aiohttp.web.json_response(
            parks_drivers_stub[branch]['response'],
        )

    @mock_fleet_transactions_api('/v1/parks/driver-profiles/balances/list')
    async def _balances_list(request):
        assert request.json == stub['balances']['request']
        return aiohttp.web.json_response(stub['balances']['response'])

    @mockserver.json_handler('/driver-work-rules/v1/work-rules/list')
    async def _v1_parks_driver_work_rules(request):
        assert request.json == work_rules_stub['request']
        return aiohttp.web.json_response(work_rules_stub['response'])

    await stq_runner.fleet_reports_transactions_summary_api_download_async.call(  # noqa
        task_id='1', args=(), kwargs=stub['service']['request'],
    )
