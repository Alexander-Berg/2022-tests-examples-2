import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mock_parks,
        mock_driver_orders,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success.json')

    @mock_driver_orders('/v1/parks/orders/list')
    async def _list_orders(request):
        orders = stub['orders']
        assert request.json == orders['driver_orders_request']
        return aiohttp.web.json_response(orders['driver_orders_response'])

    @mock_fleet_transactions_api('/v1/parks/orders/transactions/list')
    async def _list_order_transactions(request):
        assert request.json == stub['transactions']['fta_request']
        return aiohttp.web.json_response(stub['transactions']['fta_response'])

    @mock_fleet_transactions_api(
        '/v1/parks/transactions/categories/list/by-user',
    )
    async def _list_transaction_categories(request):
        assert request.json == stub['transaction-categories']['request']
        return aiohttp.web.json_response(
            stub['transaction-categories']['response'],
        )

    response = await web_app_client.post(
        '/reports-api/v1/orders/download',
        headers=headers,
        json=stub['service']['request'],
    )

    assert response.status == 200
