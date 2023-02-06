import aiohttp.web


async def test_success(
        web_app_client,
        mock_parks,
        headers,
        mock_api7,
        stq_runner,
        mock_fleet_transactions_api,
        mock_driver_profiles,
        mock_fleet_reports_storage,
        load_json,
):
    stub = load_json('success.json')

    @mock_fleet_reports_storage('/internal/v1/file/upload')
    async def _mock_frs(request):
        return None

    @mock_fleet_transactions_api(
        '/v1/parks/transactions/categories/list/by-platform',
    )
    async def _list_transaction_categories(request):
        assert request.json == stub['categories']['request']
        return aiohttp.web.json_response(stub['categories']['response'])

    @mock_driver_profiles('/v1/driver/profiles/retrieve')
    async def _list_drivers(request):
        assert request.json == stub['drivers']['driver_profiles_request']
        return aiohttp.web.json_response(
            stub['drivers']['driver_profiles_response'],
        )

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_orders_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    await stq_runner.fleet_reports_card_driver_transactions_order_download_async.call(  # noqa
        task_id='1', args=(), kwargs=stub['service']['request'],
    )
