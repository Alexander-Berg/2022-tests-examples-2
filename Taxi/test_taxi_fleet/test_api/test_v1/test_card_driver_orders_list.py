import aiohttp.web


async def test_success(
        web_app_client,
        headers,
        mock_driver_orders,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success.json')

    @mock_driver_orders('/v1/parks/orders/list')
    async def _list_orders(request):
        assert request.json == stub['orders']['api7_request']
        return aiohttp.web.json_response(stub['orders']['api7_response'])

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
        '/api/v1/cards/driver/orders/list',
        headers=headers,
        json={
            'query': {
                'driver_id': '24deba79c4efecc229acdb1e5017296d',
                'date': {
                    'type': 'ended_at',
                    'from': '2019-01-01T00:00:00+03:00',
                    'to': '2019-02-01T00:00:00+03:00',
                },
            },
            'limit': 1,
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']


async def test_success_with_types(
        web_app_client,
        headers,
        mock_driver_orders,
        mock_fleet_transactions_api,
        load_json,
):
    stub = load_json('success_with_types.json')

    @mock_driver_orders('/v1/parks/orders/list')
    async def _list_orders(request):
        assert request.json == stub['orders']['api7_request']
        return aiohttp.web.json_response(stub['orders']['api7_response'])

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
        '/api/v1/cards/driver/orders/list',
        headers=headers,
        json={
            'query': {
                'driver_id': '24deba79c4efecc229acdb1e5017296d',
                'date': {
                    'type': 'ended_at',
                    'from': '2019-01-01T00:00:00+03:00',
                    'to': '2019-02-01T00:00:00+03:00',
                },
                'order': {'types': ['62fa2e61ae9ae111bac10080484ffc05']},
            },
            'limit': 1,
        },
    )

    assert response.status == 200

    data = await response.json()
    assert data == stub['service_response']
